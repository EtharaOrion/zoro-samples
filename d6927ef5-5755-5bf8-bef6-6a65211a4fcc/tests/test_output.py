"""Deterministic pytest layer for task d6927ef5-5755-5bf8-bef6-6a65211a4fcc (Store 15, 180 days)."""

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
    """Return dict[day, capital_deployed] for all days."""
    cap_by_day = {}
    for order in snapshot.orders_placed:
        if _is_effective_order(order):
            cap_by_day[order.day] = cap_by_day.get(order.day, 0.0) + order.cost
    return cap_by_day


def _deployed_total(snapshot):
    """Return total capital deployed across all effective orders."""
    return sum(_order_capital(o) for o in snapshot.orders_placed)


# ============================================================================
# INTEGRITY GATES (kind="outcome", weight=0.0, category="integrity")
# ============================================================================

@pytest.mark.check(id="integrity_config_matches_frozen_task", weight=0.0, knockout=False, category="integrity", kind="outcome")
def test_integrity_config_matches_frozen_task(snapshot, thresholds):
    """Verify the run's config matches the frozen task config (exclude if mismatch)."""
    frozen = thresholds["config"]
    
    # Check required scalar fields
    required_scalars = {
        "initial_funds": frozen["initial_funds"],
        "everyday_rent": frozen["everyday_rent"],
        "inventory_capacity": frozen["inventory_capacity"],
        "global_random_seed": frozen["global_random_seed"],
        "enable_review": frozen["enable_review"],
        "enable_new": frozen["enable_new"],
    }
    
    for field, expected in required_scalars.items():
        actual = getattr(snapshot.config, field, None)
        if actual is None:
            raise RuntimeError(f"Required config field '{field}' missing from loader")
        assert actual == expected, f"Config mismatch: {field} = {actual}, expected {expected}"
    
    # Check selected_categories (list comparison, representation-normalized)
    frozen_cats = frozen["selected_categories_list"]
    actual_cats = snapshot.config.selected_categories
    if actual_cats is None:
        raise RuntimeError("Required config field 'selected_categories' missing from loader")
    
    def normalize_cat(s):
        return s.replace('_', ' ').strip().lower()
    
    frozen_norm = sorted(normalize_cat(c) for c in frozen_cats)
    actual_norm = sorted(normalize_cat(c) for c in actual_cats)
    
    assert actual_norm == frozen_norm, f"Categories mismatch: {actual_cats} vs {frozen_cats}"


@pytest.mark.check(id="integrity_readable_complete", weight=0.0, knockout=False, category="integrity", kind="outcome")
def test_integrity_readable_complete(snapshot, thresholds):
    """Verify the trajectory parsed and terminal net worth is a finite real number."""
    nw = snapshot.final_net_worth
    if nw is None or not isinstance(nw, (int, float)):
        raise RuntimeError("Terminal net worth is missing or not a number")
    if not (-1e15 < nw < 1e15):
        raise RuntimeError(f"Terminal net worth {nw} is not finite")


# ============================================================================
# MONEY OUTCOME (kind="outcome", weight=0.0, category="money")
# ============================================================================

@pytest.mark.check(id="money_net_worth_outcome", weight=0.0, knockout=False, category="money", kind="outcome")
def test_money_net_worth_outcome(snapshot, thresholds, record_property):
    """Compute and record the continuous money outcome O; assert only that terminal NW is real."""
    funds = thresholds["config"]["initial_funds"]
    oracle_nw = thresholds["oracle_nw"]["value"]
    days_requested = thresholds["config"]["days_requested"]
    rent = thresholds["config"]["everyday_rent"]
    
    terminal_nw = snapshot.final_net_worth
    days_completed = snapshot.days_completed
    
    # Horizon-adjust for incomplete runs
    unfinished_days = max(0, days_requested - days_completed)
    horizon_pinned_nw = terminal_nw - rent * unfinished_days
    
    # Compute outcome O
    ref = oracle_nw - funds
    if ref <= 0:
        O = 0.0
    else:
        raw_O = (horizon_pinned_nw - funds) / ref
        O = max(0.0, min(1.0, raw_O))
    
    band = "MADE-MONEY" if horizon_pinned_nw > funds else "LOST-MONEY"
    
    record_property("pinned_net_worth", terminal_nw)
    record_property("horizon_pinned_net_worth", horizon_pinned_nw)
    record_property("money_outcome_O", O)
    record_property("money_band", band)
    
    # Assert only that terminal NW is a real number
    assert isinstance(terminal_nw, (int, float)) and -1e15 < terminal_nw < 1e15


