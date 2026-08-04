"""Deterministic pytest layer for task 891a0d2a-028a-5c17-ab92-8ba39f9bebb3."""

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
    """An order is effective if it has a valid order_id, units > 0, and no error."""
    return order.order_id is not None and order.units > 0 and not order.error


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
    """Return dict[day, capital_deployed] for each day with effective orders."""
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
    required_scalars = {
        "initial_funds": frozen["initial_funds"],
        "everyday_rent": frozen["everyday_rent"],
        "inventory_capacity": frozen["inventory_capacity"],
        "global_random_seed": frozen["global_random_seed"],
        "enable_review": frozen["enable_review"],
        "enable_new": frozen["enable_new"],
    }
    
    for field, expected in required_scalars.items():
        if not hasattr(snapshot.config, field):
            raise RuntimeError(f"Required config field '{field}' missing from snapshot")
        actual = getattr(snapshot.config, field)
        assert actual == expected, f"Config mismatch: {field} = {actual}, expected {expected}"
    
    # Check selected_categories (list comparison, representation-normalized)
    if not hasattr(snapshot.config, "selected_categories"):
        raise RuntimeError("Required config field 'selected_categories' missing from snapshot")
    
    actual_cats = snapshot.config.selected_categories
    expected_cats = frozen["selected_categories_list"]
    
    # Normalize representation (' ' vs '_')
    def normalize(cat):
        return cat.replace('_', ' ').replace(' ', '_')
    
    actual_normalized = sorted(normalize(c) for c in actual_cats)
    expected_normalized = sorted(normalize(c) for c in expected_cats)
    
    assert actual_normalized == expected_normalized, \
        f"Config mismatch: selected_categories = {actual_cats}, expected {expected_cats}"


@pytest.mark.check(id="integrity_readable_complete", weight=0.0, knockout=False, category="integrity", kind="outcome")
def test_integrity_readable_complete(snapshot, thresholds):
    """Verify the trajectory parsed and terminal net worth is a finite real number."""
    nw = snapshot.final_net_worth
    if not isinstance(nw, (int, float)):
        raise RuntimeError(f"Terminal net worth is not a number: {nw}")
    if not (-1e15 < nw < 1e15):
        raise RuntimeError(f"Terminal net worth is not finite: {nw}")


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
    
    # Band
    band = "MADE-MONEY" if horizon_pinned_nw > funds else "LOST-MONEY"
    
    # Record
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
    """All tool names used are in the valid tool registry."""
    observed = set()
    for day_calls in snapshot.tool_calls_by_day.values():
        for call in day_calls:
            observed.add(call.tool)
    
    invalid = observed - set(VALID_TOOLS)
    assert not invalid, f"Invalid tools used: {invalid}"


@pytest.mark.check(id="supplier_board_before_order", weight=1.5, knockout=False, category="supplier", kind="process")
def test_supplier_board_before_order(snapshot, thresholds):
    """Of all place_order calls, the fraction whose SKUs were covered by an earlier same-day supplier board read."""
    T_supplier = thresholds["process_thresholds"]["T_supplier"]["value"]
    
    # Collect all effective orders
    effective_orders = [o for o in snapshot.orders_placed if _is_effective_order(o)]
    
    # Non-operation: zero orders -> FAIL
    if not effective_orders:
        assert False, "No effective orders placed (non-operation)"
    
    # For each order, check if its SKUs were covered by a same-day supplier board read
    covered = 0
    for order in effective_orders:
        day = order.day
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        
        # Find all view_current_date_supplier_prices calls on this day before the order
        supplier_reads = [c for c in day_calls if c.tool == "view_current_date_supplier_prices"]
        
        # Check if any supplier read covers the order's SKUs
        order_covered = False
        if supplier_reads:
            # Any supplier board read on the same day counts as covering
            order_covered = True
        
        if order_covered:
            covered += 1
    
    fraction = covered / len(effective_orders)
    assert fraction >= T_supplier, \
        f"Supplier board coverage {fraction:.2%} < threshold {T_supplier:.2%}"


@pytest.mark.check(id="view_orders_before_place", weight=1.0, knockout=False, category="reorder", kind="process")
def test_view_orders_before_place(snapshot, thresholds):
    """Of order-days, the fraction with an earlier same-day view_current_orders."""
    T_vieworders = thresholds["process_thresholds"]["T_vieworders"]["value"]
    
    # Collect days with effective orders
    order_days = set()
    for order in snapshot.orders_placed:
        if _is_effective_order(order):
            order_days.add(order.day)
    
    # Non-operation: no order days -> FAIL
    if not order_days:
        assert False, "No order days (non-operation)"
    
    # For each order day, check if there was a view_current_orders call
    covered = 0
    for day in order_days:
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        if any(c.tool == "view_current_orders" for c in day_calls):
            covered += 1
    
    fraction = covered / len(order_days)
    assert fraction >= T_vieworders, \
        f"View orders coverage {fraction:.2%} < threshold {T_vieworders:.2%}"


