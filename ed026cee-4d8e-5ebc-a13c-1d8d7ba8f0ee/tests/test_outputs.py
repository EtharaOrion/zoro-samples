"""Deterministic pytest layer for task ed026cee-4d8e-5ebc-a13c-1d8d7ba8f0ee."""

import pytest
from statistics import mean
from evaluation.conftest import *

VALID_TOOLS = (
    "place_order", "modify_sku_price", "end_today",
    "view_current_orders", "view_sku_sales_history",
    "view_current_date_supplier_prices", "view_supplier_price_history",
    "view_inventory", "view_sku_reviews", "view_sku_avg_ratings",
    "view_return_rates", "view_returns", "view_funds_and_date",
    "view_sku_prices", "view_today_news", "view_news_detail",
    "view_news_history", "add_note", "view_notes",
)


def _is_effective_order(order):
    """An order is effective if it has a valid order_id, no error, and units > 0."""
    return order.order_id is not None and order.error is None and order.units > 0


def _order_capital(order):
    """Return the capital deployed by an order (0 if ineffective)."""
    if not _is_effective_order(order):
        return 0.0
    return order.cost


def _effective_price_changes(snapshot):
    """Return the list of effective price changes (|new - old| > 1e-9 or old is None)."""
    effective = []
    for pc in snapshot.price_changes:
        if pc.old_price is None or abs(pc.new_price - pc.old_price) > 1e-9:
            effective.append(pc)
    return effective


def _capital_by_day(snapshot):
    """Return dict[day, capital_deployed] for each day."""
    capital = {}
    for order in snapshot.orders_placed:
        if _is_effective_order(order):
            capital[order.day] = capital.get(order.day, 0.0) + order.cost
    return capital


def _deployed_total(snapshot):
    """Return total capital deployed across all effective orders."""
    return sum(_order_capital(o) for o in snapshot.orders_placed)


# ============================================================================
# INTEGRITY GATES (kind="outcome", weight=0.0, category="integrity")
# ============================================================================

@pytest.mark.check(id="integrity_config_matches_frozen_task", weight=0.0, knockout=False, category="integrity", kind="outcome")
def test_integrity_config_matches_frozen_task(snapshot, thresholds):
    """Verify the run's config matches the frozen task config."""
    frozen = thresholds["config"]
    
    # Check scalar fields
    if not hasattr(snapshot.config, "initial_funds"):
        raise RuntimeError("Loader did not surface config.initial_funds")
    if not hasattr(snapshot.config, "everyday_rent"):
        raise RuntimeError("Loader did not surface config.everyday_rent")
    if not hasattr(snapshot.config, "inventory_capacity"):
        raise RuntimeError("Loader did not surface config.inventory_capacity")
    if not hasattr(snapshot.config, "global_random_seed"):
        raise RuntimeError("Loader did not surface config.global_random_seed")
    if not hasattr(snapshot.config, "enable_review"):
        raise RuntimeError("Loader did not surface config.enable_review")
    if not hasattr(snapshot.config, "enable_new"):
        raise RuntimeError("Loader did not surface config.enable_new")
    if not hasattr(snapshot.config, "selected_categories"):
        raise RuntimeError("Loader did not surface config.selected_categories")
    
    assert snapshot.config.initial_funds == frozen["initial_funds"], "initial_funds mismatch"
    assert snapshot.config.everyday_rent == frozen["everyday_rent"], "everyday_rent mismatch"
    assert snapshot.config.inventory_capacity == frozen["inventory_capacity"], "inventory_capacity mismatch"
    assert snapshot.config.global_random_seed == frozen["global_random_seed"], "global_random_seed mismatch"
    assert snapshot.config.enable_review == frozen["enable_review"], "enable_review mismatch"
    assert snapshot.config.enable_new == frozen["enable_new"], "enable_new mismatch"
    
    # Check categories list (normalize representation)
    frozen_cats = frozen["selected_categories_list"]
    observed_cats = snapshot.config.selected_categories
    
    def normalize(s):
        return s.replace("_", " ").strip().lower()
    
    frozen_normalized = sorted(normalize(c) for c in frozen_cats)
    observed_normalized = sorted(normalize(c) for c in observed_cats)
    
    assert observed_normalized == frozen_normalized, f"selected_categories mismatch: {observed_cats} vs {frozen_cats}"