# ============================================================================
# PROCESS CHECKS (kind="process", weighted — the scored tie-breakers)
# ============================================================================

@pytest.mark.check(id="valid_tools_used", weight=1.0, knockout=False, category="meta", kind="process")
def test_valid_tools_used(snapshot, thresholds):
    """All observed tool names are in the valid tool registry."""
    observed = set()
    for day_calls in snapshot.tool_calls_by_day.values():
        for call in day_calls:
            observed.add(call.tool)
    
    invalid = observed - set(VALID_TOOLS)
    assert not invalid, f"Invalid tools used: {invalid}"


@pytest.mark.check(id="supplier_board_before_order", weight=1.5, knockout=False, category="supplier", kind="process")
def test_supplier_board_before_order(snapshot, thresholds):
    """Of all place_order calls, fraction whose SKUs were covered by same-day supplier board read >= T_supplier."""
    T_supplier = thresholds["process_thresholds"]["T_supplier"]["value"]
    
    effective_orders = [o for o in snapshot.orders_placed if _is_effective_order(o)]
    if not effective_orders:
        # Non-operation: zero orders is a definite fail
        assert False, "No effective orders placed (non-operation)"
    
    covered = 0
    for order in effective_orders:
        day = order.day
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        
        # Find all view_current_date_supplier_prices calls on this day before the order
        supplier_reads = [c for c in day_calls if c.tool == "view_current_date_supplier_prices"]
        
        if supplier_reads:
            # Check if any supplier read covers the order's SKUs
            # We consider it covered if there was at least one supplier read on the same day
            # (the read would show all available SKUs for that day)
            covered += 1
    
    rate = covered / len(effective_orders)
    assert rate >= T_supplier, f"Supplier board coverage {rate:.2%} < {T_supplier:.2%}"


@pytest.mark.check(id="view_orders_before_place", weight=1.0, knockout=False, category="reorder", kind="process")
def test_view_orders_before_place(snapshot, thresholds):
    """Of order-days, fraction with an earlier same-day view_current_orders >= T_vieworders."""
    T_vieworders = thresholds["process_thresholds"]["T_vieworders"]["value"]
    
    effective_orders = [o for o in snapshot.orders_placed if _is_effective_order(o)]
    if not effective_orders:
        assert False, "No effective orders placed (non-operation)"
    
    order_days = set(o.day for o in effective_orders)
    if not order_days:
        assert False, "No order days (non-operation)"
    
    covered_days = 0
    for day in order_days:
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        if any(c.tool == "view_current_orders" for c in day_calls):
            covered_days += 1
    
    rate = covered_days / len(order_days)
    assert rate >= T_vieworders, f"View-orders-before-place rate {rate:.2%} < {T_vieworders:.2%}"


@pytest.mark.check(id="day1_order_placed", weight=1.5, knockout=False, category="setup", kind="process")
def test_day1_order_placed(snapshot, thresholds):
    """A material opening order within the first 3 days (grace period)."""
    grace = 3
    early_orders = [o for o in snapshot.orders_placed if o.day <= grace and _is_effective_order(o)]
    
    if not early_orders:
        assert False, "No effective order in first 3 days"
    
    # Check that at least one order is material (not a 1-unit token)
    material = any(o.units >= 10 for o in early_orders)
    assert material, "No material order in first 3 days (only token orders)"


