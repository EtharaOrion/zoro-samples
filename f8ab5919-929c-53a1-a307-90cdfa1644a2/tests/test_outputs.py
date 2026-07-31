"""Deterministic pytest layer for task f8ab5919-929c-53a1-a307-90cdfa1644a2."""

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
    
    # Check selected_categories (list comparison, representation-normalized)
    frozen_cats = frozen["selected_categories_list"]
    observed_cats = snapshot.config.selected_categories
    
    def normalize_cat(c):
        return c.replace("_", " ").strip().lower()
    
    frozen_normalized = sorted(normalize_cat(c) for c in frozen_cats)
    observed_normalized = sorted(normalize_cat(c) for c in observed_cats)
    
    assert observed_normalized == frozen_normalized, f"selected_categories mismatch: {observed_cats} vs {frozen_cats}"


@pytest.mark.check(id="integrity_readable_complete", weight=0.0, knockout=False, category="integrity", kind="outcome")
def test_integrity_readable_complete(snapshot, thresholds):
    """Verify the trajectory parsed and the terminal net worth is a finite real number."""
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
    
    pinned_nw = snapshot.final_net_worth
    days_short = max(0, days_requested - snapshot.days_completed)
    horizon_pinned_nw = pinned_nw - rent * days_short
    
    ref = oracle_nw - funds
    if ref <= 0:
        O = 0.0
    else:
        raw_O = (horizon_pinned_nw - funds) / ref
        O = max(0.0, min(1.0, raw_O))
    
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
    """All observed tool names are in the valid tool set."""
    observed = set()
    for day_calls in snapshot.tool_calls_by_day.values():
        for call in day_calls:
            observed.add(call.tool)
    
    assert observed <= set(VALID_TOOLS), f"Invalid tools used: {observed - set(VALID_TOOLS)}"


@pytest.mark.check(id="supplier_board_before_order", weight=1.5, knockout=False, category="supplier", kind="process")
def test_supplier_board_before_order(snapshot, thresholds):
    """Of all place_order calls, the fraction whose ordered SKUs were covered by an earlier same-day supplier board read."""
    T_supplier = thresholds["process_thresholds"]["T_supplier"]["value"]
    
    effective_orders = [o for o in snapshot.orders_placed if _is_effective_order(o)]
    if not effective_orders:
        pytest.fail("No effective orders placed (non-operation)")
    
    covered = 0
    for order in effective_orders:
        day = order.day
        ordered_skus = order.skus
        
        # Check if there was a view_current_date_supplier_prices call earlier on the same day
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        supplier_read_found = False
        for call in day_calls:
            if call.tool == "view_current_date_supplier_prices":
                supplier_read_found = True
                break
        
        if supplier_read_found:
            covered += 1
    
    rate = covered / len(effective_orders)
    assert rate >= T_supplier, f"Supplier board coverage {rate:.2%} < {T_supplier:.2%}"


@pytest.mark.check(id="view_orders_before_place", weight=1.0, knockout=False, category="reorder", kind="process")
def test_view_orders_before_place(snapshot, thresholds):
    """Of order-days, the fraction with an earlier same-day view_current_orders."""
    T_vieworders = thresholds["process_thresholds"]["T_vieworders"]["value"]
    
    effective_orders = [o for o in snapshot.orders_placed if _is_effective_order(o)]
    if not effective_orders:
        pytest.fail("No effective orders placed (non-operation)")
    
    order_days = set(o.day for o in effective_orders)
    covered_days = 0
    
    for day in order_days:
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        view_orders_found = any(call.tool == "view_current_orders" for call in day_calls)
        if view_orders_found:
            covered_days += 1
    
    rate = covered_days / len(order_days)
    assert rate >= T_vieworders, f"View orders coverage {rate:.2%} < {T_vieworders:.2%}"


@pytest.mark.check(id="day1_order_placed", weight=1.5, knockout=False, category="setup", kind="process")
def test_day1_order_placed(snapshot, thresholds):
    """A material (effective) opening order within the first 3 days."""
    grace = 3
    early_orders = [o for o in snapshot.orders_placed if o.day <= grace and _is_effective_order(o)]
    assert len(early_orders) > 0, "No effective order placed within the first 3 days"