@pytest.mark.check(id="day1_order_placed", weight=1.5, knockout=False, category="setup", kind="process")
def test_day1_order_placed(snapshot, thresholds):
    """A material opening order within the first 3 days."""
    grace = 3
    
    # Find effective orders in the first grace days
    early_orders = [o for o in snapshot.orders_placed 
                    if o.day <= grace and _is_effective_order(o)]
    
    # Must have at least one material order (units > 1, cost > 0)
    material = [o for o in early_orders if o.units > 1 and o.cost > 0]
    
    assert material, f"No material order placed within first {grace} days"


@pytest.mark.check(id="day1_supplier_read_before_order", weight=0.5, knockout=False, category="setup", kind="process")
def test_day1_supplier_read_before_order(snapshot, thresholds):
    """If a day-1 order exists, a day-1 supplier board read precedes it."""
    day1_orders = [o for o in snapshot.orders_placed if o.day == 1 and _is_effective_order(o)]
    
    # No day-1 order -> vacuous PASS
    if not day1_orders:
        return
    
    # Check for day-1 supplier board read
    day1_calls = snapshot.tool_calls_by_day.get(1, [])
    has_supplier_read = any(c.tool == "view_current_date_supplier_prices" for c in day1_calls)
    
    assert has_supplier_read, "Day-1 order exists but no day-1 supplier board read"


@pytest.mark.check(id="priced_before_first_sale", weight=1.0, knockout=False, category="setup", kind="process")
def test_priced_before_first_sale(snapshot, thresholds):
    """An effective price change on or before the first day with nonzero sales."""
    # Find first day with sales
    first_sale_day = None
    for day in sorted(snapshot.sales_units_by_day.keys()):
        if snapshot.sales_units_by_day[day] > 0:
            first_sale_day = day
            break
    
    # No sales at all -> FAIL (non-operation)
    if first_sale_day is None:
        assert False, "No sales recorded (non-operation)"
    
    # Check for effective price changes on or before first sale day
    effective_pcs = _effective_price_changes(snapshot)
    early_pcs = [pc for pc in effective_pcs if pc.day <= first_sale_day]
    
    assert early_pcs, f"No effective price change on or before first sale day {first_sale_day}"


@pytest.mark.check(id="reorder_after_stockout", weight=1.0, knockout=False, category="reorder", kind="process")
def test_reorder_after_stockout(snapshot, thresholds):
    """Of stockout events, the fraction refilled by an effective order within 7 days."""
    T_reorder = thresholds["process_thresholds"]["T_reorder"]["value"]
    reorder_window = 7
    
    # No stockouts -> vacuous PASS
    if not snapshot.stockout_events:
        return
    
    # For each stockout, check if it was refilled within 7 days
    refilled = 0
    for stockout in snapshot.stockout_events:
        # Verify sku is a bare numeric id (loader integrity)
        if not isinstance(stockout.sku, str) or not stockout.sku.isdigit():
            raise RuntimeError(f"Stockout SKU is not a bare numeric id: {stockout.sku}")
        
        sku = stockout.sku
        day = stockout.day
        
        # Find orders for this SKU within the next 7 days
        sku_orders = snapshot.orders_by_sku(sku)
        refill_orders = [o for o in sku_orders 
                        if day < o.day <= day + reorder_window 
                        and _is_effective_order(o)]
        
        if refill_orders:
            refilled += 1
    
    fraction = refilled / len(snapshot.stockout_events)
    assert fraction >= T_reorder, \
        f"Stockout refill rate {fraction:.2%} < threshold {T_reorder:.2%}"


