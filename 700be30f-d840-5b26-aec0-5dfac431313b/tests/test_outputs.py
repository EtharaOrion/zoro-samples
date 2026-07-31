"""Deterministic pytest layer for RetailBench task 700be30f-d840-5b26-aec0-5dfac431313b."""

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
    
    # Scalar fields
    assert snapshot.config.initial_funds == frozen["initial_funds"], "initial_funds mismatch"
    assert snapshot.config.everyday_rent == frozen["everyday_rent"], "everyday_rent mismatch"
    assert snapshot.config.inventory_capacity == frozen["inventory_capacity"], "inventory_capacity mismatch"
    assert snapshot.config.global_random_seed == frozen["global_random_seed"], "global_random_seed mismatch"
    assert snapshot.config.enable_review == frozen["enable_review"], "enable_review mismatch"
    assert snapshot.config.enable_new == frozen["enable_new"], "enable_new mismatch"
    
    # Categories list (representation-normalized)
    if not hasattr(snapshot.config, 'selected_categories'):
        raise RuntimeError("snapshot.config.selected_categories missing")
    
    frozen_cats = frozen["selected_categories_list"]
    run_cats = snapshot.config.selected_categories
    
    def normalize(s):
        return s.replace('_', ' ').strip().lower()
    
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
    """Compute the continuous money outcome O and record the band."""
    funds = thresholds["config"]["initial_funds"]
    oracle_nw = thresholds["oracle_nw"]["value"]
    days_requested = thresholds["config"]["days_requested"]
    rent = thresholds["config"]["everyday_rent"]
    
    # Horizon-pinned net worth
    unfinished_days = max(0, days_requested - snapshot.days_completed)
    horizon_pinned_nw = snapshot.final_net_worth - rent * unfinished_days
    
    # Reference gain
    ref = oracle_nw - funds
    
    # Guard against infeasible task
    if ref <= 0:
        O = 0.0
    else:
        gain = horizon_pinned_nw - funds
        O = max(0.0, min(1.0, gain / ref))
    
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
    """All tool names used are in the valid tool registry."""
    observed = set()
    for day_calls in snapshot.tool_calls_by_day.values():
        for call in day_calls:
            observed.add(call.tool)
    
    invalid = observed - set(VALID_TOOLS)
    assert not invalid, f"Invalid tools used: {invalid}"


@pytest.mark.check(id="supplier_board_before_order", weight=1.5, knockout=False, category="supplier", kind="process")
def test_supplier_board_before_order(snapshot, thresholds):
    """Of all place_order calls, the fraction whose ordered SKUs were covered by an earlier same-day view_current_date_supplier_prices >= threshold."""
    T = thresholds["process_thresholds"]["T_supplier"]["value"]
    
    order_calls = []
    for day, calls in snapshot.tool_calls_by_day.items():
        for call in calls:
            if call.tool == "place_order":
                order_calls.append((day, call))
    
    if not order_calls:
        # No orders placed = non-operation = definite FAIL
        assert False, "No orders placed (non-operation)"
    
    covered = 0
    for day, order_call in order_calls:
        # Extract ordered SKUs from the order call
        items = order_call.args.get("items", [])
        ordered_skus = set()
        for item in items:
            if isinstance(item, dict) and "sku_id" in item:
                ordered_skus.add(str(item["sku_id"]))
        
        if not ordered_skus:
            continue
        
        # Check if a same-day earlier view_current_date_supplier_prices covered these SKUs
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        for call in day_calls:
            if call.tool == "view_current_date_supplier_prices":
                read_skus = set(str(s) for s in call.args.get("sku_ids", []))
                if ordered_skus.issubset(read_skus):
                    covered += 1
                    break
    
    coverage = covered / len(order_calls)
    assert coverage >= T, f"Supplier board coverage {coverage:.2%} < {T:.2%}"


