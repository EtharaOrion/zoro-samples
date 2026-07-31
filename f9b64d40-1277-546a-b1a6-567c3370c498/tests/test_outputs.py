"""Deterministic pytest layer for task f9b64d40-1277-546a-b1a6-567c3370c498."""

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
    """Count price changes where new != old (beyond floating noise)."""
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
            cap[order.day] = cap.get(order.day, 0.0) + order.cost
    return cap


def _deployed_total(snapshot):
    """Total capital deployed across all effective orders."""
    return sum(_order_capital(o) for o in snapshot.orders_placed)


@pytest.mark.check(id="integrity_config_matches_frozen_task", weight=0.0, knockout=False, category="integrity", kind="outcome")
def test_integrity_config_matches_frozen_task(snapshot, thresholds):
    """Verify the run's config matches the frozen task definition."""
    frozen = thresholds["config"]
    
    # Scalar fields
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
    
    assert snapshot.config.initial_funds == frozen["initial_funds"], "initial_funds mismatch"
    assert snapshot.config.everyday_rent == frozen["everyday_rent"], "everyday_rent mismatch"
    assert snapshot.config.inventory_capacity == frozen["inventory_capacity"], "inventory_capacity mismatch"
    assert snapshot.config.global_random_seed == frozen["global_random_seed"], "global_random_seed mismatch"
    assert snapshot.config.enable_review == frozen["enable_review"], "enable_review mismatch"
    assert snapshot.config.enable_new == frozen["enable_new"], "enable_new mismatch"
    
    # Categories: compare representation-normalized lists
    if not hasattr(snapshot.config, "selected_categories"):
        raise RuntimeError("Loader did not surface config.selected_categories")
    frozen_cats = frozen["selected_categories_list"]
    observed_cats = snapshot.config.selected_categories
    
    def normalize(cat):
        return cat.replace("_", " ").strip().lower()
    
    frozen_norm = sorted(normalize(c) for c in frozen_cats)
    observed_norm = sorted(normalize(c) for c in observed_cats)
    
    assert observed_norm == frozen_norm, f"selected_categories mismatch: {observed_cats} vs {frozen_cats}"


@pytest.mark.check(id="integrity_readable_complete", weight=0.0, knockout=False, category="integrity", kind="outcome")
def test_integrity_readable_complete(snapshot, thresholds):
    """Verify the trajectory parsed and the terminal net worth is a real number."""
    nw = snapshot.final_net_worth
    if not isinstance(nw, (int, float)):
        raise RuntimeError(f"Terminal net worth is not numeric: {nw}")
    if nw != nw:  # NaN check
        raise RuntimeError("Terminal net worth is NaN")
    if nw == float('inf') or nw == float('-inf'):
        raise RuntimeError("Terminal net worth is infinite")


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
    assert snapshot.final_net_worth == snapshot.final_net_worth  # not NaN


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
    """Fraction of orders whose SKUs were covered by a same-day supplier-board read."""
    T = thresholds["process_thresholds"]["T_supplier"]["value"]
    
    effective_orders = [o for o in snapshot.orders_placed if _is_effective_order(o)]
    if not effective_orders:
        pytest.fail("No effective orders placed (non-operation)")
    
    covered = 0
    for order in effective_orders:
        day = order.day
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        
        # Find all view_current_date_supplier_prices calls before this order
        board_skus = set()
        for call in day_calls:
            if call.tool == "view_current_date_supplier_prices":
                sku_ids = call.args.get("sku_ids", [])
                for sid in sku_ids:
                    board_skus.add(str(sid))
        
        # Check if order SKUs are a subset of board SKUs
        order_skus = set(str(s) for s in order.skus)
        if order_skus <= board_skus:
            covered += 1
    
    rate = covered / len(effective_orders)
    assert rate >= T, f"Supplier board coverage {rate:.2%} < {T:.2%}"


@pytest.mark.check(id="view_orders_before_place", weight=1.0, knockout=False, category="reorder", kind="process")
def test_view_orders_before_place(snapshot, thresholds):
    """Fraction of order-days with a same-day view_current_orders call."""
    T = thresholds["process_thresholds"]["T_vieworders"]["value"]
    
    order_days = set()
    for order in snapshot.orders_placed:
        if _is_effective_order(order):
            order_days.add(order.day)
    
    if not order_days:
        pytest.fail("No effective orders placed (non-operation)")
    
    viewed = 0
    for day in order_days:
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        if any(c.tool == "view_current_orders" for c in day_calls):
            viewed += 1
    
    rate = viewed / len(order_days)
    assert rate >= T, f"View-orders-before-place rate {rate:.2%} < {T:.2%}"