@pytest.mark.check(id="integrity_readable_complete", weight=0.0, knockout=False, category="integrity", kind="outcome")
def test_integrity_readable_complete(snapshot, thresholds):
    """Verify the trajectory parsed and the terminal net worth is a finite real number."""
    if snapshot.final_net_worth is None:
        raise RuntimeError("Trajectory did not yield a terminal net worth")
    if not isinstance(snapshot.final_net_worth, (int, float)):
        raise RuntimeError(f"Terminal net worth is not a number: {type(snapshot.final_net_worth)}")
    if not (-1e15 < snapshot.final_net_worth < 1e15):
        raise RuntimeError(f"Terminal net worth is not finite: {snapshot.final_net_worth}")


# ============================================================================
# MONEY OUTCOME (kind="outcome", weight=0.0, category="money")
# ============================================================================

@pytest.mark.check(id="money_net_worth_outcome", weight=0.0, knockout=False, category="money", kind="outcome")
def test_money_net_worth_outcome(snapshot, thresholds, record_property):
    """Compute and record the continuous money outcome O."""
    funds = thresholds["config"]["initial_funds"]
    oracle_nw = thresholds["oracle_nw"]["value"]
    days_requested = thresholds["config"]["days_requested"]
    rent = thresholds["config"]["everyday_rent"]
    
    # Horizon-pinned net worth (project rent for unfinished days)
    days_short = max(0, days_requested - snapshot.days_completed)
    horizon_pinned_nw = snapshot.final_net_worth - rent * days_short
    
    # Reference gain
    ref = oracle_nw - funds
    
    # Guard against near-infeasible task
    if ref <= 0:
        O = 0.0
    else:
        raw = (horizon_pinned_nw - funds) / ref
        O = max(0.0, min(1.0, raw))
    
    band = "MADE-MONEY" if horizon_pinned_nw > funds else "LOST-MONEY"
    
    record_property("pinned_net_worth", snapshot.final_net_worth)
    record_property("horizon_pinned_net_worth", horizon_pinned_nw)
    record_property("money_outcome_O", O)
    record_property("money_band", band)
    
    # Assert only that the pinned value is a real number
    assert isinstance(snapshot.final_net_worth, (int, float))
    assert -1e15 < snapshot.final_net_worth < 1e15


# ============================================================================
# PROCESS CHECKS (kind="process", weighted)
# ============================================================================

@pytest.mark.check(id="valid_tools_used", weight=1.0, knockout=False, category="meta", kind="process")
def test_valid_tools_used(snapshot, thresholds):
    """All tool names used are in the valid registry."""
    observed = set()
    for day_calls in snapshot.tool_calls_by_day.values():
        for call in day_calls:
            observed.add(call.tool)
    
    invalid = observed - set(VALID_TOOLS)
    assert len(invalid) == 0, f"Invalid tools used: {invalid}"