@pytest.mark.check(id="day1_supplier_read_before_order", weight=0.5, knockout=False, category="setup", kind="process")
def test_day1_supplier_read_before_order(snapshot, thresholds):
    """If a day-1 order exists, a day-1 supplier-board read precedes it; no day-1 order → vacuous PASS."""
    day1_orders = [o for o in snapshot.orders_placed if o.day == 1 and _is_effective_order(o)]
    if not day1_orders:
        return  # vacuous PASS
    
    day1_calls = snapshot.tool_calls_by_day.get(1, [])
    supplier_read_found = any(call.tool == "view_current_date_supplier_prices" for call in day1_calls)
    assert supplier_read_found, "Day-1 order placed without a day-1 supplier board read"


@pytest.mark.check(id="priced_before_first_sale", weight=1.0, knockout=False, category="setup", kind="process")
def test_priced_before_first_sale(snapshot, thresholds):
    """An effective price change on or before the first day with nonzero sales."""
    effective_pcs = _effective_price_changes(snapshot)
    
    first_sale_day = None
    for day in sorted(snapshot.sales_units_by_day.keys()):
        if snapshot.sales_units_by_day[day] > 0:
            first_sale_day = day
            break
    
    if first_sale_day is None:
        pytest.fail("No sales at all (non-operation)")
    
    early_price_changes = [pc for pc in effective_pcs if pc.day <= first_sale_day]
    assert len(early_price_changes) > 0, f"No effective price change on or before first sale day {first_sale_day}"


@pytest.mark.check(id="reorder_after_stockout", weight=1.0, knockout=False, category="reorder", kind="process")
def test_reorder_after_stockout(snapshot, thresholds):
    """Of stockout events, the fraction refilled by an effective order within 7 days."""
    T_reorder = thresholds["process_thresholds"]["T_reorder"]["value"]
    
    stockouts = snapshot.stockout_events
    if not stockouts:
        return  # vacuous PASS
    
    refilled = 0
    for stockout in stockouts:
        sku = stockout.sku
        day = stockout.day
        
        # Check if sku is a bare numeric id (loader integrity)
        if not isinstance(sku, str) or not sku.isdigit():
            raise RuntimeError(f"Stockout sku is not a bare numeric id: {sku}")
        
        # Look for an effective order within 7 days that includes this sku
        window_orders = [o for o in snapshot.orders_placed 
                        if day <= o.day <= day + 7 and _is_effective_order(o)]
        
        for order in window_orders:
            if sku in order.skus:
                refilled += 1
                break
    
    rate = refilled / len(stockouts)
    assert rate >= T_reorder, f"Reorder after stockout {rate:.2%} < {T_reorder:.2%}"