@pytest.mark.check(id="view_orders_before_place", weight=1.0, knockout=False, category="reorder", kind="process")
def test_view_orders_before_place(snapshot, thresholds):
    """Of order-days, the fraction with an earlier same-day view_current_orders >= threshold."""
    T = thresholds["process_thresholds"]["T_vieworders"]["value"]
    
    order_days = set()
    for day, calls in snapshot.tool_calls_by_day.items():
        for call in calls:
            if call.tool == "place_order":
                order_days.add(day)
    
    if not order_days:
        # No orders = non-operation = definite FAIL
        assert False, "No orders placed (non-operation)"
    
    covered = 0
    for day in order_days:
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        for call in day_calls:
            if call.tool == "view_current_orders":
                covered += 1
                break
    
    coverage = covered / len(order_days)
    assert coverage >= T, f"view_current_orders coverage {coverage:.2%} < {T:.2%}"


@pytest.mark.check(id="day1_order_placed", weight=1.5, knockout=False, category="setup", kind="process")
def test_day1_order_placed(snapshot, thresholds):
    """A material (effective) opening order within the first 3 days."""
    grace = 3
    
    for order in snapshot.orders_placed:
        if order.day <= grace and _is_effective_order(order):
            return
    
    assert False, f"No effective order placed within first {grace} days"


@pytest.mark.check(id="day1_supplier_read_before_order", weight=0.5, knockout=False, category="setup", kind="process")
def test_day1_supplier_read_before_order(snapshot, thresholds):
    """Implication: IF a day-1 order exists, a day-1 supplier-board read precedes it."""
    day1_order = None
    for order in snapshot.orders_placed:
        if order.day == 1 and _is_effective_order(order):
            day1_order = order
            break
    
    if day1_order is None:
        # No day-1 order = vacuous PASS
        return
    
    # Check for a day-1 view_current_date_supplier_prices
    day1_calls = snapshot.tool_calls_by_day.get(1, [])
    for call in day1_calls:
        if call.tool == "view_current_date_supplier_prices":
            return
    
    assert False, "Day-1 order exists but no day-1 supplier board read"


@pytest.mark.check(id="priced_before_first_sale", weight=1.0, knockout=False, category="setup", kind="process")
def test_priced_before_first_sale(snapshot, thresholds):
    """An EFFECTIVE price change on or before the first day with nonzero sales."""
    first_sale_day = None
    for day in sorted(snapshot.sales_units_by_day.keys()):
        if snapshot.sales_units_by_day[day] > 0:
            first_sale_day = day
            break
    
    if first_sale_day is None:
        # No sales at all = non-operation = definite FAIL
        assert False, "No sales recorded (non-operation)"
    
    effective_changes = _effective_price_changes(snapshot)
    for pc in effective_changes:
        if pc.day <= first_sale_day:
            return
    
    assert False, f"No effective price change on or before first sale day {first_sale_day}"


@pytest.mark.check(id="reorder_after_stockout", weight=1.0, knockout=False, category="reorder", kind="process")
def test_reorder_after_stockout(snapshot, thresholds):
    """Of stockout events, the fraction refilled by an effective order within 7 days >= threshold."""
    T = thresholds["process_thresholds"]["T_reorder"]["value"]
    window = 7
    
    if not snapshot.stockout_events:
        # No stockouts = vacuous PASS
        return
    
    refilled = 0
    for stockout in snapshot.stockout_events:
        # Verify sku is a bare numeric id
        if not isinstance(stockout.sku, str) or not stockout.sku.isdigit():
            raise RuntimeError(f"Stockout sku is not a bare numeric id: {stockout.sku}")
        
        sku = stockout.sku
        day = stockout.day
        
        # Check for an effective order of this SKU within 7 days
        for order in snapshot.orders_placed:
            if day < order.day <= day + window and _is_effective_order(order):
                if sku in order.skus:
                    refilled += 1
                    break
    
    coverage = refilled / len(snapshot.stockout_events)
    assert coverage >= T, f"Reorder-after-stockout coverage {coverage:.2%} < {T:.2%}"


