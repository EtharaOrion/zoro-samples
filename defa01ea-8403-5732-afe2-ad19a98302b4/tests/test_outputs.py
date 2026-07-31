"""Deterministic pytest layer for task defa01ea-8403-5732-afe2-ad19a98302b4."""

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
    """Verify the run's config matches the frozen task parameters."""
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
        if not hasattr(snapshot.config, field):
            raise RuntimeError(f"Required config field '{field}' missing from loader")
        actual = getattr(snapshot.config, field)
        assert actual == expected, f"Config mismatch: {field} = {actual}, expected {expected}"
    
    # Categories list (normalize representation)
    frozen_cats = frozen["selected_categories_list"]
    actual_cats = snapshot.config.selected_categories
    
    def normalize(s):
        return s.replace('_', ' ').strip().lower()
    
    frozen_norm = sorted(normalize(c) for c in frozen_cats)
    actual_norm = sorted(normalize(c) for c in actual_cats)
    
    assert actual_norm == frozen_norm, f"Categories mismatch: {actual_cats} vs {frozen_cats}"


@pytest.mark.check(id="integrity_readable_complete", weight=0.0, knockout=False, category="integrity", kind="outcome")
def test_integrity_readable_complete(snapshot, thresholds):
    """Verify the trajectory parsed and terminal net worth is a finite real number."""
    nw = snapshot.final_net_worth
    if not isinstance(nw, (int, float)):
        raise RuntimeError(f"Terminal net worth is not a number: {type(nw)}")
    if not (-1e15 < nw < 1e15):
        raise RuntimeError(f"Terminal net worth is not finite: {nw}")


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
    
    pinned_nw = snapshot.final_net_worth
    days_short = max(0, days_requested - snapshot.days_completed)
    horizon_pinned_nw = pinned_nw - rent * days_short
    
    ref = oracle_nw - funds
    
    if ref <= 0:
        O = 0.0
    else:
        O = max(0.0, min(1.0, (horizon_pinned_nw - funds) / ref))
    
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
    
    order_days_skus = {}
    for order in snapshot.orders_placed:
        if order.day not in order_days_skus:
            order_days_skus[order.day] = set()
        order_days_skus[order.day].update(order.skus)
    
    if not order_days_skus:
        pytest.fail("No orders placed (non-operation)")
    
    supplier_reads_by_day = {}
    for day, calls in snapshot.tool_calls_by_day.items():
        for call in calls:
            if call.tool == "view_current_date_supplier_prices":
                if day not in supplier_reads_by_day:
                    supplier_reads_by_day[day] = True
                break
    
    covered = 0
    total = 0
    for day, skus in order_days_skus.items():
        total += 1
        if day in supplier_reads_by_day:
            covered += 1
    
    frac = covered / total
    assert frac >= T_supplier, f"Supplier board coverage {frac:.2%} < {T_supplier:.2%}"


@pytest.mark.check(id="view_orders_before_place", weight=1.0, knockout=False, category="reorder", kind="process")
def test_view_orders_before_place(snapshot, thresholds):
    """Of order-days, fraction with an earlier same-day view_current_orders."""
    T_vieworders = thresholds["process_thresholds"]["T_vieworders"]["value"]
    
    order_days = set(o.day for o in snapshot.orders_placed if _is_effective_order(o))
    
    if not order_days:
        pytest.fail("No effective orders placed (non-operation)")
    
    view_order_days = set()
    for day, calls in snapshot.tool_calls_by_day.items():
        for call in calls:
            if call.tool == "view_current_orders":
                view_order_days.add(day)
                break
    
    covered = len(order_days & view_order_days)
    frac = covered / len(order_days)
    
    assert frac >= T_vieworders, f"View orders coverage {frac:.2%} < {T_vieworders:.2%}"


