"""Deterministic pytest layer for task 000632bd-192b-5d23-8a13-b9af919b1542."""

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
    """Return the capital deployed by an order (cost in dollars)."""
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
    """Return dict[day, float] of capital deployed each day."""
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
    """Verify the run's config matches the frozen task definition."""
    frozen = thresholds["config"]
    
    # Check scalar fields
    if not hasattr(snapshot.config, "initial_funds"):
        raise RuntimeError("snapshot.config missing required field: initial_funds")
    if not hasattr(snapshot.config, "everyday_rent"):
        raise RuntimeError("snapshot.config missing required field: everyday_rent")
    if not hasattr(snapshot.config, "inventory_capacity"):
        raise RuntimeError("snapshot.config missing required field: inventory_capacity")
    if not hasattr(snapshot.config, "global_random_seed"):
        raise RuntimeError("snapshot.config missing required field: global_random_seed")
    if not hasattr(snapshot.config, "enable_review"):
        raise RuntimeError("snapshot.config missing required field: enable_review")
    if not hasattr(snapshot.config, "enable_new"):
        raise RuntimeError("snapshot.config missing required field: enable_new")
    if not hasattr(snapshot.config, "selected_categories"):
        raise RuntimeError("snapshot.config missing required field: selected_categories")
    
    assert snapshot.config.initial_funds == frozen["initial_funds"], \
        f"initial_funds mismatch: {snapshot.config.initial_funds} != {frozen['initial_funds']}"
    assert snapshot.config.everyday_rent == frozen["everyday_rent"], \
        f"everyday_rent mismatch: {snapshot.config.everyday_rent} != {frozen['everyday_rent']}"
    assert snapshot.config.inventory_capacity == frozen["inventory_capacity"], \
        f"inventory_capacity mismatch: {snapshot.config.inventory_capacity} != {frozen['inventory_capacity']}"
    assert snapshot.config.global_random_seed == frozen["global_random_seed"], \
        f"global_random_seed mismatch: {snapshot.config.global_random_seed} != {frozen['global_random_seed']}"
    assert snapshot.config.enable_review == frozen["enable_review"], \
        f"enable_review mismatch: {snapshot.config.enable_review} != {frozen['enable_review']}"
    assert snapshot.config.enable_new == frozen["enable_new"], \
        f"enable_new mismatch: {snapshot.config.enable_new} != {frozen['enable_new']}"
    
    # Check categories list (representation-normalized)
    frozen_cats = frozen["selected_categories_list"]
    run_cats = snapshot.config.selected_categories
    
    def normalize(cat):
        return cat.replace("_", " ").strip().lower()
    
    frozen_normalized = sorted(normalize(c) for c in frozen_cats)
    run_normalized = sorted(normalize(c) for c in run_cats)
    
    assert run_normalized == frozen_normalized, \
        f"selected_categories mismatch: {run_cats} != {frozen_cats}"


@pytest.mark.check(id="integrity_readable_complete", weight=0.0, knockout=False, category="integrity", kind="outcome")
def test_integrity_readable_complete(snapshot, thresholds):
    """Verify the trajectory parsed and the terminal net worth is a finite real number."""
    nw = snapshot.final_net_worth
    if not isinstance(nw, (int, float)):
        raise RuntimeError(f"final_net_worth is not a number: {type(nw)}")
    if not (-1e15 < nw < 1e15):
        raise RuntimeError(f"final_net_worth is not finite: {nw}")


# ============================================================================
# MONEY OUTCOME (kind="outcome", weight=0.0, category="money")
# ============================================================================

@pytest.mark.check(id="money_net_worth_outcome", weight=0.0, knockout=False, category="money", kind="outcome")
def test_money_net_worth_outcome(snapshot, thresholds, record_property):
    """Compute the continuous money outcome O from the horizon-pinned net worth."""
    funds = thresholds["config"]["initial_funds"]
    oracle_nw = thresholds["oracle_nw"]["value"]
    days_requested = thresholds["config"]["days_requested"]
    rent = thresholds["config"]["everyday_rent"]
    
    # Horizon-pinned net worth
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
    """Of all place_order calls, the fraction whose ordered SKUs were covered by an earlier same-day supplier board read."""
    T_supplier = thresholds["process_thresholds"]["T_supplier"]["value"]
    
    # Collect all effective orders
    effective_orders = [o for o in snapshot.orders_placed if _is_effective_order(o)]
    
    if not effective_orders:
        # Non-operation: zero orders is a definite fail
        pytest.fail("No effective orders placed (non-operation)")
    
    covered = 0
    for order in effective_orders:
        day = order.day
        # Check if there was a view_current_date_supplier_prices call earlier on the same day
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        
        # Find the order call index
        order_call_idx = None
        for i, call in enumerate(day_calls):
            if call.tool == "place_order":
                # Check if this is the order we're looking at (match by args if possible)
                # We'll assume orders appear in chronological order
                order_call_idx = i
                break
        
        # Check if there's a supplier board read before this order
        supplier_read_before = False
        if order_call_idx is not None:
            for i in range(order_call_idx):
                if day_calls[i].tool == "view_current_date_supplier_prices":
                    supplier_read_before = True
                    break
        else:
            # If we can't find the order call, check if there's any supplier read that day
            for call in day_calls:
                if call.tool == "view_current_date_supplier_prices":
                    supplier_read_before = True
                    break
        
        if supplier_read_before:
            covered += 1
    
    fraction = covered / len(effective_orders)
    assert fraction >= T_supplier, \
        f"Supplier board before order: {fraction:.2%} < {T_supplier:.2%}"


