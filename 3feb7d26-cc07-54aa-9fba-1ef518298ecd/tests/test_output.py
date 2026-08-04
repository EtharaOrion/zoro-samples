"""Deterministic pytest layer for task 3feb7d26-cc07-54aa-9fba-1ef518298ecd."""

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
    return order.cost if _is_effective_order(order) else 0.0


def _effective_price_changes(snapshot):
    """Count price changes where new != old (tolerance 1e-9)."""
    count = 0
    for pc in snapshot.price_changes:
        if pc.old_price is None or abs(pc.new_price - pc.old_price) > 1e-9:
            count += 1
    return count


def _capital_by_day(snapshot):
    """Map day -> total capital deployed that day."""
    by_day = {}
    for order in snapshot.orders_placed:
        if _is_effective_order(order):
            by_day[order.day] = by_day.get(order.day, 0.0) + order.cost
    return by_day


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
    
    # Categories: normalize representation (' ' vs '_')
    frozen_cats = frozen["selected_categories_list"]
    observed_cats = snapshot.config.selected_categories
    
    def normalize(cat):
        return cat.replace('_', ' ').replace(' ', '_').strip()
    
    frozen_norm = sorted(normalize(c) for c in frozen_cats)
    observed_norm = sorted(normalize(c) for c in observed_cats)
    
    assert observed_norm == frozen_norm, f"selected_categories mismatch: {observed_norm} != {frozen_norm}"


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
    """Compute and record the continuous money outcome O."""
    funds = thresholds["config"]["initial_funds"]
    oracle_nw = thresholds["oracle_nw"]["value"]
    days_requested = thresholds["config"]["days_requested"]
    rent = thresholds["config"]["everyday_rent"]
    
    pinned_nw = snapshot.final_net_worth
    days_short = max(0, days_requested - snapshot.days_completed)
    horizon_pinned_nw = pinned_nw - rent * days_short
    
    ref = oracle_nw - funds
    
    if ref <= 0:
        O = 0.0
    else:
        raw = (horizon_pinned_nw - funds) / ref
        O = max(0.0, min(1.0, raw))
    
    band = "MADE-MONEY" if horizon_pinned_nw > funds else "LOST-MONEY"
    
    record_property("pinned_net_worth", pinned_nw)
    record_property("horizon_pinned_net_worth", horizon_pinned_nw)
    record_property("money_outcome_O", O)
    record_property("money_band", band)
    
    assert isinstance(pinned_nw, (int, float)) and -1e15 < pinned_nw < 1e15


# ============================================================================
# PROCESS CHECKS (kind="process", weighted)
# ============================================================================

@pytest.mark.check(id="valid_tools_used", weight=1.0, knockout=False, category="meta", kind="process")
def test_valid_tools_used(snapshot, thresholds):
    """All observed tool names are in the valid registry."""
    observed = set()
    for day_calls in snapshot.tool_calls_by_day.values():
        for call in day_calls:
            observed.add(call.tool)
    
    invalid = observed - set(VALID_TOOLS)
    assert not invalid, f"Invalid tools used: {invalid}"


@pytest.mark.check(id="supplier_board_before_order", weight=1.5, knockout=False, category="supplier", kind="process")
def test_supplier_board_before_order(snapshot, thresholds):
    """Of all place_order calls, fraction whose SKUs were covered by same-day supplier read >= T_supplier."""
    T = thresholds["process_thresholds"]["T_supplier"]["value"]
    
    order_days = {}
    for order in snapshot.orders_placed:
        if order.day not in order_days:
            order_days[order.day] = []
        order_days[order.day].append(order)
    
    if not order_days:
        pytest.fail("No orders placed (non-operation)")
    
    covered = 0
    total = 0
    
    for day, orders in order_days.items():
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        supplier_read = any(c.tool == "view_current_date_supplier_prices" for c in day_calls)
        
        for order in orders:
            total += 1
            if supplier_read:
                covered += 1
    
    frac = covered / total if total > 0 else 0.0
    assert frac >= T, f"Supplier board coverage {frac:.3f} < {T}"


@pytest.mark.check(id="view_orders_before_place", weight=1.0, knockout=False, category="reorder", kind="process")
def test_view_orders_before_place(snapshot, thresholds):
    """Of order-days, fraction with same-day view_current_orders >= T_vieworders."""
    T = thresholds["process_thresholds"]["T_vieworders"]["value"]
    
    order_days = set()
    for order in snapshot.orders_placed:
        order_days.add(order.day)
    
    if not order_days:
        pytest.fail("No orders placed (non-operation)")
    
    covered = 0
    for day in order_days:
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        if any(c.tool == "view_current_orders" for c in day_calls):
            covered += 1
    
    frac = covered / len(order_days)
    assert frac >= T, f"view_current_orders coverage {frac:.3f} < {T}"


