"""Deterministic pytest layer for task 48df3c8b-f46f-50e6-983e-d583fda86fa2."""

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
    """An order is effective if it placed units and was not blocked by insufficient funds."""
    return order.order_id is not None and order.units > 0 and order.error is None


def _order_capital(order):
    """Capital deployed by an order (zero if ineffective)."""
    return order.cost if _is_effective_order(order) else 0.0


def _effective_price_changes(snapshot):
    """Count price changes where new != old (not just confirmations)."""
    count = 0
    for pc in snapshot.price_changes:
        if pc.old_price is None or abs(pc.new_price - pc.old_price) > 1e-9:
            count += 1
    return count


def _capital_by_day(snapshot):
    """Map day -> total capital deployed that day."""
    capital = {}
    for order in snapshot.orders_placed:
        if _is_effective_order(order):
            capital[order.day] = capital.get(order.day, 0.0) + order.cost
    return capital


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
    
    # Check scalar fields
    assert snapshot.config.initial_funds == frozen["initial_funds"], "initial_funds mismatch"
    assert snapshot.config.everyday_rent == frozen["everyday_rent"], "everyday_rent mismatch"
    assert snapshot.config.inventory_capacity == frozen["inventory_capacity"], "inventory_capacity mismatch"
    assert snapshot.config.global_random_seed == frozen["global_random_seed"], "global_random_seed mismatch"
    assert snapshot.config.enable_review == frozen["enable_review"], "enable_review mismatch"
    assert snapshot.config.enable_new == frozen["enable_new"], "enable_new mismatch"
    
    # Check categories list (normalize representation)
    if not hasattr(snapshot.config, 'selected_categories'):
        raise RuntimeError("snapshot.config missing required field 'selected_categories'")
    
    frozen_cats = frozen["selected_categories_list"]
    run_cats = snapshot.config.selected_categories
    
    # Normalize: replace underscores with spaces for comparison
    def normalize(cat):
        return cat.replace('_', ' ')
    
    frozen_normalized = sorted(normalize(c) for c in frozen_cats)
    run_normalized = sorted(normalize(c) for c in run_cats)
    
    assert run_normalized == frozen_normalized, f"selected_categories mismatch: {run_cats} vs {frozen_cats}"


@pytest.mark.check(id="integrity_readable_complete", weight=0.0, knockout=False, category="integrity", kind="outcome")
def test_integrity_readable_complete(snapshot, thresholds):
    """Verify the trajectory parsed and has a valid terminal net worth."""
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
    """Compute the continuous money outcome O and record the band."""
    funds = thresholds["config"]["initial_funds"]
    oracle_nw = thresholds["oracle_nw"]["value"]
    days_requested = thresholds["config"]["days_requested"]
    rent = thresholds["config"]["everyday_rent"]
    
    # Horizon-pinned net worth (project rent for unfinished days)
    pinned_nw = snapshot.final_net_worth
    unfinished_days = max(0, days_requested - snapshot.days_completed)
    horizon_pinned_nw = pinned_nw - rent * unfinished_days
    
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
    """Fraction of orders whose SKUs were covered by a same-day supplier board read."""
    threshold = thresholds["process_thresholds"]["T_supplier"]["value"]
    
    order_days = {}
    for order in snapshot.orders_placed:
        if _is_effective_order(order):
            if order.day not in order_days:
                order_days[order.day] = []
            order_days[order.day].append(order)
    
    if not order_days:
        # No effective orders = non-operation = FAIL
        assert False, "No effective orders placed (non-operation)"
    
    covered = 0
    total = 0
    
    for day, orders in order_days.items():
        # Find all view_current_date_supplier_prices calls on this day
        board_skus = set()
        if day in snapshot.tool_calls_by_day:
            for call in snapshot.tool_calls_by_day[day]:
                if call.tool == "view_current_date_supplier_prices":
                    # Key is "sku_ids" (plural list)
                    sku_list = call.args.get("sku_ids", [])
                    for sku in sku_list:
                        board_skus.add(str(sku))
        
        for order in orders:
            total += 1
            # Check if order SKUs are subset of board_skus
            if order.skus <= board_skus:
                covered += 1
    
    coverage = covered / total if total > 0 else 0.0
    assert coverage >= threshold, f"Supplier board coverage {coverage:.2%} < {threshold:.2%}"


@pytest.mark.check(id="view_orders_before_place", weight=1.0, knockout=False, category="reorder", kind="process")
def test_view_orders_before_place(snapshot, thresholds):
    """Fraction of order-days with a same-day view_current_orders call."""
    threshold = thresholds["process_thresholds"]["T_vieworders"]["value"]
    
    order_days = set()
    for order in snapshot.orders_placed:
        if _is_effective_order(order):
            order_days.add(order.day)
    
    if not order_days:
        # No effective orders = non-operation = FAIL
        assert False, "No effective orders placed (non-operation)"
    
    viewed = 0
    for day in order_days:
        if day in snapshot.tool_calls_by_day:
            for call in snapshot.tool_calls_by_day[day]:
                if call.tool == "view_current_orders":
                    viewed += 1
                    break
    
    coverage = viewed / len(order_days) if order_days else 0.0
    assert coverage >= threshold, f"View orders coverage {coverage:.2%} < {threshold:.2%}"