@pytest.mark.check(id="supplier_board_before_order", weight=1.5, knockout=False, category="supplier", kind="process")
def test_supplier_board_before_order(snapshot, thresholds):
    """Of all place_order calls, the fraction whose SKUs were covered by an earlier same-day supplier board read."""
    T_supplier = thresholds["process_thresholds"]["T_supplier"]["value"]
    
    # Collect all place_order calls
    order_calls = []
    for day, calls in snapshot.tool_calls_by_day.items():
        for call in calls:
            if call.tool == "place_order":
                order_calls.append((day, call))
    
    if len(order_calls) == 0:
        # No orders placed → definite FAIL (non-operation)
        assert False, "No orders placed (non-operation)"
    
    # For each order, check if there was a same-day supplier board read before it
    covered = 0
    for day, order_call in order_calls:
        # Get all calls on that day
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        
        # Find the index of this order call
        order_idx = None
        for i, c in enumerate(day_calls):
            if c is order_call:
                order_idx = i
                break
        
        if order_idx is None:
            continue
        
        # Check if there's a view_current_date_supplier_prices before this order
        found = False
        for i in range(order_idx):
            if day_calls[i].tool == "view_current_date_supplier_prices":
                found = True
                break
        
        if found:
            covered += 1
    
    fraction = covered / len(order_calls)
    assert fraction >= T_supplier, f"Supplier board coverage {fraction:.2%} < {T_supplier:.2%}"


@pytest.mark.check(id="view_orders_before_place", weight=1.0, knockout=False, category="reorder", kind="process")
def test_view_orders_before_place(snapshot, thresholds):
    """Of order-days, the fraction with an earlier same-day view_current_orders."""
    T_vieworders = thresholds["process_thresholds"]["T_vieworders"]["value"]
    
    # Collect days with place_order calls
    order_days = set()
    for day, calls in snapshot.tool_calls_by_day.items():
        for call in calls:
            if call.tool == "place_order":
                order_days.add(day)
                break
    
    if len(order_days) == 0:
        # No order days → definite FAIL (non-operation)
        assert False, "No order days (non-operation)"
    
    # For each order day, check if there was a view_current_orders before any place_order
    covered = 0
    for day in order_days:
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        
        # Find first place_order
        first_order_idx = None
        for i, call in enumerate(day_calls):
            if call.tool == "place_order":
                first_order_idx = i
                break
        
        if first_order_idx is None:
            continue
        
        # Check if there's a view_current_orders before it
        found = False
        for i in range(first_order_idx):
            if day_calls[i].tool == "view_current_orders":
                found = True
                break
        
        if found:
            covered += 1
    
    fraction = covered / len(order_days)
    assert fraction >= T_vieworders, f"View orders coverage {fraction:.2%} < {T_vieworders:.2%}"


@pytest.mark.check(id="day1_order_placed", weight=1.5, knockout=False, category="setup", kind="process")
def test_day1_order_placed(snapshot, thresholds):
    """A material opening order within the first 3 days."""
    grace = 3
    
    # Find effective orders in first grace days
    early_orders = [o for o in snapshot.orders_placed if o.day <= grace and _is_effective_order(o)]
    
    if len(early_orders) == 0:
        assert False, f"No effective order in first {grace} days"
    
    # Check that at least one is material (not a 1-unit token)
    material = any(o.units > 1 for o in early_orders)
    assert material, f"No material order in first {grace} days (only token orders)"


@pytest.mark.check(id="day1_supplier_read_before_order", weight=0.5, knockout=False, category="setup", kind="process")
def test_day1_supplier_read_before_order(snapshot, thresholds):
    """Implication: IF a day-1 order exists, a day-1 supplier board read precedes it."""
    day1_calls = snapshot.tool_calls_by_day.get(1, [])
    
    # Find first place_order on day 1
    first_order_idx = None
    for i, call in enumerate(day1_calls):
        if call.tool == "place_order":
            first_order_idx = i
            break
    
    if first_order_idx is None:
        # No day-1 order → vacuous PASS
        return
    
    # Check if there's a supplier board read before it
    found = False
    for i in range(first_order_idx):
        if day1_calls[i].tool == "view_current_date_supplier_prices":
            found = True
            break
    
    assert found, "Day-1 order placed without prior supplier board read"


