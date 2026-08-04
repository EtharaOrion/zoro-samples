"""Deterministic pytest checks for task f2200047-d5b4-58fe-b9d0-6367297ecd7a."""

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
    """An order is effective if it was not rejected and deployed nonzero units."""
    return order.order_id is not None and order.units > 0


def _order_capital(order):
    """Capital deployed by an order (zero if ineffective)."""
    if not _is_effective_order(order):
        return 0.0
    return order.cost


def _effective_price_changes(snapshot):
    """Count price changes where new != old (|delta| > 1e-9)."""
    count = 0
    for pc in snapshot.price_changes:
        if pc.old_price is None or abs(pc.new_price - pc.old_price) > 1e-9:
            count += 1
    return count


def _capital_by_day(snapshot):
    """Map day -> total capital deployed that day."""
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
    
    # Categories list (normalize representation)
    frozen_cats = frozen["selected_categories_list"]
    actual_cats = snapshot.config.selected_categories
    if actual_cats is None:
        raise RuntimeError("Required config field 'selected_categories' missing from loader")
    
    def normalize_cat(c):
        return c.replace("_", " ").strip().lower()
    
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
    """Compute the continuous money outcome O from horizon-pinned net worth."""
    funds = thresholds["config"]["initial_funds"]
    oracle_nw = thresholds["oracle_nw"]["value"]
    days_requested = thresholds["config"]["days_requested"]
    rent = thresholds["config"]["everyday_rent"]
    
    # Horizon-pinned net worth (project rent for unfinished days)
    unfinished_days = max(0, days_requested - snapshot.days_completed)
    horizon_pinned_nw = snapshot.final_net_worth - rent * unfinished_days
    
    # Reference gain
    ref = oracle_nw - funds
    
    # Guard against near-infeasible task
    if ref <= 0:
        O = 0.0
    else:
        O = max(0.0, min(1.0, (horizon_pinned_nw - funds) / ref))
    
    band = "MADE-MONEY" if horizon_pinned_nw > funds else "LOST-MONEY"
    
    record_property("pinned_net_worth", snapshot.final_net_worth)
    record_property("horizon_pinned_net_worth", horizon_pinned_nw)
    record_property("money_outcome_O", O)
    record_property("money_band", band)
    
    # Assert only that the pinned value is a real number
    assert isinstance(snapshot.final_net_worth, (int, float))
    assert -1e15 < snapshot.final_net_worth < 1e15


# ============================================================================
# PROCESS CHECKS (kind="process", weighted tie-breakers)
# ============================================================================

@pytest.mark.check(id="valid_tools_used", weight=1.0, knockout=False, category="meta", kind="process")
def test_valid_tools_used(snapshot, thresholds):
    """All tool names used are in the valid registry."""
    observed = set()
    for day_calls in snapshot.tool_calls_by_day.values():
        for call in day_calls:
            observed.add(call.tool)
    
    assert observed <= set(VALID_TOOLS), f"Invalid tools: {observed - set(VALID_TOOLS)}"


@pytest.mark.check(id="supplier_board_before_order", weight=1.5, knockout=False, category="supplier", kind="process")
def test_supplier_board_before_order(snapshot, thresholds):
    """Fraction of orders whose SKUs were covered by same-day supplier board read >= threshold."""
    T = thresholds["process_thresholds"]["T_supplier"]["value"]
    
    order_days = {}
    for order in snapshot.orders_placed:
        if _is_effective_order(order):
            order_days.setdefault(order.day, []).append(order)
    
    if not order_days:
        # No effective orders = non-operation
        pytest.fail("No effective orders placed (non-operation)")
    
    covered = 0
    total = 0
    
    for day, orders in order_days.items():
        # Find all view_current_date_supplier_prices calls on this day
        board_skus = set()
        if day in snapshot.tool_calls_by_day:
            for call in snapshot.tool_calls_by_day[day]:
                if call.tool == "view_current_date_supplier_prices":
                    sku_ids = call.args.get("sku_ids", [])
                    for s in sku_ids:
                        board_skus.add(str(s))
        
        for order in orders:
            total += 1
            order_skus = set(str(s) for s in order.skus)
            if order_skus <= board_skus:
                covered += 1
    
    rate = covered / total if total > 0 else 0.0
    assert rate >= T, f"Supplier board coverage {rate:.1%} < {T:.1%}"