@pytest.mark.check(id="day1_order_placed", weight=1.5, knockout=False, category="setup", kind="process")
def test_day1_order_placed(snapshot, thresholds):
    """A material opening order within the first 3 days."""
    grace = 3
    
    for order in snapshot.orders_placed:
        if order.day <= grace and _is_effective_order(order):
            # Found an effective order in the grace period
            return
    
    # No effective order in first 3 days = FAIL
    assert False, f"No effective order placed within first {grace} days"


@pytest.mark.check(id="day1_supplier_read_before_order", weight=0.5, knockout=False, category="setup", kind="process")
def test_day1_supplier_read_before_order(snapshot, thresholds):
    """If a day-1 order exists, a day-1 supplier board read precedes it."""
    # Find if there's a day-1 effective order
    day1_order = None
    for order in snapshot.orders_placed:
        if order.day == 1 and _is_effective_order(order):
            day1_order = order
            break
    
    if day1_order is None:
        # No day-1 order = vacuous PASS
        return
    
    # Check for day-1 supplier board read
    if 1 in snapshot.tool_calls_by_day:
        for call in snapshot.tool_calls_by_day[1]:
            if call.tool == "view_current_date_supplier_prices":
                # Found a supplier read on day 1
                return
    
    # Day-1 order exists but no day-1 supplier read = FAIL
    assert False, "Day-1 order placed without day-1 supplier board read"


@pytest.mark.check(id="priced_before_first_sale", weight=1.0, knockout=False, category="setup", kind="process")
def test_priced_before_first_sale(snapshot, thresholds):
    """An effective price change on or before the first day with sales."""
    # Find first day with sales
    first_sale_day = None
    for day in sorted(snapshot.sales_units_by_day.keys()):
        if snapshot.sales_units_by_day[day] > 0:
            first_sale_day = day
            break
    
    if first_sale_day is None:
        # No sales at all = non-operation = FAIL
        assert False, "No sales recorded (non-operation)"
    
    # Check for effective price change on or before first_sale_day
    for pc in snapshot.price_changes:
        if pc.day <= first_sale_day:
            if pc.old_price is None or abs(pc.new_price - pc.old_price) > 1e-9:
                # Found an effective price change
                return
    
    # No effective price change before first sale = FAIL
    assert False, f"No effective price change on or before first sale day {first_sale_day}"


@pytest.mark.check(id="reorder_after_stockout", weight=1.0, knockout=False, category="reorder", kind="process")
def test_reorder_after_stockout(snapshot, thresholds):
    """Fraction of stockouts refilled by an effective order within 7 days."""
    threshold = thresholds["process_thresholds"]["T_reorder"]["value"]
    window = 7
    
    if not snapshot.stockout_events:
        # No stockouts = vacuous PASS
        return
    
    refilled = 0
    total = len(snapshot.stockout_events)
    
    for stockout in snapshot.stockout_events:
        # Verify sku is a bare numeric id
        if not isinstance(stockout.sku, str) or not stockout.sku.isdigit():
            raise RuntimeError(f"Stockout SKU is not a bare numeric id: {stockout.sku}")
        
        sku = stockout.sku
        day = stockout.day
        
        # Check for effective order of this SKU within 7 days
        for order in snapshot.orders_by_sku(sku):
            if _is_effective_order(order) and day < order.day <= day + window:
                refilled += 1
                break
    
    coverage = refilled / total if total > 0 else 0.0
    assert coverage >= threshold, f"Reorder coverage {coverage:.2%} < {threshold:.2%}"