@pytest.mark.check(id="priced_before_first_sale", weight=1.0, knockout=False, category="setup", kind="process")
def test_priced_before_first_sale(snapshot, thresholds):
    """An effective price change on or before the first day with nonzero sales."""
    # Find first day with sales
    first_sale_day = None
    for day in sorted(snapshot.sales_units_by_day.keys()):
        if snapshot.sales_units_by_day[day] > 0:
            first_sale_day = day
            break
    
    if first_sale_day is None:
        # No sales at all → definite FAIL (non-operation)
        assert False, "No sales (non-operation)"
    
    # Check for effective price change on or before first sale day
    effective_pcs = _effective_price_changes(snapshot)
    early_pcs = [pc for pc in effective_pcs if pc.day <= first_sale_day]
    
    assert len(early_pcs) > 0, f"No effective price change before first sale (day {first_sale_day})"


@pytest.mark.check(id="reorder_after_stockout", weight=1.0, knockout=False, category="reorder", kind="process")
def test_reorder_after_stockout(snapshot, thresholds):
    """Of stockout events, the fraction refilled by an effective order within 7 days."""
    T_reorder = thresholds["process_thresholds"]["T_reorder"]["value"]
    reorder_window = 7
    
    if len(snapshot.stockout_events) == 0:
        # No stockouts → vacuous PASS
        return
    
    covered = 0
    for stockout in snapshot.stockout_events:
        # Verify sku is a bare numeric id
        if not isinstance(stockout.sku, str) or not stockout.sku.isdigit():
            raise RuntimeError(f"Stockout sku is not a bare numeric id: {stockout.sku}")
        
        # Find effective orders for this SKU within 7 days after stockout
        sku_orders = snapshot.orders_by_sku(stockout.sku)
        refill_orders = [
            o for o in sku_orders
            if _is_effective_order(o) and stockout.day < o.day <= stockout.day + reorder_window
        ]
        
        if len(refill_orders) > 0:
            covered += 1
    
    fraction = covered / len(snapshot.stockout_events)
    assert fraction >= T_reorder, f"Reorder coverage {fraction:.2%} < {T_reorder:.2%}"