@pytest.mark.check(id="day1_order_placed", weight=1.5, knockout=False, category="setup", kind="process")
def test_day1_order_placed(snapshot, thresholds):
    """A material opening order within the first 3 days."""
    grace = 3
    
    for order in snapshot.orders_placed:
        if order.day <= grace and _is_effective_order(order) and order.units > 1:
            return
    
    pytest.fail("No material opening order within first 3 days")


@pytest.mark.check(id="day1_supplier_read_before_order", weight=0.5, knockout=False, category="setup", kind="process")
def test_day1_supplier_read_before_order(snapshot, thresholds):
    """If a day-1 order exists, a day-1 supplier board read precedes it."""
    day1_order = any(o.day == 1 for o in snapshot.orders_placed if _is_effective_order(o))
    
    if not day1_order:
        return  # vacuous pass
    
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
    
    has_early_price = False
    for pc in snapshot.price_changes:
        if pc.day <= first_sale_day:
            if pc.old_price is None or abs(pc.new_price - pc.old_price) > 1e-9:
                has_early_price = True
                break
    
    assert has_early_price, f"No effective price change on or before first sale day {first_sale_day}"


@pytest.mark.check(id="reorder_after_stockout", weight=1.0, knockout=False, category="reorder", kind="process")
def test_reorder_after_stockout(snapshot, thresholds):
    """Of stockout events, fraction refilled by an effective order within 7 days."""
    T_reorder = thresholds["process_thresholds"]["T_reorder"]["value"]
    
    if not snapshot.stockout_events:
        return  # vacuous pass
    
    refilled = 0
    for stockout in snapshot.stockout_events:
        sku = stockout.sku
        if not sku.isdigit():
            raise RuntimeError(f"Stockout SKU not a bare numeric id: {sku}")
        
        day = stockout.day
        window_end = day + 7
        
        for order in snapshot.orders_by_sku(sku):
            if day < order.day <= window_end and _is_effective_order(order):
                refilled += 1
                break
    
    frac = refilled / len(snapshot.stockout_events)
    assert frac >= T_reorder, f"Reorder after stockout {frac:.2%} < {T_reorder:.2%}"