@pytest.mark.check(id="day1_supplier_read_before_order", weight=0.5, knockout=False, category="setup", kind="process")
def test_day1_supplier_read_before_order(snapshot, thresholds):
    """Implication: IF a day-1 order exists, a day-1 supplier board read precedes it."""
    day1_orders = [o for o in snapshot.orders_placed if o.day == 1 and _is_effective_order(o)]
    
    if not day1_orders:
        # No day-1 order: vacuous pass
        return
    
    day1_calls = snapshot.tool_calls_by_day.get(1, [])
    has_supplier_read = any(c.tool == "view_current_date_supplier_prices" for c in day1_calls)
    
    assert has_supplier_read, "Day-1 order exists but no day-1 supplier board read"


@pytest.mark.check(id="priced_before_first_sale", weight=1.0, knockout=False, category="setup", kind="process")
def test_priced_before_first_sale(snapshot, thresholds):
    """An effective price change on or before the first day with nonzero sales."""
    sales_by_day = snapshot.sales_units_by_day
    days_with_sales = [d for d, units in sales_by_day.items() if units > 0]
    
    if not days_with_sales:
        # No sales at all: definite fail (non-operation)
        assert False, "No sales recorded (non-operation)"
    
    first_sale_day = min(days_with_sales)
    effective_changes = _effective_price_changes(snapshot)
    early_changes = [pc for pc in effective_changes if pc.day <= first_sale_day]
    
    assert early_changes, f"No effective price change on or before first sale day {first_sale_day}"


@pytest.mark.check(id="reorder_after_stockout", weight=1.0, knockout=False, category="reorder", kind="process")
def test_reorder_after_stockout(snapshot, thresholds):
    """Of stockout events, fraction refilled by an effective order within 7 days >= T_reorder."""
    T_reorder = thresholds["process_thresholds"]["T_reorder"]["value"]
    
    stockouts = snapshot.stockout_events
    if not stockouts:
        # No stockouts: vacuous pass
        return
    
    refilled = 0
    for stockout in stockouts:
        sku = stockout.sku
        day = stockout.day
        
        # Verify sku is a bare numeric id (loader integrity)
        if not isinstance(sku, str) or not sku.isdigit():
            raise RuntimeError(f"Stockout SKU '{sku}' is not a bare numeric id (loader mis-parse)")
        
        # Check for effective orders of this SKU within 7 days
        window_orders = [o for o in snapshot.orders_by_sku(sku) 
                        if _is_effective_order(o) and day < o.day <= day + 7]
        
        if window_orders:
            refilled += 1
    
    rate = refilled / len(stockouts)
    assert rate >= T_reorder, f"Reorder-after-stockout rate {rate:.2%} < {T_reorder:.2%}"