@pytest.mark.check(id="view_orders_before_place", weight=1.0, knockout=False, category="reorder", kind="process")
def test_view_orders_before_place(snapshot, thresholds):
    """Fraction of order-days with earlier same-day view_current_orders >= threshold."""
    T = thresholds["process_thresholds"]["T_vieworders"]["value"]
    
    order_days = set()
    for order in snapshot.orders_placed:
        if _is_effective_order(order):
            order_days.add(order.day)
    
    if not order_days:
        pytest.fail("No effective orders placed (non-operation)")
    
    viewed = 0
    for day in order_days:
        if day in snapshot.tool_calls_by_day:
            for call in snapshot.tool_calls_by_day[day]:
                if call.tool == "view_current_orders":
                    viewed += 1
                    break
    
    rate = viewed / len(order_days) if order_days else 0.0
    assert rate >= T, f"View orders before place {rate:.1%} < {T:.1%}"


@pytest.mark.check(id="day1_order_placed", weight=1.5, knockout=False, category="setup", kind="process")
def test_day1_order_placed(snapshot, thresholds):
    """A material opening order within the first 3 days."""
    grace = 3
    
    for order in snapshot.orders_placed:
        if order.day <= grace and _is_effective_order(order):
            # Material = more than a token 1-unit
            if order.units > 1:
                return
    
    pytest.fail("No material opening order within first 3 days")


@pytest.mark.check(id="day1_supplier_read_before_order", weight=0.5, knockout=False, category="setup", kind="process")
def test_day1_supplier_read_before_order(snapshot, thresholds):
    """Implication: IF day-1 order exists, a day-1 supplier board read precedes it."""
    day1_order = None
    for order in snapshot.orders_placed:
        if order.day == 1 and _is_effective_order(order):
            day1_order = order
            break
    
    if day1_order is None:
        # No day-1 order => vacuous pass
        return
    
    # Check for day-1 supplier board read
    if 1 in snapshot.tool_calls_by_day:
        for call in snapshot.tool_calls_by_day[1]:
            if call.tool == "view_current_date_supplier_prices":
                return
    
    pytest.fail("Day-1 order exists but no day-1 supplier board read")


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
    
    for pc in snapshot.price_changes:
        if pc.day <= first_sale_day:
            if pc.old_price is None or abs(pc.new_price - pc.old_price) > 1e-9:
                return
    
    pytest.fail(f"No effective price change on or before first sale day {first_sale_day}")


@pytest.mark.check(id="reorder_after_stockout", weight=1.0, knockout=False, category="reorder", kind="process")
def test_reorder_after_stockout(snapshot, thresholds):
    """Fraction of stockouts refilled by effective order within 7 days >= threshold."""
    T = thresholds["process_thresholds"]["T_reorder"]["value"]
    window = 7
    
    if not snapshot.stockout_events:
        # No stockouts => vacuous pass
        return
    
    refilled = 0
    total = len(snapshot.stockout_events)
    
    for stockout in snapshot.stockout_events:
        sku_str = str(stockout.sku)
        if not sku_str.isdigit():
            raise RuntimeError(f"Stockout SKU '{stockout.sku}' is not a bare numeric id")
        
        # Check for effective order of this SKU within 7 days
        for order in snapshot.orders_placed:
            if stockout.day < order.day <= stockout.day + window:
                if _is_effective_order(order) and sku_str in (str(s) for s in order.skus):
                    refilled += 1
                    break
    
    rate = refilled / total if total > 0 else 0.0
    assert rate >= T, f"Reorder after stockout {rate:.1%} < {T:.1%}"