@pytest.mark.check(id="view_orders_before_place", weight=1.0, knockout=False, category="reorder", kind="process")
def test_view_orders_before_place(snapshot, thresholds):
    """Of order-days, the fraction with an earlier same-day view_current_orders."""
    T_vieworders = thresholds["process_thresholds"]["T_vieworders"]["value"]
    
    # Find all days with effective orders
    order_days = set()
    for order in snapshot.orders_placed:
        if _is_effective_order(order):
            order_days.add(order.day)
    
    if not order_days:
        # Non-operation: zero order-days is a definite fail
        pytest.fail("No order-days (non-operation)")
    
    covered = 0
    for day in order_days:
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        
        # Find first place_order call
        first_order_idx = None
        for i, call in enumerate(day_calls):
            if call.tool == "place_order":
                first_order_idx = i
                break
        
        # Check if there's a view_current_orders before it
        if first_order_idx is not None:
            for i in range(first_order_idx):
                if day_calls[i].tool == "view_current_orders":
                    covered += 1
                    break
    
    fraction = covered / len(order_days)
    assert fraction >= T_vieworders, \
        f"View orders before place: {fraction:.2%} < {T_vieworders:.2%}"


@pytest.mark.check(id="day1_order_placed", weight=1.5, knockout=False, category="setup", kind="process")
def test_day1_order_placed(snapshot, thresholds):
    """A material (effective) opening order within the first 3 days."""
    grace = 3
    
    for order in snapshot.orders_placed:
        if order.day <= grace and _is_effective_order(order):
            return  # Found a material opening order
    
    pytest.fail(f"No effective order placed within first {grace} days")


@pytest.mark.check(id="day1_supplier_read_before_order", weight=0.5, knockout=False, category="setup", kind="process")
def test_day1_supplier_read_before_order(snapshot, thresholds):
    """If a day-1 order exists, a day-1 supplier-board read precedes it."""
    day1_orders = [o for o in snapshot.orders_placed if o.day == 1 and _is_effective_order(o)]
    
    if not day1_orders:
        # No day-1 order: vacuous pass
        return
    
    day1_calls = snapshot.tool_calls_by_day.get(1, [])
    
    # Find first place_order on day 1
    first_order_idx = None
    for i, call in enumerate(day1_calls):
        if call.tool == "place_order":
            first_order_idx = i
            break
    
    # Check if there's a supplier read before it
    if first_order_idx is not None:
        for i in range(first_order_idx):
            if day1_calls[i].tool == "view_current_date_supplier_prices":
                return  # Found supplier read before order
    
    pytest.fail("Day-1 order exists but no day-1 supplier board read precedes it")


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
        # No sales at all: non-operation, definite fail
        pytest.fail("No sales recorded (non-operation)")
    
    # Check for effective price change on or before first sale day
    effective_changes = _effective_price_changes(snapshot)
    for pc in effective_changes:
        if pc.day <= first_sale_day:
            return  # Found effective price change before first sale
    
    pytest.fail(f"No effective price change on or before first sale day {first_sale_day}")