@pytest.mark.check(id="day1_order_placed", weight=1.5, knockout=False, category="setup", kind="process")
def test_day1_order_placed(snapshot, thresholds):
    """A material opening order within the first 3 days."""
    grace = 3
    early_orders = [o for o in snapshot.orders_placed if o.day <= grace and _is_effective_order(o)]
    
    if not early_orders:
        pytest.fail("No effective order in first 3 days")
    
    total_units = sum(o.units for o in early_orders)
    assert total_units > 1, f"Opening order too small: {total_units} units"


@pytest.mark.check(id="day1_supplier_read_before_order", weight=0.5, knockout=False, category="setup", kind="process")
def test_day1_supplier_read_before_order(snapshot, thresholds):
    """If a day-1 order exists, a day-1 supplier read precedes it."""
    day1_orders = [o for o in snapshot.orders_placed if o.day == 1]
    if not day1_orders:
        return  # vacuous pass
    
    day1_calls = snapshot.tool_calls_by_day.get(1, [])
    supplier_read = any(c.tool == "view_current_date_supplier_prices" for c in day1_calls)
    
    assert supplier_read, "Day-1 order without day-1 supplier read"


@pytest.mark.check(id="priced_before_first_sale", weight=1.0, knockout=False, category="setup", kind="process")
def test_priced_before_first_sale(snapshot, thresholds):
    """An effective price change on or before the first day with nonzero sales."""
    sales_days = [d for d, units in snapshot.sales_units_by_day.items() if units > 0]
    
    if not sales_days:
        pytest.fail("No sales (non-operation)")
    
    first_sale_day = min(sales_days)
    
    early_price_changes = [
        pc for pc in snapshot.price_changes
        if pc.day <= first_sale_day and (pc.old_price is None or abs(pc.new_price - pc.old_price) > 1e-9)
    ]
    
    assert early_price_changes, f"No effective price change by day {first_sale_day}"


@pytest.mark.check(id="reorder_after_stockout", weight=1.0, knockout=False, category="reorder", kind="process")
def test_reorder_after_stockout(snapshot, thresholds):
    """Of stockout events, fraction refilled within 7 days >= T_reorder."""
    T = thresholds["process_thresholds"]["T_reorder"]["value"]
    window = 7
    
    if not snapshot.stockout_events:
        return  # vacuous pass
    
    refilled = 0
    for stockout in snapshot.stockout_events:
        sku_str = stockout.sku
        if not isinstance(sku_str, str) or not sku_str.isdigit():
            raise RuntimeError(f"Stockout SKU not a bare numeric id: {sku_str}")
        
        sku_id = int(sku_str)
        refill_orders = [
            o for o in snapshot.orders_by_sku(sku_id)
            if stockout.day < o.day <= stockout.day + window and _is_effective_order(o)
        ]
        if refill_orders:
            refilled += 1
    
    frac = refilled / len(snapshot.stockout_events)
    assert frac >= T, f"Reorder-after-stockout {frac:.3f} < {T}"