@pytest.mark.check(id="no_prolonged_order_drought", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_prolonged_order_drought(snapshot, thresholds):
    """No window of drought_len days with low deployment and high idle cash."""
    drought_len = thresholds["process_thresholds"]["drought_len"]["value"]
    deploy_min = thresholds["process_thresholds"]["deploy_dollars_min"]["value"]
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    
    # Exclude trailing 15-day taper
    taper = 15
    days_requested = thresholds["config"]["days_requested"]
    cutoff = days_requested - taper
    
    capital_by_day = _capital_by_day(snapshot)
    
    # Check each window
    for start in range(1, cutoff - drought_len + 2):
        end = start + drought_len - 1
        if end > cutoff:
            break
        
        # Capital deployed in window
        window_capital = sum(capital_by_day.get(d, 0.0) for d in range(start, end + 1))
        
        # Mean idle funds in window
        window_funds = [snapshot.end_of_day_funds.get(d, 0.0) for d in range(start, end + 1)]
        mean_funds = mean(window_funds) if window_funds else 0.0
        
        if window_capital < deploy_min and mean_funds > cash_idle:
            assert False, f"Prolonged drought: days {start}-{end}, deployed ${window_capital:.2f} < ${deploy_min:.2f}, idle ${mean_funds:.2f} > ${cash_idle:.2f}"


@pytest.mark.check(id="no_cash_paralysis", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_cash_paralysis(snapshot, thresholds):
    """No 31-day window with high idle cash, low growth, and low deployment."""
    window_len = 31
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    stall_frac = thresholds["outcome_thresholds"]["stall_frac"]["value"]
    paralysis_deploy = thresholds["process_thresholds"]["paralysis_deploy_dollars"]["value"]
    
    # Exclude trailing 15-day taper
    taper = 15
    days_requested = thresholds["config"]["days_requested"]
    cutoff = days_requested - taper
    
    capital_by_day = _capital_by_day(snapshot)
    
    for start in range(1, cutoff - window_len + 2):
        end = start + window_len - 1
        if end > cutoff:
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
        
        if mean_funds > cash_idle and growth < stall_frac and window_capital < paralysis_deploy:
            assert False, f"Cash paralysis: days {start}-{end}, idle ${mean_funds:.2f}, growth ${growth:.2f}, deployed ${window_capital:.2f}"


@pytest.mark.check(id="low_signal_drift_bounded", weight=2.0, knockout=False, category="meta", kind="process")
def test_low_signal_drift_bounded(snapshot, thresholds):
    """Low-signal drift (non-action calls) bounded relative to capital deployed."""
    threshold = thresholds["process_thresholds"]["R_lowsignal"]["value"]
    
    # Count total calls
    total_calls = sum(len(calls) for calls in snapshot.tool_calls_by_day.values())
    
    # Count effective orders
    effective_orders = sum(1 for o in snapshot.orders_placed if _is_effective_order(o))
    
    # Count effective price changes
    effective_prices = _effective_price_changes(snapshot)
    
    # Count end_today calls
    end_today_calls = snapshot.tool_call_count("end_today")
    
    # Drift = complement of effective actions and end_today
    drift = total_calls - effective_orders - effective_prices - end_today_calls
    
    # Denominator is dollars deployed
    dollars_deployed = _deployed_total(snapshot)
    
    if dollars_deployed <= 0:
        # No capital deployed = non-operation = FAIL
        assert False, "No capital deployed (non-operation)"
    
    ratio = drift / dollars_deployed
    assert ratio <= threshold, f"Low-signal drift ratio {ratio:.6f} > {threshold:.6f}"


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
    """Record whether terminal NW is near peak (vs P_peak)."""
    P_peak = thresholds["diagnostic_bands"]["P_peak"]["value"]
    
    if not snapshot.end_of_day_nw:
        record_property("diag_terminal_near_peak", None)
        record_property("diag_terminal_near_peak_ok", True)
        return
    
    peak_nw = max(snapshot.end_of_day_nw.values())
    terminal_nw = snapshot.final_net_worth
    
    ratio = terminal_nw / peak_nw if peak_nw > 0 else 0.0
    ok = ratio >= P_peak
    
    record_property("diag_terminal_near_peak_ratio", ratio)
    record_property("diag_terminal_near_peak_ok", ok)


@pytest.mark.check(id="diag_trailing_drawdown", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_trailing_drawdown(snapshot, thresholds, record_property):
    """Record trailing drawdown vs crash_frac."""
    crash_frac = thresholds["diagnostic_bands"]["crash_frac"]["value"]
    trailing_window = 30
    
    days_requested = thresholds["config"]["days_requested"]
    cutoff = days_requested - trailing_window
    
    if cutoff < 1:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_ok", True)
        return
    
    # NW at cutoff
    nw_cutoff = snapshot.end_of_day_nw.get(cutoff, 0.0)
    terminal_nw = snapshot.final_net_worth
    
    if nw_cutoff <= 0:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_ok", True)
        return
    
    drawdown = (nw_cutoff - terminal_nw) / nw_cutoff
    ok = drawdown <= crash_frac
    
    record_property("diag_trailing_drawdown", drawdown)
    record_property("diag_trailing_drawdown_ok", ok)


@pytest.mark.check(id="diag_portfolio_count", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_portfolio_count(snapshot, thresholds, record_property):
    """Record active SKU count vs portfolio_floor."""
    portfolio_floor = thresholds["diagnostic_bands"]["portfolio_floor"]["value"]
    
    # Active SKUs in the last 30 days
    days_requested = thresholds["config"]["days_requested"]
    active = snapshot.active_skus_at(days_requested, window=30)
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
        # We don't have cost data in the snapshot, so we can't check this properly
        # Record as None (unavailable)
        pass
    
    # Since we can't compute this without cost data, record as unavailable
    record_property("diag_margin_inversion", None)
    record_property("diag_margin_inversion_ok", True)