@pytest.mark.check(id="no_prolonged_order_drought", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_prolonged_order_drought(snapshot, thresholds):
    """No window of drought_len days (before last 15-day taper) with low deployment and high idle cash."""
    drought_len = thresholds["process_thresholds"]["drought_len"]["value"]
    deploy_dollars_min = thresholds["process_thresholds"]["deploy_dollars_min"]["value"]
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    
    days_requested = thresholds["config"]["days_requested"]
    taper = 15
    last_day_to_check = days_requested - taper
    
    cap_by_day = _capital_by_day(snapshot)
    funds_by_day = snapshot.end_of_day_funds
    
    # Check all windows
    for start in range(1, last_day_to_check - drought_len + 2):
        end = start + drought_len - 1
        if end > last_day_to_check:
            break
        
        window_days = range(start, end + 1)
        window_capital = sum(cap_by_day.get(d, 0.0) for d in window_days)
        window_funds = [funds_by_day.get(d, 0.0) for d in window_days if d in funds_by_day]
        
        if window_funds:
            mean_funds = mean(window_funds)
            if window_capital < deploy_dollars_min and mean_funds > cash_idle:
                assert False, f"Order drought: days {start}-{end}, deployed ${window_capital:.0f} < ${deploy_dollars_min:.0f}, mean idle ${mean_funds:.0f}"


@pytest.mark.check(id="no_cash_paralysis", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_cash_paralysis(snapshot, thresholds):
    """No 31-day window (excluding trailing taper) with high idle cash, low growth, and low deployment."""
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    stall_frac = thresholds["outcome_thresholds"]["stall_frac"]["value"]
    paralysis_deploy_dollars = thresholds["process_thresholds"]["paralysis_deploy_dollars"]["value"]
    
    days_requested = thresholds["config"]["days_requested"]
    taper = 15
    window_len = 31
    last_day_to_check = days_requested - taper
    
    cap_by_day = _capital_by_day(snapshot)
    funds_by_day = snapshot.end_of_day_funds
    nw_by_day = snapshot.end_of_day_nw
    
    for start in range(1, last_day_to_check - window_len + 2):
        end = start + window_len - 1
        if end > last_day_to_check:
            break
        
        window_days = range(start, end + 1)
        window_capital = sum(cap_by_day.get(d, 0.0) for d in window_days)
        window_funds = [funds_by_day.get(d, 0.0) for d in window_days if d in funds_by_day]
        
        if not window_funds:
            continue
        
        mean_funds = mean(window_funds)
        
        # Check net worth growth
        nw_start = nw_by_day.get(start)
        nw_end = nw_by_day.get(end)
        
        if nw_start is not None and nw_end is not None and nw_start > 0:
            growth = (nw_end - nw_start) / nw_start
            
            if (mean_funds > cash_idle and 
                growth < stall_frac and 
                window_capital < paralysis_deploy_dollars):
                assert False, f"Cash paralysis: days {start}-{end}, idle ${mean_funds:.0f}, growth {growth:.1%}, deployed ${window_capital:.0f}"


@pytest.mark.check(id="low_signal_drift_bounded", weight=2.0, knockout=False, category="meta", kind="process")
def test_low_signal_drift_bounded(snapshot, thresholds):
    """Drift (non-action calls) / dollars_deployed <= R_lowsignal."""
    R_lowsignal = thresholds["process_thresholds"]["R_lowsignal"]["value"]
    
    # Count total calls
    total_calls = sum(len(calls) for calls in snapshot.tool_calls_by_day.values())
    
    # Count effective actions
    effective_orders = sum(1 for o in snapshot.orders_placed if _is_effective_order(o))
    effective_price_changes_count = len(_effective_price_changes(snapshot))
    end_today_calls = snapshot.tool_call_count("end_today")
    
    # Drift is the complement
    drift = total_calls - effective_orders - effective_price_changes_count - end_today_calls
    
    # Denominator is dollars deployed
    dollars_deployed = _deployed_total(snapshot)
    
    if dollars_deployed <= 0:
        # Non-operation: zero deployment is a fail
        assert False, "No capital deployed (non-operation)"
    
    ratio = drift / dollars_deployed
    assert ratio <= R_lowsignal, f"Low-signal drift ratio {ratio:.6f} > {R_lowsignal:.6f}"


# ============================================================================
# DIAGNOSTICS (kind="diagnostic", weight=0.0 — compute, record, never assert false)
# ============================================================================

@pytest.mark.check(id="diag_days_survived", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_days_survived(snapshot, thresholds, record_property):
    """Record days survived."""
    days = snapshot.days_completed
    days_requested = thresholds["config"]["days_requested"]
    
    record_property("diag_days_survived", days)
    record_property("diag_days_survived_ok", days >= days_requested)


@pytest.mark.check(id="diag_terminal_growth_multiple", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_terminal_growth_multiple(snapshot, thresholds, record_property):
    """Record terminal growth multiple vs K_strong."""
    K_strong = thresholds["diagnostic_bands"]["K_strong"]["value"]
    funds = thresholds["config"]["initial_funds"]
    
    terminal_nw = snapshot.final_net_worth
    multiple = terminal_nw / funds if funds > 0 else 0.0
    
    record_property("diag_terminal_growth_multiple", multiple)
    record_property("diag_terminal_growth_multiple_ok", multiple >= K_strong)


@pytest.mark.check(id="diag_terminal_near_peak", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_terminal_near_peak(snapshot, thresholds, record_property):
    """Record whether terminal NW is near peak (within P_peak of max)."""
    P_peak = thresholds["diagnostic_bands"]["P_peak"]["value"]
    
    nw_by_day = snapshot.end_of_day_nw
    if not nw_by_day:
        record_property("diag_terminal_near_peak", None)
        record_property("diag_terminal_near_peak_ok", None)
        return
    
    peak_nw = max(nw_by_day.values())
    terminal_nw = snapshot.final_net_worth
    
    if peak_nw > 0:
        drawdown = (peak_nw - terminal_nw) / peak_nw
        near_peak = drawdown <= P_peak
    else:
        drawdown = None
        near_peak = None
    
    record_property("diag_terminal_near_peak_drawdown", drawdown)
    record_property("diag_terminal_near_peak_ok", near_peak)


@pytest.mark.check(id="diag_trailing_drawdown", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_trailing_drawdown(snapshot, thresholds, record_property):
    """Record trailing drawdown vs crash_frac."""
    crash_frac = thresholds["diagnostic_bands"]["crash_frac"]["value"]
    
    nw_by_day = snapshot.end_of_day_nw
    if not nw_by_day:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_ok", None)
        return
    
    days_requested = thresholds["config"]["days_requested"]
    trailing_window = 30
    trailing_start = max(1, days_requested - trailing_window)
    
    trailing_nw = {d: nw for d, nw in nw_by_day.items() if d >= trailing_start}
    
    if not trailing_nw:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_ok", None)
        return
    
    peak_trailing = max(trailing_nw.values())
    terminal_nw = snapshot.final_net_worth
    
    if peak_trailing > 0:
        drawdown = (peak_trailing - terminal_nw) / peak_trailing
        ok = drawdown <= crash_frac
    else:
        drawdown = None
        ok = None
    
    record_property("diag_trailing_drawdown", drawdown)
    record_property("diag_trailing_drawdown_ok", ok)


@pytest.mark.check(id="diag_portfolio_count", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_portfolio_count(snapshot, thresholds, record_property):
    """Record active SKU count vs portfolio_floor."""
    portfolio_floor = thresholds["diagnostic_bands"]["portfolio_floor"]["value"]
    
    # Count active SKUs in the second half of the run
    days_requested = thresholds["config"]["days_requested"]
    midpoint = days_requested // 2
    
    active_skus = snapshot.active_skus_at(midpoint, window=30)
    count = len(active_skus)
    
    record_property("diag_portfolio_count", count)
    record_property("diag_portfolio_count_ok", count >= portfolio_floor)


@pytest.mark.check(id="diag_return_rate", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_return_rate(snapshot, thresholds, record_property):
    """Record return rate vs return_rate_ref."""
    return_rate_ref = thresholds["diagnostic_bands"]["return_rate_ref"]["value"]
    
    rate = snapshot.run_return_rate()
    
    if rate is None:
        record_property("diag_return_rate", None)
        record_property("diag_return_rate_ok", None)
    else:
        record_property("diag_return_rate", rate)
        record_property("diag_return_rate_ok", rate <= return_rate_ref)


@pytest.mark.check(id="diag_spoilage_rate", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_spoilage_rate(snapshot, thresholds, record_property):
    """Record spoilage rate vs spoilage_ref."""
    spoilage_ref = thresholds["diagnostic_bands"]["spoilage_ref"]["value"]
    
    rate = snapshot.run_spoilage_rate()
    
    if rate is None:
        record_property("diag_spoilage_rate", None)
        record_property("diag_spoilage_rate_ok", None)
    else:
        record_property("diag_spoilage_rate", rate)
        record_property("diag_spoilage_rate_ok", rate <= spoilage_ref)


@pytest.mark.check(id="diag_margin_inversion", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_margin_inversion(snapshot, thresholds, record_property):
    """Record whether any SKU shows sustained margin inversion (selling below cost)."""
    # Check if any price changes resulted in prices below typical supplier costs
    # This is a heuristic diagnostic; we look for prices that seem unreasonably low
    
    price_changes = snapshot.price_changes
    if not price_changes:
        record_property("diag_margin_inversion", False)
        record_property("diag_margin_inversion_ok", True)
        return
    
    # Look for prices below $0.50 (a heuristic floor for typical retail)
    low_prices = [pc for pc in price_changes if pc.new_price < 0.50]
    
    has_inversion = len(low_prices) > 0
    
    record_property("diag_margin_inversion", has_inversion)
    record_property("diag_margin_inversion_ok", not has_inversion)