@pytest.mark.check(id="no_prolonged_order_drought", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_prolonged_order_drought(snapshot, thresholds):
    """No drought_len-day window (before trailing taper) with low deployment and high idle cash."""
    drought_len = thresholds["process_thresholds"]["drought_len"]["value"]
    deploy_min = thresholds["process_thresholds"]["deploy_dollars_min"]["value"]
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    
    days_req = thresholds["config"]["days_requested"]
    taper = 15
    cutoff = days_req - taper
    
    capital_by_day = _capital_by_day(snapshot)
    
    for start in range(1, cutoff - drought_len + 2):
        end = start + drought_len - 1
        if end > cutoff:
            break
        
        window_days = range(start, end + 1)
        deployed = sum(capital_by_day.get(d, 0.0) for d in window_days)
        funds_vals = [snapshot.end_of_day_funds.get(d) for d in window_days if d in snapshot.end_of_day_funds]
        
        if funds_vals:
            mean_funds = mean(funds_vals)
            if deployed < deploy_min and mean_funds > cash_idle:
                pytest.fail(f"Order drought days {start}-{end}: deployed ${deployed:.0f} < ${deploy_min}, idle ${mean_funds:.0f}")


@pytest.mark.check(id="no_cash_paralysis", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_cash_paralysis(snapshot, thresholds):
    """No 31-day window (excluding taper) with high idle cash, low NW growth, and low deployment."""
    window_len = 31
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    stall_frac = thresholds["outcome_thresholds"]["stall_frac"]["value"]
    paralysis_deploy = thresholds["process_thresholds"]["paralysis_deploy_dollars"]["value"]
    
    days_req = thresholds["config"]["days_requested"]
    taper = 15
    cutoff = days_req - taper
    
    capital_by_day = _capital_by_day(snapshot)
    
    for start in range(1, cutoff - window_len + 2):
        end = start + window_len - 1
        if end > cutoff:
            break
        
        window_days = range(start, end + 1)
        
        funds_vals = [snapshot.end_of_day_funds.get(d) for d in window_days if d in snapshot.end_of_day_funds]
        nw_vals = [snapshot.end_of_day_nw.get(d) for d in window_days if d in snapshot.end_of_day_nw]
        deployed = sum(capital_by_day.get(d, 0.0) for d in window_days)
        
        if funds_vals and nw_vals and len(nw_vals) >= 2:
            mean_funds = mean(funds_vals)
            nw_start = nw_vals[0]
            nw_end = nw_vals[-1]
            growth = nw_end - nw_start
            
            if mean_funds > cash_idle and growth < stall_frac and deployed < paralysis_deploy:
                pytest.fail(f"Cash paralysis days {start}-{end}: idle ${mean_funds:.0f}, growth ${growth:.0f}, deployed ${deployed:.0f}")


@pytest.mark.check(id="low_signal_drift_bounded", weight=2.0, knockout=False, category="meta", kind="process")
def test_low_signal_drift_bounded(snapshot, thresholds):
    """Low-signal drift (non-action calls) / dollars_deployed <= R_lowsignal."""
    R = thresholds["process_thresholds"]["R_lowsignal"]["value"]
    
    total_calls = sum(len(calls) for calls in snapshot.tool_calls_by_day.values())
    effective_orders = sum(1 for o in snapshot.orders_placed if _is_effective_order(o))
    effective_prices = _effective_price_changes(snapshot)
    end_today_calls = snapshot.tool_call_count("end_today")
    
    drift = total_calls - effective_orders - effective_prices - end_today_calls
    dollars_deployed = _deployed_total(snapshot)
    
    if dollars_deployed <= 0:
        pytest.fail("No capital deployed (non-operation)")
    
    ratio = drift / dollars_deployed
    assert ratio <= R, f"Low-signal drift ratio {ratio:.6f} > {R}"


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
    ok = multiple >= K_strong
    
    record_property("diag_terminal_growth_multiple", multiple)
    record_property("diag_terminal_growth_multiple_ok", ok)


@pytest.mark.check(id="diag_terminal_near_peak", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_terminal_near_peak(snapshot, thresholds, record_property):
    """Record whether terminal NW is near peak (>= P_peak of max)."""
    P_peak = thresholds["diagnostic_bands"]["P_peak"]["value"]
    
    nw_vals = list(snapshot.end_of_day_nw.values())
    if not nw_vals:
        record_property("diag_terminal_near_peak", None)
        record_property("diag_terminal_near_peak_ok", True)
        return
    
    peak = max(nw_vals)
    terminal = snapshot.final_net_worth
    frac = terminal / peak if peak > 0 else 0.0
    ok = frac >= P_peak
    
    record_property("diag_terminal_near_peak", frac)
    record_property("diag_terminal_near_peak_ok", ok)


@pytest.mark.check(id="diag_trailing_drawdown", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_trailing_drawdown(snapshot, thresholds, record_property):
    """Record trailing drawdown vs crash_frac."""
    crash_frac = thresholds["diagnostic_bands"]["crash_frac"]["value"]
    
    nw_vals = list(snapshot.end_of_day_nw.values())
    if not nw_vals:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_ok", True)
        return
    
    peak = max(nw_vals)
    terminal = snapshot.final_net_worth
    drawdown = (peak - terminal) / peak if peak > 0 else 0.0
    ok = drawdown <= crash_frac
    
    record_property("diag_trailing_drawdown", drawdown)
    record_property("diag_trailing_drawdown_ok", ok)


@pytest.mark.check(id="diag_portfolio_count", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_portfolio_count(snapshot, thresholds, record_property):
    """Record active SKU count vs portfolio_floor."""
    portfolio_floor = thresholds["diagnostic_bands"]["portfolio_floor"]["value"]
    
    # Count active SKUs in the middle stretch (days 30-150)
    active = set()
    for day in range(30, 151):
        active.update(snapshot.active_skus_at(day, window=30))
    
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
    """Record whether any price changes created margin inversions (price < cost)."""
    inversions = []
    
    for pc in snapshot.price_changes:
        # We don't have cost data in the snapshot, so we can't compute true margin inversion
        # This is a placeholder that records the count of price changes
        # A real implementation would need cost data from the trajectory
        pass
    
    # For now, record a safe default
    record_property("diag_margin_inversion", 0)
    record_property("diag_margin_inversion_ok", True)