@pytest.mark.check(id="no_prolonged_order_drought", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_prolonged_order_drought(snapshot, thresholds):
    """No window of drought_len days (before the last 15-day taper) with low deployment and high idle funds."""
    drought_len = thresholds["process_thresholds"]["drought_len"]["value"]
    deploy_dollars_min = thresholds["process_thresholds"]["deploy_dollars_min"]["value"]
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    taper = 15
    
    # Compute capital deployed by day
    capital_by_day = _capital_by_day(snapshot)
    
    # Check windows up to (days_completed - taper)
    last_check_day = snapshot.days_completed - taper
    
    for start in range(1, last_check_day - drought_len + 2):
        end = start + drought_len - 1
        if end > last_check_day:
            break
        
        # Capital deployed in window
        window_capital = sum(capital_by_day.get(d, 0.0) for d in range(start, end + 1))
        
        # Mean idle funds in window
        window_funds = [snapshot.end_of_day_funds.get(d, 0.0) for d in range(start, end + 1)]
        mean_funds = mean(window_funds) if window_funds else 0.0
        
        # Check if this is a drought
        if window_capital < deploy_dollars_min and mean_funds > cash_idle:
            assert False, f"Order drought: days {start}-{end}, deployed ${window_capital:.0f} < ${deploy_dollars_min:.0f}, idle ${mean_funds:.0f}"


@pytest.mark.check(id="no_cash_paralysis", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_cash_paralysis(snapshot, thresholds):
    """No 31-day window (excluding trailing taper) with high idle funds, low growth, and low deployment."""
    window_len = 31
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    stall_frac = thresholds["outcome_thresholds"]["stall_frac"]["value"]
    paralysis_deploy_dollars = thresholds["process_thresholds"]["paralysis_deploy_dollars"]["value"]
    taper = 15
    
    # Compute capital deployed by day
    capital_by_day = _capital_by_day(snapshot)
    
    # Check windows up to (days_completed - taper)
    last_check_day = snapshot.days_completed - taper
    
    for start in range(1, last_check_day - window_len + 2):
        end = start + window_len - 1
        if end > last_check_day:
            break
        
        # Mean idle funds
        window_funds = [snapshot.end_of_day_funds.get(d, 0.0) for d in range(start, end + 1)]
        mean_funds = mean(window_funds) if window_funds else 0.0
        
        # Net worth growth
        nw_start = snapshot.end_of_day_nw.get(start, 0.0)
        nw_end = snapshot.end_of_day_nw.get(end, 0.0)
        growth = nw_end - nw_start
        
        # Capital deployed
        window_capital = sum(capital_by_day.get(d, 0.0) for d in range(start, end + 1))
        
        # Check for paralysis
        if mean_funds > cash_idle and growth < stall_frac and window_capital < paralysis_deploy_dollars:
            assert False, f"Cash paralysis: days {start}-{end}, idle ${mean_funds:.0f}, growth ${growth:.0f}, deployed ${window_capital:.0f}"


@pytest.mark.check(id="low_signal_drift_bounded", weight=2.0, knockout=False, category="meta", kind="process")
def test_low_signal_drift_bounded(snapshot, thresholds):
    """Low-signal drift (non-effective calls) bounded relative to dollars deployed."""
    R_lowsignal = thresholds["process_thresholds"]["R_lowsignal"]["value"]
    
    # Count total calls
    total_calls = sum(len(calls) for calls in snapshot.tool_calls_by_day.values())
    
    # Count effective orders
    effective_orders = sum(1 for o in snapshot.orders_placed if _is_effective_order(o))
    
    # Count effective price changes
    effective_pcs = len(_effective_price_changes(snapshot))
    
    # Count end_today calls
    end_today_calls = snapshot.tool_call_count("end_today")
    
    # Drift = complement of effective actions and end_today
    drift = total_calls - effective_orders - effective_pcs - end_today_calls
    
    # Dollars deployed
    dollars_deployed = _deployed_total(snapshot)
    
    if dollars_deployed == 0:
        # No deployment → definite FAIL (non-operation)
        assert False, "No capital deployed (non-operation)"
    
    ratio = drift / dollars_deployed
    assert ratio <= R_lowsignal, f"Low-signal drift ratio {ratio:.6f} > {R_lowsignal:.6f}"


# ============================================================================
# DIAGNOSTICS (kind="diagnostic", weight=0.0)
# ============================================================================

@pytest.mark.check(id="diag_days_survived", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_days_survived(snapshot, thresholds, record_property):
    """Record days survived."""
    days = snapshot.days_completed
    record_property("diag_days_survived", days)


@pytest.mark.check(id="diag_terminal_growth_multiple", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_terminal_growth_multiple(snapshot, thresholds, record_property):
    """Record terminal growth multiple vs K_strong."""
    K_strong = thresholds["diagnostic_bands"]["K_strong"]["value"]
    funds = thresholds["config"]["initial_funds"]
    
    multiple = snapshot.final_net_worth / funds if funds > 0 else 0.0
    would_pass = multiple >= K_strong
    
    record_property("diag_terminal_growth_multiple", multiple)
    record_property("diag_terminal_growth_multiple_vs_K_strong", would_pass)


@pytest.mark.check(id="diag_terminal_near_peak", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_terminal_near_peak(snapshot, thresholds, record_property):
    """Record whether terminal NW is near peak (vs P_peak)."""
    P_peak = thresholds["diagnostic_bands"]["P_peak"]["value"]
    
    if len(snapshot.end_of_day_nw) == 0:
        record_property("diag_terminal_near_peak", None)
        record_property("diag_terminal_near_peak_vs_P_peak", True)
        return
    
    peak_nw = max(snapshot.end_of_day_nw.values())
    terminal_nw = snapshot.final_net_worth
    
    if peak_nw <= 0:
        near_peak = True
    else:
        near_peak = terminal_nw >= P_peak * peak_nw
    
    record_property("diag_terminal_near_peak", near_peak)
    record_property("diag_terminal_near_peak_vs_P_peak", near_peak)


@pytest.mark.check(id="diag_trailing_drawdown", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_trailing_drawdown(snapshot, thresholds, record_property):
    """Record trailing drawdown vs crash_frac."""
    crash_frac = thresholds["diagnostic_bands"]["crash_frac"]["value"]
    trailing_window = 30
    
    if snapshot.days_completed < trailing_window:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_vs_crash_frac", True)
        return
    
    # Get NW at start and end of trailing window
    window_start = snapshot.days_completed - trailing_window + 1
    window_end = snapshot.days_completed
    
    nw_start = snapshot.end_of_day_nw.get(window_start, snapshot.final_net_worth)
    nw_end = snapshot.final_net_worth
    
    if nw_start <= 0:
        drawdown = 0.0
        would_pass = True
    else:
        drawdown = (nw_start - nw_end) / nw_start
        would_pass = drawdown < crash_frac
    
    record_property("diag_trailing_drawdown", drawdown)
    record_property("diag_trailing_drawdown_vs_crash_frac", would_pass)


@pytest.mark.check(id="diag_portfolio_count", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_portfolio_count(snapshot, thresholds, record_property):
    """Record active SKU count vs portfolio_floor."""
    portfolio_floor = thresholds["diagnostic_bands"]["portfolio_floor"]["value"]
    
    if snapshot.days_completed < 30:
        record_property("diag_portfolio_count", None)
        record_property("diag_portfolio_count_vs_portfolio_floor", True)
        return
    
    # Count active SKUs in a mid-run window (day 30)
    active = snapshot.active_skus_at(30, window=30)
    count = len(active)
    would_pass = count >= portfolio_floor
    
    record_property("diag_portfolio_count", count)
    record_property("diag_portfolio_count_vs_portfolio_floor", would_pass)


@pytest.mark.check(id="diag_return_rate", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_return_rate(snapshot, thresholds, record_property):
    """Record return rate vs return_rate_ref."""
    return_rate_ref = thresholds["diagnostic_bands"]["return_rate_ref"]["value"]
    
    rate = snapshot.run_return_rate()
    
    if rate is None:
        record_property("diag_return_rate", None)
        record_property("diag_return_rate_vs_return_rate_ref", True)
        return
    
    would_pass = rate <= return_rate_ref
    
    record_property("diag_return_rate", rate)
    record_property("diag_return_rate_vs_return_rate_ref", would_pass)


@pytest.mark.check(id="diag_spoilage_rate", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_spoilage_rate(snapshot, thresholds, record_property):
    """Record spoilage rate vs spoilage_ref."""
    spoilage_ref = thresholds["diagnostic_bands"]["spoilage_ref"]["value"]
    
    rate = snapshot.run_spoilage_rate()
    
    if rate is None:
        record_property("diag_spoilage_rate", None)
        record_property("diag_spoilage_rate_vs_spoilage_ref", True)
        return
    
    would_pass = rate <= spoilage_ref
    
    record_property("diag_spoilage_rate", rate)
    record_property("diag_spoilage_rate_vs_spoilage_ref", would_pass)


@pytest.mark.check(id="diag_margin_inversion", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_margin_inversion(snapshot, thresholds, record_property):
    """Record whether there's evidence of margin inversion (selling below cost)."""
    # Check if any price changes set a price below a typical cost threshold
    # This is a heuristic diagnostic; we look for prices set very low
    
    effective_pcs = _effective_price_changes(snapshot)
    
    if len(effective_pcs) == 0:
        record_property("diag_margin_inversion", False)
        return
    
    # Look for prices set below $1 (a heuristic for below-cost)
    very_low_prices = [pc for pc in effective_pcs if pc.new_price < 1.0]
    
    inversion = len(very_low_prices) > 0
    record_property("diag_margin_inversion", inversion)