@pytest.mark.check(id="day1_order_placed", weight=1.5, knockout=False, category="setup", kind="process")
def test_day1_order_placed(snapshot, thresholds):
    """A material opening order within the first 3 days."""
    grace = 3
    early_orders = [o for o in snapshot.orders_placed if o.day <= grace and _is_effective_order(o)]
    
    assert early_orders, f"No effective order within first {grace} days"


@pytest.mark.check(id="day1_supplier_read_before_order", weight=0.5, knockout=False, category="setup", kind="process")
def test_day1_supplier_read_before_order(snapshot, thresholds):
    """If a day-1 order exists, a day-1 supplier-board read precedes it."""
    day1_orders = [o for o in snapshot.orders_placed if o.day == 1 and _is_effective_order(o)]
    
    if not day1_orders:
        # No day-1 order -> vacuous pass
        return
    
    day1_calls = snapshot.tool_calls_by_day.get(1, [])
    has_board_read = any(c.tool == "view_current_date_supplier_prices" for c in day1_calls)
    
    assert has_board_read, "Day-1 order exists but no day-1 supplier-board read"


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
    
    early_price_changes = [
        pc for pc in snapshot.price_changes
        if pc.day <= first_sale_day and (pc.old_price is None or abs(pc.new_price - pc.old_price) > 1e-9)
    ]
    
    assert early_price_changes, f"No effective price change on or before first sale day {first_sale_day}"


@pytest.mark.check(id="reorder_after_stockout", weight=1.0, knockout=False, category="reorder", kind="process")
def test_reorder_after_stockout(snapshot, thresholds):
    """Fraction of stockouts refilled by an effective order within 7 days."""
    T = thresholds["process_thresholds"]["T_reorder"]["value"]
    window = 7
    
    if not snapshot.stockout_events:
        # No stockouts -> vacuous pass
        return
    
    refilled = 0
    for stockout in snapshot.stockout_events:
        sku = stockout.sku
        if not sku.isdigit():
            raise RuntimeError(f"Stockout SKU is not a bare numeric id: {sku}")
        
        day = stockout.day
        # Find orders for this SKU within the next 7 days
        future_orders = [
            o for o in snapshot.orders_by_sku(sku)
            if day < o.day <= day + window and _is_effective_order(o)
        ]
        if future_orders:
            refilled += 1
    
    rate = refilled / len(snapshot.stockout_events)
    assert rate >= T, f"Reorder-after-stockout rate {rate:.2%} < {T:.2%}"