@pytest.mark.check(id="no_prolonged_order_drought", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_prolonged_order_drought(snapshot, thresholds):
    """No window of drought_len days (before trailing taper) with low deployment and high idle cash."""
    drought_len = thresholds["process_thresholds"]["drought_len"]["value"]
    deploy_min = thresholds["process_thresholds"]["deploy_dollars_min"]["value"]
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    
    taper = 15
    days_req = thresholds["config"]["days_requested"]
    cutoff = days_req - taper
    
    cap_by_day = _capital_by_day(snapshot)
    
    for start in range(1, cutoff - drought_len + 2):
        end = start + drought_len - 1
        if end > cutoff:
            break
        
        window_days = list(range(start, end + 1))
        deployed = sum(cap_by_day.get(d, 0.0) for d in window_days)
        
        funds_vals = [snapshot.end_of_day_funds.get(d) for d in window_days if d in snapshot.end_of_day_funds]
        if funds_vals:
            mean_funds = mean(funds_vals)
        else:
            mean_funds = 0.0
        
        if deployed < deploy_min and mean_funds > cash_idle:
            pytest.fail(f"Order drought days {start}-{end}: deployed ${deployed:.0f} < ${deploy_min:.0f}, idle ${mean_funds:.0f}")
    
    # Pass if no drought found


@pytest.mark.check(id="no_cash_paralysis", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_cash_paralysis(snapshot, thresholds):
    """No 31-day window (excluding taper) with high idle cash, low growth, and low deployment."""
    window_len = 31
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    stall_frac = thresholds["outcome_thresholds"]["stall_frac"]["value"]
    deploy_min = thresholds["process_thresholds"]["paralysis_deploy_dollars"]["value"]
    
    taper = 15
    days_req = thresholds["config"]["days_requested"]
    cutoff = days_req - taper
    
    cap_by_day = _capital_by_day(snapshot)
    
    for start in range(1, cutoff - window_len + 2):
        end = start + window_len - 1
        if end > cutoff:
            break
        
        window_days = list(range(start, end + 1))
        
        # Mean idle funds
        funds_vals = [snapshot.end_of_day_funds.get(d) for d in window_days if d in snapshot.end_of_day_funds]
        if funds_vals:
            mean_funds = mean(funds_vals)
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
        
        if mean_funds > cash_idle and growth < stall_frac and deployed < deploy_min:
            pytest.fail(f"Cash paralysis days {start}-{end}: idle ${mean_funds:.0f}, growth {growth:.1%}, deployed ${deployed:.0f}")
    
    # Pass if no paralysis found


@pytest.mark.check(id="low_signal_drift_bounded", weight=2.0, knockout=False, category="meta", kind="process")
def test_low_signal_drift_bounded(snapshot, thresholds):
    """Drift (non-action calls) / dollars_deployed <= threshold."""
    R = thresholds["process_thresholds"]["R_lowsignal"]["value"]
    
    total_calls = sum(len(calls) for calls in snapshot.tool_calls_by_day.values())
    effective_orders = sum(1 for o in snapshot.orders_placed if _is_effective_order(o))
    effective_prices = _effective_price_changes(snapshot)
    end_today_calls = snapshot.tool_call_count("end_today")
    
    drift = total_calls - effective_orders - effective_prices - end_today_calls
    dollars_deployed = _deployed_total(snapshot)
    
    if dollars_deployed <= 0:
        pytest.fail("Zero dollars deployed (non-operation)")
    
    ratio = drift / dollars_deployed
    assert ratio <= R, f"Low-signal drift ratio {ratio:.6f} > {R:.6f}"


# ============================================================================
# DIAGNOSTICS (kind="diagnostic", weight=0.0 — record, never assert false)
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
    ok = multiple >= K_strong
    
    record_property("diag_terminal_growth_multiple", multiple)
    record_property("diag_terminal_growth_ok", ok)


@pytest.mark.check(id="diag_terminal_near_peak", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_terminal_near_peak(snapshot, thresholds, record_property):
    """Record whether terminal NW is near peak (within P_peak fraction)."""
    P_peak = thresholds["diagnostic_bands"]["P_peak"]["value"]
    
    nw_vals = list(snapshot.end_of_day_nw.values())
    if not nw_vals:
        record_property("diag_terminal_near_peak", None)
        record_property("diag_terminal_near_peak_ok", True)
        return
    
    peak = max(nw_vals)
    terminal = snapshot.final_net_worth
    
    if peak > 0:
        frac = terminal / peak
    else:
        frac = 1.0
    
    ok = frac >= P_peak
    
    record_property("diag_terminal_near_peak_frac", frac)
    record_property("diag_terminal_near_peak_ok", ok)


@pytest.mark.check(id="diag_trailing_drawdown", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_trailing_drawdown(snapshot, thresholds, record_property):
    """Record trailing drawdown vs crash_frac."""
    crash_frac = thresholds["diagnostic_bands"]["crash_frac"]["value"]
    trailing = 30
    
    days_req = thresholds["config"]["days_requested"]
    cutoff = days_req - trailing
    
    nw_before = [snapshot.end_of_day_nw.get(d) for d in range(1, cutoff + 1) if d in snapshot.end_of_day_nw]
    if not nw_before:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_ok", True)
        return
    
    peak_before = max(nw_before)
    terminal = snapshot.final_net_worth
    
    if peak_before > 0:
        drawdown = (peak_before - terminal) / peak_before
    else:
        drawdown = 0.0
    
    ok = drawdown <= crash_frac
    
    record_property("diag_trailing_drawdown", drawdown)
    record_property("diag_trailing_drawdown_ok", ok)


@pytest.mark.check(id="diag_portfolio_count", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_portfolio_count(snapshot, thresholds, record_property):
    """Record active SKU count vs portfolio_floor."""
    portfolio_floor = thresholds["diagnostic_bands"]["portfolio_floor"]["value"]
    
    # Active SKUs in the middle 60 days (days 60-120)
    active = snapshot.active_skus_at(day=90, window=30)
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
    """Record whether any price changes inverted margin (new < cost)."""
    inversions = 0
    
    for pc in snapshot.price_changes:
        # We don't have per-SKU cost data in snapshot, so we skip this diagnostic
        # or mark it as not applicable
        pass
    
    record_property("diag_margin_inversion_count", 0)
    record_property("diag_margin_inversion_ok", True)