@pytest.mark.check(id="no_prolonged_order_drought", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_prolonged_order_drought(snapshot, thresholds):
    """No window of drought_len days (before the last 15-day taper) with < deploy_dollars_min of capital deployed while mean idle funds > cash_idle."""
    drought_len = thresholds["process_thresholds"]["drought_len"]["value"]
    deploy_min = thresholds["process_thresholds"]["deploy_dollars_min"]["value"]
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    taper = 15
    
    days_requested = thresholds["config"]["days_requested"]
    cutoff = days_requested - taper
    
    capital_by_day = _capital_by_day(snapshot)
    
    for start in range(1, cutoff - drought_len + 2):
        end = start + drought_len - 1
        if end > cutoff:
            break
        
        window_days = range(start, end + 1)
        window_capital = sum(capital_by_day.get(d, 0.0) for d in window_days)
        window_funds = [snapshot.end_of_day_funds.get(d) for d in window_days if d in snapshot.end_of_day_funds]
        
        if window_funds:
            mean_funds = mean(window_funds)
            if window_capital < deploy_min and mean_funds > cash_idle:
                assert False, f"Order drought days {start}-{end}: ${window_capital:.2f} deployed < ${deploy_min:.2f}, mean idle ${mean_funds:.2f} > ${cash_idle:.2f}"


@pytest.mark.check(id="no_cash_paralysis", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_cash_paralysis(snapshot, thresholds):
    """No 31-day window (excluding trailing taper) where mean idle funds > cash_idle AND net-worth growth < stall_frac AND < paralysis_deploy_dollars of capital deployed."""
    window_len = 31
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    stall_frac = thresholds["outcome_thresholds"]["stall_frac"]["value"]
    paralysis_deploy = thresholds["process_thresholds"]["paralysis_deploy_dollars"]["value"]
    taper = 15
    
    days_requested = thresholds["config"]["days_requested"]
    cutoff = days_requested - taper
    
    capital_by_day = _capital_by_day(snapshot)
    
    for start in range(1, cutoff - window_len + 2):
        end = start + window_len - 1
        if end > cutoff:
            break
        
        window_days = range(start, end + 1)
        
        # Mean idle funds
        window_funds = [snapshot.end_of_day_funds.get(d) for d in window_days if d in snapshot.end_of_day_funds]
        if not window_funds:
            continue
        mean_funds = mean(window_funds)
        
        # Net worth growth
        nw_start = snapshot.end_of_day_nw.get(start)
        nw_end = snapshot.end_of_day_nw.get(end)
        if nw_start is None or nw_end is None or nw_start <= 0:
            continue
        growth = (nw_end - nw_start) / nw_start
        
        # Capital deployed
        window_capital = sum(capital_by_day.get(d, 0.0) for d in window_days)
        
        if mean_funds > cash_idle and growth < stall_frac and window_capital < paralysis_deploy:
            assert False, f"Cash paralysis days {start}-{end}: mean idle ${mean_funds:.2f}, growth {growth:.2%}, deployed ${window_capital:.2f}"


@pytest.mark.check(id="low_signal_drift_bounded", weight=2.0, knockout=False, category="meta", kind="process")
def test_low_signal_drift_bounded(snapshot, thresholds):
    """drift = total_calls - effective_orders - effective_price_changes - end_today_calls; ratio = drift / dollars_deployed; assert ratio <= R_lowsignal."""
    R = thresholds["process_thresholds"]["R_lowsignal"]["value"]
    
    total_calls = sum(len(calls) for calls in snapshot.tool_calls_by_day.values())
    
    effective_orders = sum(1 for o in snapshot.orders_placed if _is_effective_order(o))
    effective_price_changes_count = len(_effective_price_changes(snapshot))
    
    end_today_calls = sum(snapshot.tool_call_count("end_today") for _ in [None])
    end_today_calls = snapshot.tool_call_count("end_today")
    
    drift = total_calls - effective_orders - effective_price_changes_count - end_today_calls
    
    dollars_deployed = _deployed_total(snapshot)
    
    if dollars_deployed <= 0:
        # No capital deployed = non-operation = definite FAIL
        assert False, "No capital deployed (non-operation)"
    
    ratio = drift / dollars_deployed
    assert ratio <= R, f"Low-signal drift ratio {ratio:.6f} > {R:.6f} (drift={drift}, deployed=${dollars_deployed:.2f})"


# ============================================================================
# DIAGNOSTICS (kind="diagnostic", weight=0.0)
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
    
    nw = snapshot.final_net_worth
    multiple = nw / funds if funds > 0 else 0.0
    
    record_property("diag_terminal_growth_multiple", multiple)
    record_property("diag_terminal_growth_multiple_ok", multiple >= K_strong)


@pytest.mark.check(id="diag_terminal_near_peak", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_terminal_near_peak(snapshot, thresholds, record_property):
    """Record whether terminal NW is near peak (within P_peak fraction)."""
    P_peak = thresholds["diagnostic_bands"]["P_peak"]["value"]
    
    if not snapshot.end_of_day_nw:
        record_property("diag_terminal_near_peak", None)
        record_property("diag_terminal_near_peak_ok", True)
        return
    
    peak_nw = max(snapshot.end_of_day_nw.values())
    terminal_nw = snapshot.final_net_worth
    
    if peak_nw <= 0:
        record_property("diag_terminal_near_peak", None)
        record_property("diag_terminal_near_peak_ok", True)
        return
    
    ratio = terminal_nw / peak_nw
    near_peak = ratio >= (1 - P_peak)
    
    record_property("diag_terminal_near_peak", ratio)
    record_property("diag_terminal_near_peak_ok", near_peak)


@pytest.mark.check(id="diag_trailing_drawdown", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_trailing_drawdown(snapshot, thresholds, record_property):
    """Record trailing drawdown vs crash_frac."""
    crash_frac = thresholds["diagnostic_bands"]["crash_frac"]["value"]
    taper = 15
    
    days_requested = thresholds["config"]["days_requested"]
    cutoff = days_requested - taper
    
    if not snapshot.end_of_day_nw:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_ok", True)
        return
    
    pre_taper_days = [d for d in snapshot.end_of_day_nw.keys() if d <= cutoff]
    if not pre_taper_days:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_ok", True)
        return
    
    pre_taper_nw = max(snapshot.end_of_day_nw[d] for d in pre_taper_days)
    terminal_nw = snapshot.final_net_worth
    
    if pre_taper_nw <= 0:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_ok", True)
        return
    
    drawdown = (pre_taper_nw - terminal_nw) / pre_taper_nw
    ok = drawdown <= crash_frac
    
    record_property("diag_trailing_drawdown", drawdown)
    record_property("diag_trailing_drawdown_ok", ok)


@pytest.mark.check(id="diag_portfolio_count", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_portfolio_count(snapshot, thresholds, record_property):
    """Record active SKU count vs portfolio_floor."""
    portfolio_floor = thresholds["diagnostic_bands"]["portfolio_floor"]["value"]
    
    # Active SKUs at mid-run (day 90, 30-day window)
    mid_day = 90
    window = 30
    
    active = snapshot.active_skus_at(mid_day, window=window)
    count = len(active)
    ok = count >= portfolio_floor
    
    record_property("diag_portfolio_count", count)
    record_property("diag_portfolio_count_ok", ok)


@pytest.mark.check(id="diag_return_rate", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_return_rate(snapshot, thresholds, record_property):
    """Record return rate vs return_rate_ref."""
    return_rate_ref = thresholds["diagnostic_bands"]["return_rate_ref"]["value"]
    
    rate = snapshot.run_return_rate()
    
    if rate is None:
        record_property("diag_return_rate", None)
        record_property("diag_return_rate_ok", True)
        return
    
    ok = rate <= return_rate_ref
    record_property("diag_return_rate", rate)
    record_property("diag_return_rate_ok", ok)


@pytest.mark.check(id="diag_spoilage_rate", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_spoilage_rate(snapshot, thresholds, record_property):
    """Record spoilage rate vs spoilage_ref."""
    spoilage_ref = thresholds["diagnostic_bands"]["spoilage_ref"]["value"]
    
    rate = snapshot.run_spoilage_rate()
    
    if rate is None:
        record_property("diag_spoilage_rate", None)
        record_property("diag_spoilage_rate_ok", True)
        return
    
    ok = rate <= spoilage_ref
    record_property("diag_spoilage_rate", rate)
    record_property("diag_spoilage_rate_ok", ok)


@pytest.mark.check(id="diag_margin_inversion", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_margin_inversion(snapshot, thresholds, record_property):
    """Record whether any price changes inverted margin (new < buy cost)."""
    inversions = []
    
    for pc in snapshot.price_changes:
        # We don't have direct access to buy cost per SKU in the snapshot
        # This diagnostic is structural and would require additional data
        # For now, record None (data unavailable)
        pass
    
    # Data unavailable from snapshot API
    record_property("diag_margin_inversion", None)
    record_property("diag_margin_inversion_ok", True)