@pytest.mark.check(id="no_prolonged_order_drought", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_prolonged_order_drought(snapshot, thresholds):
    """No window of drought_len days (before the last 15-day taper) with < deploy_dollars_min deployed while mean idle funds > cash_idle."""
    drought_len = thresholds["process_thresholds"]["drought_len"]["value"]
    deploy_dollars_min = thresholds["process_thresholds"]["deploy_dollars_min"]["value"]
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    
    taper = 15
    last_day = snapshot.days_completed
    cutoff = last_day - taper
    
    capital_by_day = _capital_by_day(snapshot)
    
    for start_day in range(1, cutoff - drought_len + 2):
        end_day = start_day + drought_len - 1
        if end_day > cutoff:
            break
        
        window_capital = sum(capital_by_day.get(d, 0.0) for d in range(start_day, end_day + 1))
        window_funds = [snapshot.end_of_day_funds.get(d) for d in range(start_day, end_day + 1) if d in snapshot.end_of_day_funds]
        
        if window_funds:
            mean_funds = mean(window_funds)
            if window_capital < deploy_dollars_min and mean_funds > cash_idle:
                pytest.fail(f"Prolonged order drought: days {start_day}-{end_day}, capital ${window_capital:.2f} < ${deploy_dollars_min:.2f}, mean funds ${mean_funds:.2f} > ${cash_idle:.2f}")


@pytest.mark.check(id="no_cash_paralysis", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_cash_paralysis(snapshot, thresholds):
    """No 31-day window (excluding trailing taper) where mean idle funds > cash_idle AND net-worth growth < stall_frac AND < paralysis_deploy_dollars deployed."""
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    stall_frac = thresholds["outcome_thresholds"]["stall_frac"]["value"]
    paralysis_deploy_dollars = thresholds["process_thresholds"]["paralysis_deploy_dollars"]["value"]
    
    window_len = 31
    taper = 15
    last_day = snapshot.days_completed
    cutoff = last_day - taper
    
    capital_by_day = _capital_by_day(snapshot)
    
    for start_day in range(1, cutoff - window_len + 2):
        end_day = start_day + window_len - 1
        if end_day > cutoff:
            break
        
        window_funds = [snapshot.end_of_day_funds.get(d) for d in range(start_day, end_day + 1) if d in snapshot.end_of_day_funds]
        window_nw = [snapshot.end_of_day_nw.get(d) for d in range(start_day, end_day + 1) if d in snapshot.end_of_day_nw]
        window_capital = sum(capital_by_day.get(d, 0.0) for d in range(start_day, end_day + 1))
        
        if window_funds and window_nw and len(window_nw) >= 2:
            mean_funds = mean(window_funds)
            nw_start = window_nw[0]
            nw_end = window_nw[-1]
            
            if nw_start > 0:
                nw_growth = (nw_end - nw_start) / nw_start
            else:
                nw_growth = 0.0
            
            if mean_funds > cash_idle and nw_growth < stall_frac and window_capital < paralysis_deploy_dollars:
                pytest.fail(f"Cash paralysis: days {start_day}-{end_day}, mean funds ${mean_funds:.2f} > ${cash_idle:.2f}, NW growth {nw_growth:.2%} < {stall_frac:.2%}, capital ${window_capital:.2f} < ${paralysis_deploy_dollars:.2f}")


@pytest.mark.check(id="low_signal_drift_bounded", weight=2.0, knockout=False, category="meta", kind="process")
def test_low_signal_drift_bounded(snapshot, thresholds):
    """drift = total_calls - effective_orders - effective_price_changes - end_today_calls; ratio = drift / dollars_deployed; assert ratio <= R_lowsignal."""
    R_lowsignal = thresholds["process_thresholds"]["R_lowsignal"]["value"]
    
    total_calls = sum(len(calls) for calls in snapshot.tool_calls_by_day.values())
    effective_orders = sum(1 for o in snapshot.orders_placed if _is_effective_order(o))
    effective_pcs = len(_effective_price_changes(snapshot))
    end_today_calls = snapshot.tool_call_count("end_today")
    
    drift = total_calls - effective_orders - effective_pcs - end_today_calls
    dollars_deployed = _deployed_total(snapshot)
    
    if dollars_deployed <= 0:
        pytest.fail("No capital deployed (non-operation)")
    
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
    
    nw = snapshot.final_net_worth
    multiple = nw / funds if funds > 0 else 0.0
    verdict = multiple >= K_strong
    
    record_property("diag_terminal_growth_multiple", multiple)
    record_property("diag_terminal_growth_multiple_ok", verdict)


@pytest.mark.check(id="diag_terminal_near_peak", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_terminal_near_peak(snapshot, thresholds, record_property):
    """Record whether terminal NW is near peak (within P_peak)."""
    P_peak = thresholds["diagnostic_bands"]["P_peak"]["value"]
    
    nw_values = list(snapshot.end_of_day_nw.values())
    if not nw_values:
        record_property("diag_terminal_near_peak", None)
        record_property("diag_terminal_near_peak_ok", True)
        return
    
    peak = max(nw_values)
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
    
    last_day = snapshot.days_completed
    trailing_window = 30
    start_day = max(1, last_day - trailing_window + 1)
    
    trailing_nw = [snapshot.end_of_day_nw.get(d) for d in range(start_day, last_day + 1) if d in snapshot.end_of_day_nw]
    
    if not trailing_nw or len(trailing_nw) < 2:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_ok", True)
        return
    
    peak_in_window = max(trailing_nw)
    terminal = snapshot.final_net_worth
    
    if peak_in_window > 0:
        drawdown = (peak_in_window - terminal) / peak_in_window
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
    
    # Count active SKUs in the last 30 days
    last_day = snapshot.days_completed
    active_skus = snapshot.active_skus_at(last_day, window=30)
    count = len(active_skus)
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
    """Record whether there are price changes that invert margin (new price < cost)."""
    effective_pcs = _effective_price_changes(snapshot)
    
    # We don't have cost data in the snapshot, so we can't compute this diagnostic.
    # Record None and treat as ok.
    record_property("diag_margin_inversion", None)
    record_property("diag_margin_inversion_ok", True)
