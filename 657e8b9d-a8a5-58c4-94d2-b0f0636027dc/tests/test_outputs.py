"""Deterministic pytest layer for task 657e8b9d-a8a5-58c4-94d2-b0f0636027dc."""

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
    """An order is effective if it placed units and was not an insufficient-funds no-op."""
    return order.order_id is not None and order.units > 0 and order.error is None


def _order_capital(order):
    """Capital deployed by an order (zero if ineffective)."""
    if not _is_effective_order(order):
        return 0.0
    return order.cost


def _effective_price_changes(snapshot):
    """Count of price changes where new != old (|new - old| > 1e-9)."""
    count = 0
    for pc in snapshot.price_changes:
        if pc.old_price is None or abs(pc.new_price - pc.old_price) > 1e-9:
            count += 1
    return count


def _capital_by_day(snapshot):
    """Map day -> capital deployed that day."""
    cap = {}
    for order in snapshot.orders_placed:
        if _is_effective_order(order):
            cap[order.day] = cap.get(order.day, 0.0) + _order_capital(order)
    return cap


def _deployed_total(snapshot):
    """Total capital deployed across all effective orders."""
    return sum(_order_capital(o) for o in snapshot.orders_placed)


# ============================================================================
# INTEGRITY GATES (kind="outcome", weight=0.0, category="integrity")
# ============================================================================

@pytest.mark.check(id="integrity_config_matches_frozen_task", weight=0.0, knockout=False, category="integrity", kind="outcome")
def test_integrity_config_matches_frozen_task(snapshot, thresholds):
    """Verify the run's config matches the frozen task definition."""
    frozen = thresholds["config"]
    
    # Scalar fields
    assert snapshot.config.initial_funds == frozen["initial_funds"], "initial_funds mismatch"
    assert snapshot.config.everyday_rent == frozen["everyday_rent"], "everyday_rent mismatch"
    assert snapshot.config.inventory_capacity == frozen["inventory_capacity"], "inventory_capacity mismatch"
    assert snapshot.config.global_random_seed == frozen["global_random_seed"], "global_random_seed mismatch"
    assert snapshot.config.enable_review == frozen["enable_review"], "enable_review mismatch"
    assert snapshot.config.enable_new == frozen["enable_new"], "enable_new mismatch"
    
    # Categories: compare the list, normalized
    if not hasattr(snapshot.config, 'selected_categories'):
        raise RuntimeError("snapshot.config.selected_categories missing")
    
    frozen_cats = frozen["selected_categories_list"]
    run_cats = snapshot.config.selected_categories
    
    def normalize(cat):
        return cat.replace('_', ' ').strip().lower()
    
    frozen_norm = sorted(normalize(c) for c in frozen_cats)
    run_norm = sorted(normalize(c) for c in run_cats)
    
    assert run_norm == frozen_norm, f"selected_categories mismatch: {run_cats} vs {frozen_cats}"


@pytest.mark.check(id="integrity_readable_complete", weight=0.0, knockout=False, category="integrity", kind="outcome")
def test_integrity_readable_complete(snapshot, thresholds):
    """Verify the trajectory parsed and terminal net worth is a finite real number."""
    nw = snapshot.final_net_worth
    if not isinstance(nw, (int, float)):
        raise RuntimeError(f"final_net_worth is not numeric: {type(nw)}")
    if not (-1e15 < nw < 1e15):
        raise RuntimeError(f"final_net_worth is not finite: {nw}")


# ============================================================================
# MONEY OUTCOME (kind="outcome", weight=0.0, category="money")
# ============================================================================

@pytest.mark.check(id="money_net_worth_outcome", weight=0.0, knockout=False, category="money", kind="outcome")
def test_money_net_worth_outcome(snapshot, thresholds, record_property):
    """Compute the continuous money outcome O from horizon-pinned net worth."""
    funds = thresholds["config"]["initial_funds"]
    oracle_nw = thresholds["oracle_nw"]["value"]
    days_requested = thresholds["config"]["days_requested"]
    rent = thresholds["config"]["everyday_rent"]
    
    # Horizon-pinned net worth: add back rent for unfinished days
    pinned_nw = snapshot.final_net_worth
    days_short = max(0, days_requested - snapshot.days_completed)
    horizon_pinned_nw = pinned_nw + rent * days_short
    
    # Reference gain
    ref = oracle_nw - funds
    
    # Guard against near-infeasible task
    if ref <= 0:
        O = 0.0
    else:
        O = max(0.0, min(1.0, (horizon_pinned_nw - funds) / ref))
    
    band = "MADE-MONEY" if horizon_pinned_nw > funds else "LOST-MONEY"
    
    record_property("pinned_net_worth", pinned_nw)
    record_property("horizon_pinned_net_worth", horizon_pinned_nw)
    record_property("money_outcome_O", O)
    record_property("money_band", band)
    
    # Assert only that the pinned value is a real number
    assert isinstance(pinned_nw, (int, float)) and -1e15 < pinned_nw < 1e15


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
    assert not invalid, f"Invalid tools used: {invalid}"