@pytest.mark.check(id="reorder_after_stockout", weight=1.0, knockout=False, category="reorder", kind="process")
def test_reorder_after_stockout(snapshot, thresholds):
    """Of stockout events, the fraction refilled by an effective order within 7 days."""
    T_reorder = thresholds["process_thresholds"]["T_reorder"]["value"]
    reorder_window = 7
    
    if not snapshot.stockout_events:
        # No stockouts: vacuous pass
        return
    
    refilled = 0
    for stockout in snapshot.stockout_events:
        # Verify sku is a bare numeric id
        if not isinstance(stockout.sku, str) or not stockout.sku.isdigit():
            raise RuntimeError(f"Stockout sku is not a bare numeric id: {stockout.sku}")
        
        sku = stockout.sku
        day = stockout.day
        
        # Check for effective orders of this SKU within 7 days
        orders_for_sku = snapshot.orders_by_sku(sku)
        for order in orders_for_sku:
            if _is_effective_order(order) and day < order.day <= day + reorder_window:
                refilled += 1
                break
    
    fraction = refilled / len(snapshot.stockout_events)
    assert fraction >= T_reorder, \
        f"Reorder after stockout: {fraction:.2%} < {T_reorder:.2%}"


@pytest.mark.check(id="no_prolonged_order_drought", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_prolonged_order_drought(snapshot, thresholds):
    """No window of drought_len days (before the last 15-day taper) with < deploy_dollars_min capital deployed while mean idle funds > cash_idle."""
    drought_len = thresholds["process_thresholds"]["drought_len"]["value"]
    deploy_dollars_min = thresholds["process_thresholds"]["deploy_dollars_min"]["value"]
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    taper = 15
    
    # Exclude the trailing taper
    last_day = snapshot.days_completed
    check_until = max(1, last_day - taper)
    
    capital_by_day = _capital_by_day(snapshot)
    
    # Check each window
    for start in range(1, check_until - drought_len + 2):
        end = start + drought_len - 1
        if end > check_until:
            break
        
        # Capital deployed in window
        window_capital = sum(capital_by_day.get(d, 0.0) for d in range(start, end + 1))
        
        # Mean idle funds in window
        window_funds = [snapshot.end_of_day_funds.get(d, 0.0) for d in range(start, end + 1)]
        mean_funds = mean(window_funds) if window_funds else 0.0
        
        # Check violation
        if window_capital < deploy_dollars_min and mean_funds > cash_idle:
            pytest.fail(
                f"Order drought: days {start}-{end} deployed ${window_capital:.0f} < ${deploy_dollars_min:.0f} "
                f"while mean idle funds ${mean_funds:.0f} > ${cash_idle:.0f}"
            )


@pytest.mark.check(id="no_cash_paralysis", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_cash_paralysis(snapshot, thresholds):
    """No 31-day window (excluding trailing taper) where mean idle funds > cash_idle AND net-worth growth < stall_frac AND < paralysis_deploy_dollars capital deployed."""
    window_len = 31
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    stall_frac = thresholds["outcome_thresholds"]["stall_frac"]["value"]
    paralysis_deploy_dollars = thresholds["process_thresholds"]["paralysis_deploy_dollars"]["value"]
    taper = 15
    
    last_day = snapshot.days_completed
    check_until = max(1, last_day - taper)
    
    capital_by_day = _capital_by_day(snapshot)
    
    for start in range(1, check_until - window_len + 2):
        end = start + window_len - 1
        if end > check_until:
            break
        
        # Mean idle funds
        window_funds = [snapshot.end_of_day_funds.get(d, 0.0) for d in range(start, end + 1)]
        mean_funds = mean(window_funds) if window_funds else 0.0
        
        # Net worth growth
        nw_start = snapshot.end_of_day_nw.get(start, 0.0)
        nw_end = snapshot.end_of_day_nw.get(end, 0.0)
        growth = (nw_end - nw_start) / nw_start if nw_start > 0 else 0.0
        
        # Capital deployed
        window_capital = sum(capital_by_day.get(d, 0.0) for d in range(start, end + 1))
        
        # Check violation
        if mean_funds > cash_idle and growth < stall_frac and window_capital < paralysis_deploy_dollars:
            pytest.fail(
                f"Cash paralysis: days {start}-{end} mean funds ${mean_funds:.0f} > ${cash_idle:.0f}, "
                f"growth {growth:.2%} < {stall_frac:.2%}, deployed ${window_capital:.0f} < ${paralysis_deploy_dollars:.0f}"
            )


@pytest.mark.check(id="low_signal_drift_bounded", weight=2.0, knockout=False, category="meta", kind="process")
def test_low_signal_drift_bounded(snapshot, thresholds):
    """Drift (total calls - effective actions - end_today) / dollars_deployed <= R_lowsignal."""
    R_lowsignal = thresholds["process_thresholds"]["R_lowsignal"]["value"]
    
    # Total calls
    total_calls = sum(len(calls) for calls in snapshot.tool_calls_by_day.values())
    
    # Effective orders
    effective_orders = sum(1 for o in snapshot.orders_placed if _is_effective_order(o))
    
    # Effective price changes
    effective_price_changes_count = len(_effective_price_changes(snapshot))
    
    # end_today calls
    end_today_calls = snapshot.tool_call_count("end_today")
    
    # Drift (complement of effective actions and end_today)
    drift = total_calls - effective_orders - effective_price_changes_count - end_today_calls
    
    # Dollars deployed
    dollars_deployed = _deployed_total(snapshot)
    
    if dollars_deployed <= 0:
        # Non-operation: zero dollars deployed is a definite fail
        pytest.fail("No capital deployed (non-operation)")
    
    ratio = drift / dollars_deployed
    assert ratio <= R_lowsignal, \
        f"Low-signal drift ratio: {ratio:.6f} > {R_lowsignal:.6f} (drift={drift}, deployed=${dollars_deployed:.0f})"


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
    
    nw = snapshot.final_net_worth
    multiple = nw / funds if funds > 0 else 0.0
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
        record_property("diag_terminal_near_peak", None)
        record_property("diag_terminal_near_peak_vs_P_peak", True)
        return
    
    ratio = terminal_nw / peak_nw
    would_pass = ratio >= P_peak
    
    record_property("diag_terminal_near_peak", ratio)
    record_property("diag_terminal_near_peak_vs_P_peak", would_pass)


@pytest.mark.check(id="diag_trailing_drawdown", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_trailing_drawdown(snapshot, thresholds, record_property):
    """Record trailing drawdown vs crash_frac."""
    crash_frac = thresholds["diagnostic_bands"]["crash_frac"]["value"]
    trailing_days = 30
    
    last_day = snapshot.days_completed
    if last_day < trailing_days:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_vs_crash_frac", True)
        return
    
    start_day = last_day - trailing_days + 1
    trailing_nw = [snapshot.end_of_day_nw.get(d, 0.0) for d in range(start_day, last_day + 1)]
    
    if not trailing_nw:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_vs_crash_frac", True)
        return
    
    peak_trailing = max(trailing_nw)
    terminal_nw = snapshot.final_net_worth
    
    if peak_trailing <= 0:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_vs_crash_frac", True)
        return
    
    drawdown = (peak_trailing - terminal_nw) / peak_trailing
    would_pass = drawdown <= crash_frac
    
    record_property("diag_trailing_drawdown", drawdown)
    record_property("diag_trailing_drawdown_vs_crash_frac", would_pass)


@pytest.mark.check(id="diag_portfolio_count", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_portfolio_count(snapshot, thresholds, record_property):
    """Record active SKU count vs portfolio_floor."""
    portfolio_floor = thresholds["diagnostic_bands"]["portfolio_floor"]["value"]
    window = 30
    
    last_day = snapshot.days_completed
    if last_day < 1:
        record_property("diag_portfolio_count", None)
        record_property("diag_portfolio_count_vs_portfolio_floor", True)
        return
    
    active = snapshot.active_skus_at(last_day, window=window)
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
        record_property("diag_return_rate_vs_ref", True)
        return
    
    would_pass = rate <= return_rate_ref
    
    record_property("diag_return_rate", rate)
    record_property("diag_return_rate_vs_ref", would_pass)


@pytest.mark.check(id="diag_spoilage_rate", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_spoilage_rate(snapshot, thresholds, record_property):
    """Record spoilage rate vs spoilage_ref."""
    spoilage_ref = thresholds["diagnostic_bands"]["spoilage_ref"]["value"]
    
    rate = snapshot.run_spoilage_rate()
    
    if rate is None:
        record_property("diag_spoilage_rate", None)
        record_property("diag_spoilage_rate_vs_ref", True)
        return
    
    would_pass = rate <= spoilage_ref
    
    record_property("diag_spoilage_rate", rate)
    record_property("diag_spoilage_rate_vs_ref", would_pass)


@pytest.mark.check(id="diag_margin_inversion", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_margin_inversion(snapshot, thresholds, record_property):
    """Record whether there's evidence of margin inversion (selling below cost)."""
    # Check if any price changes set a price below typical supplier costs
    # This is a heuristic diagnostic; we don't have per-SKU cost data in the snapshot
    # So we'll just record whether there are suspiciously low prices
    
    suspiciously_low = []
    for pc in snapshot.price_changes:
        if pc.new_price < 1.0:  # Prices below $1 are suspicious for most categories
            suspiciously_low.append((pc.sku, pc.new_price))
    
    has_inversion = len(suspiciously_low) > 0
    
    record_property("diag_margin_inversion_count", len(suspiciously_low))
    record_property("diag_margin_inversion", has_inversion)