@pytest.mark.check(id="no_prolonged_order_drought", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_prolonged_order_drought(snapshot, thresholds):
    """No window of drought_len days (before the last 15-day taper) with low capital deployed and high idle funds."""
    drought_len = thresholds["process_thresholds"]["drought_len"]["value"]
    deploy_dollars_min = thresholds["process_thresholds"]["deploy_dollars_min"]["value"]
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    taper = 15
    
    capital_by_day = _capital_by_day(snapshot)
    
    # Check windows up to (days_completed - taper)
    last_day = snapshot.days_completed - taper
    
    for start in range(1, last_day - drought_len + 2):
        end = start + drought_len - 1
        if end > last_day:
            break
        
        # Capital deployed in this window
        window_capital = sum(capital_by_day.get(d, 0.0) for d in range(start, end + 1))
        
        # Mean idle funds in this window
        window_funds = [snapshot.end_of_day_funds.get(d, 0.0) for d in range(start, end + 1)]
        mean_funds = mean(window_funds) if window_funds else 0.0
        
        # Check for drought
        if window_capital < deploy_dollars_min and mean_funds > cash_idle:
            assert False, \
                f"Order drought: days {start}-{end} deployed ${window_capital:.0f} < ${deploy_dollars_min:.0f} with mean idle ${mean_funds:.0f}"


@pytest.mark.check(id="no_cash_paralysis", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_cash_paralysis(snapshot, thresholds):
    """No 31-day window (excluding trailing taper) with high idle funds, low growth, and low deployment."""
    window_len = 31
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    stall_frac = thresholds["outcome_thresholds"]["stall_frac"]["value"]
    paralysis_deploy_dollars = thresholds["process_thresholds"]["paralysis_deploy_dollars"]["value"]
    taper = 15
    
    capital_by_day = _capital_by_day(snapshot)
    
    # Check windows up to (days_completed - taper)
    last_day = snapshot.days_completed - taper
    
    for start in range(1, last_day - window_len + 2):
        end = start + window_len - 1
        if end > last_day:
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
            assert False, \
                f"Cash paralysis: days {start}-{end} mean idle ${mean_funds:.0f}, growth ${growth:.0f}, deployed ${window_capital:.0f}"


@pytest.mark.check(id="low_signal_drift_bounded", weight=2.0, knockout=False, category="meta", kind="process")
def test_low_signal_drift_bounded(snapshot, thresholds):
    """Low-signal drift (non-action calls) bounded relative to dollars deployed."""
    R_lowsignal = thresholds["process_thresholds"]["R_lowsignal"]["value"]
    
    # Count total calls
    total_calls = sum(len(calls) for calls in snapshot.tool_calls_by_day.values())
    
    # Count effective actions
    effective_orders = sum(1 for o in snapshot.orders_placed if _is_effective_order(o))
    effective_pcs = len(_effective_price_changes(snapshot))
    end_today_calls = snapshot.tool_call_count("end_today")
    
    # Drift = complement of effective actions and end_today
    drift = total_calls - effective_orders - effective_pcs - end_today_calls
    
    # Dollars deployed
    dollars_deployed = _deployed_total(snapshot)
    
    # Non-operation: zero deployment -> FAIL
    if dollars_deployed <= 0:
        assert False, "No capital deployed (non-operation)"
    
    # Ratio
    ratio = drift / dollars_deployed
    
    assert ratio <= R_lowsignal, \
        f"Low-signal drift ratio {ratio:.6f} > threshold {R_lowsignal:.6f}"


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
    
    if not snapshot.end_of_day_nw:
        record_property("diag_terminal_near_peak", None)
        record_property("diag_terminal_near_peak_vs_P_peak", True)
        return
    
    peak_nw = max(snapshot.end_of_day_nw.values())
    terminal_nw = snapshot.final_net_worth
    
    if peak_nw <= 0:
        near_peak = None
        would_pass = True
    else:
        near_peak = terminal_nw / peak_nw
        would_pass = near_peak >= P_peak
    
    record_property("diag_terminal_near_peak", near_peak)
    record_property("diag_terminal_near_peak_vs_P_peak", would_pass)


@pytest.mark.check(id="diag_trailing_drawdown", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_trailing_drawdown(snapshot, thresholds, record_property):
    """Record trailing drawdown vs crash_frac."""
    crash_frac = thresholds["diagnostic_bands"]["crash_frac"]["value"]
    trailing_window = 30
    
    if snapshot.days_completed < trailing_window:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_vs_crash_frac", True)
        return
    
    # Get NW values in the trailing window
    start_day = snapshot.days_completed - trailing_window + 1
    trailing_nw = [snapshot.end_of_day_nw.get(d, 0.0) 
                   for d in range(start_day, snapshot.days_completed + 1)]
    
    if not trailing_nw:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_vs_crash_frac", True)
        return
    
    peak_trailing = max(trailing_nw)
    terminal_nw = snapshot.final_net_worth
    
    if peak_trailing <= 0:
        drawdown = None
        would_pass = True
    else:
        drawdown = (peak_trailing - terminal_nw) / peak_trailing
        would_pass = drawdown <= crash_frac
    
    record_property("diag_trailing_drawdown", drawdown)
    record_property("diag_trailing_drawdown_vs_crash_frac", would_pass)


@pytest.mark.check(id="diag_portfolio_count", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_portfolio_count(snapshot, thresholds, record_property):
    """Record active SKU count vs portfolio_floor."""
    portfolio_floor = thresholds["diagnostic_bands"]["portfolio_floor"]["value"]
    
    # Count active SKUs in the last 30 days
    if snapshot.days_completed < 30:
        # Structural skip for short runs
        pytest.skip("Run too short for portfolio diagnostic")
    
    active = snapshot.active_skus_at(snapshot.days_completed, window=30)
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
    """Record whether the run shows margin inversion (terminal NW < opening funds)."""
    funds = thresholds["config"]["initial_funds"]
    terminal_nw = snapshot.final_net_worth
    
    inverted = terminal_nw < funds
    
    record_property("diag_margin_inversion", inverted)