@pytest.mark.check(id="no_prolonged_order_drought", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_prolonged_order_drought(snapshot, thresholds):
    """No prolonged window with low capital deployed while idle cash is high."""
    drought_len = thresholds["process_thresholds"]["drought_len"]["value"]
    deploy_min = thresholds["process_thresholds"]["deploy_dollars_min"]["value"]
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    
    taper = 15
    horizon = snapshot.days_completed - taper
    
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
        
        if deployed < deploy_min and mean_funds > cash_idle:
            pytest.fail(f"Order drought: days {start}-{end}, deployed ${deployed:.0f} < ${deploy_min:.0f}, mean funds ${mean_funds:.0f}")


@pytest.mark.check(id="no_cash_paralysis", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_cash_paralysis(snapshot, thresholds):
    """No 31-day window with high idle cash, low growth, and low deployment."""
    window_len = 31
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    stall_frac = thresholds["outcome_thresholds"]["stall_frac"]["value"]
    deploy_min = thresholds["process_thresholds"]["paralysis_deploy_dollars"]["value"]
    
    taper = 15
    horizon = snapshot.days_completed - taper
    
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
        
        # Capital deployed
        deployed = sum(cap_by_day.get(d, 0.0) for d in window_days)
        
        if mean_funds > cash_idle and growth < stall_frac and deployed < deploy_min:
            pytest.fail(f"Cash paralysis: days {start}-{end}, mean funds ${mean_funds:.0f}, growth {growth:.2%}, deployed ${deployed:.0f}")


@pytest.mark.check(id="low_signal_drift_bounded", weight=2.0, knockout=False, category="meta", kind="process")
def test_low_signal_drift_bounded(snapshot, thresholds):
    """Low-signal drift (non-action calls) per dollar deployed is bounded."""
    R = thresholds["process_thresholds"]["R_lowsignal"]["value"]
    
    total_calls = sum(len(calls) for calls in snapshot.tool_calls_by_day.values())
    effective_orders = sum(1 for o in snapshot.orders_placed if _is_effective_order(o))
    effective_prices = _effective_price_changes(snapshot)
    end_today_calls = snapshot.tool_call_count("end_today")
    
    drift = total_calls - effective_orders - effective_prices - end_today_calls
    deployed = _deployed_total(snapshot)
    
    if deployed == 0:
        pytest.fail("Zero capital deployed (non-operation)")
    
    ratio = drift / deployed
    assert ratio <= R, f"Low-signal drift ratio {ratio:.6f} > {R:.6f}"


@pytest.mark.check(id="diag_days_survived", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_days_survived(snapshot, thresholds, record_property):
    """Record days survived."""
    record_property("diag_days_survived", snapshot.days_completed)


@pytest.mark.check(id="diag_terminal_growth_multiple", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_terminal_growth_multiple(snapshot, thresholds, record_property):
    """Record terminal growth multiple vs strong threshold."""
    K_strong = thresholds["diagnostic_bands"]["K_strong"]["value"]
    funds = thresholds["config"]["initial_funds"]
    
    multiple = snapshot.final_net_worth / funds if funds > 0 else 0.0
    ok = multiple >= K_strong
    
    record_property("diag_terminal_growth_multiple", multiple)
    record_property("diag_terminal_growth_ok", ok)


@pytest.mark.check(id="diag_terminal_near_peak", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_terminal_near_peak(snapshot, thresholds, record_property):
    """Record whether terminal NW is near peak (not a deep drawdown)."""
    P_peak = thresholds["diagnostic_bands"]["P_peak"]["value"]
    
    if not snapshot.end_of_day_nw:
        record_property("diag_terminal_near_peak", None)
        record_property("diag_terminal_near_peak_ok", True)
        return
    
    peak = max(snapshot.end_of_day_nw.values())
    terminal = snapshot.final_net_worth
    
    if peak > 0:
        ratio = terminal / peak
    else:
        ratio = 1.0
    
    ok = ratio >= P_peak
    
    record_property("diag_terminal_near_peak", ratio)
    record_property("diag_terminal_near_peak_ok", ok)


@pytest.mark.check(id="diag_trailing_drawdown", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_trailing_drawdown(snapshot, thresholds, record_property):
    """Record trailing drawdown in the final phase."""
    crash_frac = thresholds["diagnostic_bands"]["crash_frac"]["value"]
    window = 30
    
    if snapshot.days_completed < window:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_ok", True)
        return
    
    trailing_days = range(snapshot.days_completed - window + 1, snapshot.days_completed + 1)
    trailing_nw = [snapshot.end_of_day_nw.get(d) for d in trailing_days if d in snapshot.end_of_day_nw]
    
    if not trailing_nw:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_ok", True)
        return
    
    peak_trailing = max(trailing_nw)
    terminal = snapshot.final_net_worth
    
    if peak_trailing > 0:
        drawdown = (peak_trailing - terminal) / peak_trailing
    else:
        drawdown = 0.0
    
    ok = drawdown <= crash_frac
    
    record_property("diag_trailing_drawdown", drawdown)
    record_property("diag_trailing_drawdown_ok", ok)


@pytest.mark.check(id="diag_portfolio_count", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_portfolio_count(snapshot, thresholds, record_property):
    """Record active SKU count in the steady state."""
    portfolio_floor = thresholds["diagnostic_bands"]["portfolio_floor"]["value"]
    
    if snapshot.days_completed < 60:
        pytest.skip("Run too short for portfolio diagnostic")
    
    mid_day = snapshot.days_completed // 2
    active = snapshot.active_skus_at(mid_day, window=30)
    count = len(active)
    ok = count >= portfolio_floor
    
    record_property("diag_portfolio_count", count)
    record_property("diag_portfolio_count_ok", ok)


@pytest.mark.check(id="diag_return_rate", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_return_rate(snapshot, thresholds, record_property):
    """Record run-wide return rate."""
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
    """Record run-wide spoilage rate."""
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
    """Record whether the run shows margin inversion (selling below cost)."""
    # A margin inversion is when the run's terminal NW is below opening funds despite sales
    funds = thresholds["config"]["initial_funds"]
    terminal = snapshot.final_net_worth
    
    total_sales = sum(snapshot.sales_units_by_day.values())
    
    if total_sales == 0:
        # No sales -> no inversion to detect
        record_property("diag_margin_inversion", None)
        record_property("diag_margin_inversion_ok", True)
        return
    
    inverted = terminal < funds
    
    record_property("diag_margin_inversion", inverted)
    record_property("diag_margin_inversion_ok", not inverted)