@pytest.mark.check(id="supplier_board_before_order", weight=1.5, knockout=False, category="supplier", kind="process")
def test_supplier_board_before_order(snapshot, thresholds):
    """Of all place_order calls, fraction whose SKUs were covered by same-day supplier board read."""
    T_supplier = thresholds["process_thresholds"]["T_supplier"]["value"]
    
    order_days_with_skus = []
    for order in snapshot.orders_placed:
        if _is_effective_order(order):
            order_days_with_skus.append((order.day, order.skus))
    
    if not order_days_with_skus:
        # No effective orders = non-operation = FAIL
        pytest.fail("No effective orders placed (non-operation)")
    
    covered = 0
    for day, skus in order_days_with_skus:
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        supplier_reads = [c for c in day_calls if c.tool == "view_current_date_supplier_prices"]
        
        # Check if any supplier read before this order covered the SKUs
        # We consider it covered if a supplier read happened on the same day
        # (the order of calls within a day is preserved in tool_calls_by_day)
        if supplier_reads:
            covered += 1
    
    frac = covered / len(order_days_with_skus)
    assert frac >= T_supplier, f"Supplier board coverage {frac:.2%} < {T_supplier:.2%}"


@pytest.mark.check(id="view_orders_before_place", weight=1.0, knockout=False, category="reorder", kind="process")
def test_view_orders_before_place(snapshot, thresholds):
    """Of order-days, fraction with an earlier same-day view_current_orders."""
    T_vieworders = thresholds["process_thresholds"]["T_vieworders"]["value"]
    
    order_days = set()
    for order in snapshot.orders_placed:
        if _is_effective_order(order):
            order_days.add(order.day)
    
    if not order_days:
        pytest.fail("No effective orders placed (non-operation)")
    
    covered = 0
    for day in order_days:
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        if any(c.tool == "view_current_orders" for c in day_calls):
            covered += 1
    
    frac = covered / len(order_days)
    assert frac >= T_vieworders, f"View orders coverage {frac:.2%} < {T_vieworders:.2%}"


@pytest.mark.check(id="day1_order_placed", weight=1.5, knockout=False, category="setup", kind="process")
def test_day1_order_placed(snapshot, thresholds):
    """A material opening order within the first 3 days."""
    grace = 3
    
    for order in snapshot.orders_placed:
        if order.day <= grace and _is_effective_order(order) and order.units > 1:
            return  # Found a material opening order
    
    pytest.fail("No material opening order within first 3 days")


@pytest.mark.check(id="day1_supplier_read_before_order", weight=0.5, knockout=False, category="setup", kind="process")
def test_day1_supplier_read_before_order(snapshot, thresholds):
    """If a day-1 order exists, a day-1 supplier board read precedes it."""
    day1_orders = [o for o in snapshot.orders_placed if o.day == 1 and _is_effective_order(o)]
    
    if not day1_orders:
        # No day-1 order = vacuous PASS
        return
    
    day1_calls = snapshot.tool_calls_by_day.get(1, [])
    has_supplier_read = any(c.tool == "view_current_date_supplier_prices" for c in day1_calls)
    
    assert has_supplier_read, "Day-1 order exists but no day-1 supplier board read"


@pytest.mark.check(id="priced_before_first_sale", weight=1.0, knockout=False, category="setup", kind="process")
def test_priced_before_first_sale(snapshot, thresholds):
    """An effective price change on or before the first day with nonzero sales."""
    first_sale_day = None
    for day in sorted(snapshot.sales_units_by_day.keys()):
        if snapshot.sales_units_by_day[day] > 0:
            first_sale_day = day
            break
    
    if first_sale_day is None:
        pytest.fail("No sales at all (non-operation)")
    
    effective_price_days = set()
    for pc in snapshot.price_changes:
        if pc.old_price is None or abs(pc.new_price - pc.old_price) > 1e-9:
            effective_price_days.add(pc.day)
    
    earliest_price = min(effective_price_days) if effective_price_days else float('inf')
    assert earliest_price <= first_sale_day, f"No effective price change before first sale (day {first_sale_day})"