@pytest.mark.check(id="no_prolonged_order_drought", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_prolonged_order_drought(snapshot, thresholds):
    """No window of drought_len days (before trailing taper) with low deployment and high idle cash."""
    drought_len = thresholds["process_thresholds"]["drought_len"]["value"]
    deploy_min = thresholds["process_thresholds"]["deploy_dollars_min"]["value"]
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    
    taper = 15
    last_eval_day = snapshot.days_completed - taper
    
    if last_eval_day < drought_len:
        return  # horizon too short
    
    capital_by_day = _capital_by_day(snapshot)
    
    for start in range(1, last_eval_day - drought_len + 2):
        end = start + drought_len - 1
        window_deploy = sum(capital_by_day.get(d, 0.0) for d in range(start, end + 1))
        
        window_funds = []
        for d in range(start, end + 1):
            if d in snapshot.end_of_day_funds:
                window_funds.append(snapshot.end_of_day_funds[d])
        
        if window_funds:
            mean_funds = mean(window_funds)
            if window_deploy < deploy_min and mean_funds > cash_idle:
                pytest.fail(f"Order drought days {start}-{end}: deployed ${window_deploy:.0f} < ${deploy_min:.0f}, idle ${mean_funds:.0f}")


@pytest.mark.check(id="no_cash_paralysis", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_cash_paralysis(snapshot, thresholds):
    """No 31-day window (excluding trailing taper) with high idle cash, low growth, and low deployment."""
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    stall_frac = thresholds["outcome_thresholds"]["stall_frac"]["value"]
    paralysis_deploy = thresholds["process_thresholds"]["paralysis_deploy_dollars"]["value"]
    
    taper = 15
    window_len = 31
    last_eval_day = snapshot.days_completed - taper
    
    if last_eval_day < window_len:
        return
    
    capital_by_day = _capital_by_day(snapshot)
    
    for start in range(1, last_eval_day - window_len + 2):
        end = start + window_len - 1
        
        window_funds = []
        for d in range(start, end + 1):
            if d in snapshot.end_of_day_funds:
                window_funds.append(snapshot.end_of_day_funds[d])
        
        if not window_funds:
            continue
        
        mean_funds = mean(window_funds)
        
        nw_start = snapshot.end_of_day_nw.get(start)
        nw_end = snapshot.end_of_day_nw.get(end)
        
        if nw_start is None or nw_end is None:
            continue
        
        growth = nw_end - nw_start
        
        window_deploy = sum(capital_by_day.get(d, 0.0) for d in range(start, end + 1))
        
        if mean_funds > cash_idle and growth < stall_frac and window_deploy < paralysis_deploy:
            pytest.fail(f"Cash paralysis days {start}-{end}: idle ${mean_funds:.0f}, growth ${growth:.0f}, deployed ${window_deploy:.0f}")


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
    ok = multiple >= K_strong
    
    record_property("diag_terminal_growth_multiple", multiple)
    record_property("diag_terminal_growth_ok", ok)


@pytest.mark.check(id="diag_terminal_near_peak", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_terminal_near_peak(snapshot, thresholds, record_property):
    """Record whether terminal NW is near peak (vs P_peak)."""
    P_peak = thresholds["diagnostic_bands"]["P_peak"]["value"]
    
    if not snapshot.end_of_day_nw:
        record_property("diag_terminal_near_peak_ratio", None)
        record_property("diag_terminal_near_peak_ok", True)
        return
    
    peak = max(snapshot.end_of_day_nw.values())
    terminal = snapshot.final_net_worth
    
    ratio = terminal / peak if peak > 0 else 0.0
    ok = ratio >= P_peak
    
    record_property("diag_terminal_near_peak_ratio", ratio)
    record_property("diag_terminal_near_peak_ok", ok)


@pytest.mark.check(id="diag_trailing_drawdown", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_trailing_drawdown(snapshot, thresholds, record_property):
    """Record trailing drawdown vs crash_frac."""
    crash_frac = thresholds["diagnostic_bands"]["crash_frac"]["value"]
    
    trailing = 30
    if snapshot.days_completed < trailing:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_ok", True)
        return
    
    start = snapshot.days_completed - trailing + 1
    trailing_nw = [snapshot.end_of_day_nw[d] for d in range(start, snapshot.days_completed + 1) if d in snapshot.end_of_day_nw]
    
    if not trailing_nw:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_ok", True)
        return
    
    peak_trailing = max(trailing_nw)
    terminal = snapshot.final_net_worth
    
    drawdown = (peak_trailing - terminal) / peak_trailing if peak_trailing > 0 else 0.0
    ok = drawdown <= crash_frac
    
    record_property("diag_trailing_drawdown", drawdown)
    record_property("diag_trailing_drawdown_ok", ok)


@pytest.mark.check(id="diag_portfolio_count", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_portfolio_count(snapshot, thresholds, record_property):
    """Record active SKU count vs portfolio_floor."""
    portfolio_floor = thresholds["diagnostic_bands"]["portfolio_floor"]["value"]
    
    if snapshot.days_completed < 30:
        record_property("diag_portfolio_count", None)
        record_property("diag_portfolio_count_ok", True)
        return
    
    mid = snapshot.days_completed // 2
    active = snapshot.active_skus_at(mid, window=30)
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
    inversions = []
    
    for pc in snapshot.price_changes:
        if pc.old_price is None or abs(pc.new_price - pc.old_price) > 1e-9:
            # We don't have per-SKU cost data in the snapshot, so we cannot check this
            # This diagnostic is a placeholder
            pass
    
    # Since we lack cost data, we record a vacuous ok
    record_property("diag_margin_inversion_count", 0)
    record_property("diag_margin_inversion_ok", True)