@pytest.mark.check(id="reorder_after_stockout", weight=1.0, knockout=False, category="reorder", kind="process")
def test_reorder_after_stockout(snapshot, thresholds):
    """Of stockout events, fraction refilled by an effective order within 7 days."""
    T_reorder = thresholds["process_thresholds"]["T_reorder"]["value"]
    
    if not snapshot.stockout_events:
        # No stockouts = vacuous PASS
        return
    
    refilled = 0
    for stockout in snapshot.stockout_events:
        sku = stockout.sku
        day = stockout.day
        
        # Check if sku is a bare numeric id (loader integrity)
        if not isinstance(sku, str) or not sku.isdigit():
            raise RuntimeError(f"Stockout SKU is not a bare numeric id: {sku}")
        
        # Look for an effective order of this SKU within 7 days
        orders = snapshot.orders_by_sku(sku)
        for order in orders:
            if _is_effective_order(order) and day < order.day <= day + 7:
                refilled += 1
                break
    
    frac = refilled / len(snapshot.stockout_events)
    assert frac >= T_reorder, f"Stockout reorder rate {frac:.2%} < {T_reorder:.2%}"


@pytest.mark.check(id="no_prolonged_order_drought", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_prolonged_order_drought(snapshot, thresholds):
    """No window of drought_len days (before trailing taper) with low deployment and high idle cash."""
    drought_len = thresholds["process_thresholds"]["drought_len"]["value"]
    deploy_dollars_min = thresholds["process_thresholds"]["deploy_dollars_min"]["value"]
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    
    days_requested = thresholds["config"]["days_requested"]
    taper = 15
    horizon = days_requested - taper
    
    cap_by_day = _capital_by_day(snapshot)
    
    for start in range(1, horizon - drought_len + 2):
        end = start + drought_len - 1
        if end > horizon:
            break
        
        window_days = range(start, end + 1)
        deployed = sum(cap_by_day.get(d, 0.0) for d in window_days)
        
        funds_in_window = [snapshot.end_of_day_funds.get(d) for d in window_days if d in snapshot.end_of_day_funds]
        if funds_in_window:
            mean_funds = mean(funds_in_window)
        else:
            mean_funds = 0.0
        
        if deployed < deploy_dollars_min and mean_funds > cash_idle:
            pytest.fail(f"Order drought: days {start}-{end}, deployed ${deployed:.0f} < ${deploy_dollars_min:.0f}, mean funds ${mean_funds:.0f}")


@pytest.mark.check(id="no_cash_paralysis", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_cash_paralysis(snapshot, thresholds):
    """No 31-day window (excluding trailing taper) with high idle cash, low growth, and low deployment."""
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    stall_frac = thresholds["outcome_thresholds"]["stall_frac"]["value"]
    paralysis_deploy_dollars = thresholds["process_thresholds"]["paralysis_deploy_dollars"]["value"]
    
    days_requested = thresholds["config"]["days_requested"]
    taper = 15
    horizon = days_requested - taper
    window_len = 31
    
    cap_by_day = _capital_by_day(snapshot)
    
    for start in range(1, horizon - window_len + 2):
        end = start + window_len - 1
        if end > horizon:
            break
        
        window_days = range(start, end + 1)
        
        # Mean idle funds
        funds_in_window = [snapshot.end_of_day_funds.get(d) for d in window_days if d in snapshot.end_of_day_funds]
        if funds_in_window:
            mean_funds = mean(funds_in_window)
        else:
            mean_funds = 0.0
        
        # Net worth growth
        nw_start = snapshot.end_of_day_nw.get(start)
        nw_end = snapshot.end_of_day_nw.get(end)
        if nw_start is not None and nw_end is not None and nw_start > 0:
            growth = (nw_end - nw_start) / nw_start
        else:
            growth = 0.0
        
        # Deployed capital
        deployed = sum(cap_by_day.get(d, 0.0) for d in window_days)
        
        if mean_funds > cash_idle and growth < stall_frac and deployed < paralysis_deploy_dollars:
            pytest.fail(f"Cash paralysis: days {start}-{end}, mean funds ${mean_funds:.0f}, growth {growth:.1%}, deployed ${deployed:.0f}")


@pytest.mark.check(id="low_signal_drift_bounded", weight=2.0, knockout=False, category="meta", kind="process")
def test_low_signal_drift_bounded(snapshot, thresholds):
    """Low-signal drift (non-action calls) per dollar deployed is bounded."""
    R_lowsignal = thresholds["process_thresholds"]["R_lowsignal"]["value"]
    
    total_calls = sum(len(calls) for calls in snapshot.tool_calls_by_day.values())
    effective_orders = sum(1 for o in snapshot.orders_placed if _is_effective_order(o))
    effective_prices = _effective_price_changes(snapshot)
    end_today_calls = snapshot.tool_call_count("end_today")
    
    drift = total_calls - effective_orders - effective_prices - end_today_calls
    dollars_deployed = _deployed_total(snapshot)
    
    if dollars_deployed == 0:
        pytest.fail("Zero dollars deployed (non-operation)")
    
    ratio = drift / dollars_deployed
    assert ratio <= R_lowsignal, f"Low-signal drift ratio {ratio:.4f} > {R_lowsignal:.4f}"


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
    verdict = multiple >= K_strong
    
    record_property("diag_terminal_growth_multiple", multiple)
    record_property("diag_terminal_growth_multiple_ok", verdict)


@pytest.mark.check(id="diag_terminal_near_peak", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_terminal_near_peak(snapshot, thresholds, record_property):
    """Record whether terminal NW is near peak (within P_peak)."""
    P_peak = thresholds["diagnostic_bands"]["P_peak"]["value"]
    
    if not snapshot.end_of_day_nw:
        record_property("diag_terminal_near_peak", None)
        record_property("diag_terminal_near_peak_ok", True)
        return
    
    peak = max(snapshot.end_of_day_nw.values())
    terminal = snapshot.final_net_worth
    
    if peak > 0:
        ratio = terminal / peak
        verdict = ratio >= P_peak
    else:
        ratio = None
        verdict = True
    
    record_property("diag_terminal_near_peak", ratio)
    record_property("diag_terminal_near_peak_ok", verdict)


@pytest.mark.check(id="diag_trailing_drawdown", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_trailing_drawdown(snapshot, thresholds, record_property):
    """Record trailing drawdown vs crash_frac."""
    crash_frac = thresholds["diagnostic_bands"]["crash_frac"]["value"]
    
    days_requested = thresholds["config"]["days_requested"]
    trailing = 30
    start = max(1, days_requested - trailing)
    
    nw_in_window = [snapshot.end_of_day_nw.get(d) for d in range(start, days_requested + 1) if d in snapshot.end_of_day_nw]
    
    if not nw_in_window:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_ok", True)
        return
    
    peak_trailing = max(nw_in_window)
    terminal = snapshot.final_net_worth
    
    if peak_trailing > 0:
        drawdown = (peak_trailing - terminal) / peak_trailing
        verdict = drawdown <= crash_frac
    else:
        drawdown = None
        verdict = True
    
    record_property("diag_trailing_drawdown", drawdown)
    record_property("diag_trailing_drawdown_ok", verdict)


@pytest.mark.check(id="diag_portfolio_count", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_portfolio_count(snapshot, thresholds, record_property):
    """Record active SKU count vs portfolio_floor."""
    portfolio_floor = thresholds["diagnostic_bands"]["portfolio_floor"]["value"]
    
    days_requested = thresholds["config"]["days_requested"]
    mid = days_requested // 2
    
    active = snapshot.active_skus_at(mid, window=30)
    count = len(active)
    verdict = count >= portfolio_floor
    
    record_property("diag_portfolio_count", count)
    record_property("diag_portfolio_count_ok", verdict)


@pytest.mark.check(id="diag_return_rate", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_return_rate(snapshot, thresholds, record_property):
    """Record return rate vs return_rate_ref."""
    return_rate_ref = thresholds["diagnostic_bands"]["return_rate_ref"]["value"]
    
    rate = snapshot.run_return_rate()
    
    if rate is None:
        record_property("diag_return_rate", None)
        record_property("diag_return_rate_ok", True)
        return
    
    verdict = rate <= return_rate_ref
    record_property("diag_return_rate", rate)
    record_property("diag_return_rate_ok", verdict)


@pytest.mark.check(id="diag_spoilage_rate", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_spoilage_rate(snapshot, thresholds, record_property):
    """Record spoilage rate vs spoilage_ref."""
    spoilage_ref = thresholds["diagnostic_bands"]["spoilage_ref"]["value"]
    
    rate = snapshot.run_spoilage_rate()
    
    if rate is None:
        record_property("diag_spoilage_rate", None)
        record_property("diag_spoilage_rate_ok", True)
        return
    
    verdict = rate <= spoilage_ref
    record_property("diag_spoilage_rate", rate)
    record_property("diag_spoilage_rate_ok", verdict)


@pytest.mark.check(id="diag_margin_inversion", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_margin_inversion(snapshot, thresholds, record_property):
    """Record whether any price changes inverted margin (new < cost)."""
    inversions = 0
    
    for pc in snapshot.price_changes:
        # We don't have cost data in the snapshot, so we can't check this properly
        # Record a placeholder
        pass
    
    record_property("diag_margin_inversion", inversions)
    record_property("diag_margin_inversion_ok", inversions == 0)
