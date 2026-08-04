"""Deterministic pytest layer for task c2789eb2-73ef-5ac5-9be8-fee09d29997f."""

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
    """An order is effective if it deployed capital (units > 0, no error, order_id assigned)."""
    return order.order_id is not None and order.units > 0 and order.error is None


def _order_capital(order):
    """Capital deployed by an order (0 if ineffective)."""
    if not _is_effective_order(order):
        return 0.0
    return order.cost


def _effective_price_changes(snapshot):
    """Count price changes where |new - old| > 1e-9 (excludes confirmations)."""
    count = 0
    for pc in snapshot.price_changes:
        if pc.old_price is None or abs(pc.new_price - pc.old_price) > 1e-9:
            count += 1
    return count


def _capital_by_day(snapshot):
    """Map day -> total capital deployed that day."""
    cap_by_day = {}
    for order in snapshot.orders_placed:
        if _is_effective_order(order):
            cap_by_day[order.day] = cap_by_day.get(order.day, 0.0) + order.cost
    return cap_by_day


def _deployed_total(snapshot):
    """Total capital deployed across all effective orders."""
    return sum(_order_capital(o) for o in snapshot.orders_placed)


def _end_today_count(snapshot):
    """Count end_today calls."""
    count = 0
    for day_calls in snapshot.tool_calls_by_day.values():
        for call in day_calls:
            if call.tool == "end_today":
                count += 1
    return count


# ============================================================================
# INTEGRITY GATES (kind="outcome", weight=0.0, category="integrity")
# ============================================================================

@pytest.mark.check(id="integrity_config_matches_frozen_task", weight=0.0, knockout=False, category="integrity", kind="outcome")
def test_integrity_config_matches_frozen_task(snapshot, thresholds):
    """Verify the run's config matches the frozen task config."""
    frozen = thresholds["config"]
    
    # Check scalar fields
    if not hasattr(snapshot.config, "initial_funds"):
        raise RuntimeError("Loader did not surface initial_funds")
    if not hasattr(snapshot.config, "everyday_rent"):
        raise RuntimeError("Loader did not surface everyday_rent")
    if not hasattr(snapshot.config, "inventory_capacity"):
        raise RuntimeError("Loader did not surface inventory_capacity")
    if not hasattr(snapshot.config, "global_random_seed"):
        raise RuntimeError("Loader did not surface global_random_seed")
    if not hasattr(snapshot.config, "enable_review"):
        raise RuntimeError("Loader did not surface enable_review")
    if not hasattr(snapshot.config, "enable_new"):
        raise RuntimeError("Loader did not surface enable_new")
    
    assert snapshot.config.initial_funds == frozen["initial_funds"], "initial_funds mismatch"
    assert snapshot.config.everyday_rent == frozen["everyday_rent"], "everyday_rent mismatch"
    assert snapshot.config.inventory_capacity == frozen["inventory_capacity"], "inventory_capacity mismatch"
    assert snapshot.config.global_random_seed == frozen["global_random_seed"], "global_random_seed mismatch"
    assert snapshot.config.enable_review == frozen["enable_review"], "enable_review mismatch"
    assert snapshot.config.enable_new == frozen["enable_new"], "enable_new mismatch"
    
    # Check selected_categories (list comparison, representation-normalized)
    if not hasattr(snapshot.config, "selected_categories"):
        raise RuntimeError("Loader did not surface selected_categories")
    
    frozen_cats = frozen["selected_categories_list"]
    observed_cats = snapshot.config.selected_categories
    
    # Normalize: replace underscores with spaces for comparison
    def normalize(cat):
        return cat.replace("_", " ")
    
    frozen_normalized = sorted([normalize(c) for c in frozen_cats])
    observed_normalized = sorted([normalize(c) for c in observed_cats])
    
    assert observed_normalized == frozen_normalized, f"selected_categories mismatch: {observed_normalized} != {frozen_normalized}"


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
    
    terminal_nw = snapshot.final_net_worth
    days_completed = snapshot.days_completed
    
    # Horizon-pin: add back rent for unfinished days
    unfinished_days = max(0, days_requested - days_completed)
    horizon_pinned_nw = terminal_nw + rent * unfinished_days
    
    # Compute reference gain
    ref = oracle_nw - funds
    
    # Guard against near-infeasible task
    if ref <= 0:
        O = 0.0
    else:
        gain = horizon_pinned_nw - funds
        O = max(0.0, min(1.0, gain / ref))
    
    # Determine band
    band = "MADE-MONEY" if horizon_pinned_nw > funds else "LOST-MONEY"
    
    # Record properties
    record_property("pinned_net_worth", terminal_nw)
    record_property("horizon_pinned_net_worth", horizon_pinned_nw)
    record_property("money_outcome_O", O)
    record_property("money_band", band)
    
    # Assert only that terminal net worth is a real number
    assert isinstance(terminal_nw, (int, float)) and -1e15 < terminal_nw < 1e15


# ============================================================================
# PROCESS CHECKS (kind="process", weighted)
# ============================================================================

@pytest.mark.check(id="valid_tools_used", weight=1.0, knockout=False, category="meta", kind="process")
def test_valid_tools_used(snapshot, thresholds):
    """All observed tool names are in the valid tool registry."""
    observed = set()
    for day_calls in snapshot.tool_calls_by_day.values():
        for call in day_calls:
            observed.add(call.tool)
    
    assert observed.issubset(VALID_TOOLS), f"Invalid tools: {observed - set(VALID_TOOLS)}"


@pytest.mark.check(id="supplier_board_before_order", weight=1.5, knockout=False, category="supplier", kind="process")
def test_supplier_board_before_order(snapshot, thresholds):
    """Of all place_order calls, the fraction whose SKUs were covered by an earlier same-day supplier board read."""
    T_supplier = thresholds["process_thresholds"]["T_supplier"]["value"]
    
    # Collect all effective orders
    effective_orders = [o for o in snapshot.orders_placed if _is_effective_order(o)]
    
    if len(effective_orders) == 0:
        # Non-operation: no orders placed
        pytest.fail("No effective orders placed (non-operation)")
    
    # For each order, check if there was a same-day view_current_date_supplier_prices covering its SKUs
    covered = 0
    for order in effective_orders:
        day = order.day
        order_skus = order.skus
        
        # Check if there was a same-day supplier board read
        if day in snapshot.tool_calls_by_day:
            for call in snapshot.tool_calls_by_day[day]:
                if call.tool == "view_current_date_supplier_prices":
                    # This call happened on the same day; we assume it covers all SKUs
                    # (the tool returns the full board, not filtered by SKU)
                    covered += 1
                    break
    
    fraction = covered / len(effective_orders)
    assert fraction >= T_supplier, f"Supplier board coverage {fraction:.2%} < {T_supplier:.2%}"


@pytest.mark.check(id="view_orders_before_place", weight=1.0, knockout=False, category="reorder", kind="process")
def test_view_orders_before_place(snapshot, thresholds):
    """Of order-days, the fraction with an earlier same-day view_current_orders."""
    T_vieworders = thresholds["process_thresholds"]["T_vieworders"]["value"]
    
    # Collect days with effective orders
    order_days = set()
    for order in snapshot.orders_placed:
        if _is_effective_order(order):
            order_days.add(order.day)
    
    if len(order_days) == 0:
        pytest.fail("No effective orders placed (non-operation)")
    
    # For each order-day, check if there was a same-day view_current_orders
    covered = 0
    for day in order_days:
        if day in snapshot.tool_calls_by_day:
            for call in snapshot.tool_calls_by_day[day]:
                if call.tool == "view_current_orders":
                    covered += 1
                    break
    
    fraction = covered / len(order_days)
    assert fraction >= T_vieworders, f"View orders coverage {fraction:.2%} < {T_vieworders:.2%}"


@pytest.mark.check(id="day1_order_placed", weight=1.5, knockout=False, category="setup", kind="process")
def test_day1_order_placed(snapshot, thresholds):
    """A material opening order within the first 3 days."""
    grace = 3
    
    # Check for effective orders in days 1-3
    for order in snapshot.orders_placed:
        if order.day <= grace and _is_effective_order(order):
            # Found a material order
            return
    
    pytest.fail("No material opening order within first 3 days")


@pytest.mark.check(id="day1_supplier_read_before_order", weight=0.5, knockout=False, category="setup", kind="process")
def test_day1_supplier_read_before_order(snapshot, thresholds):
    """Implication: IF a day-1 order exists, a day-1 supplier board read precedes it."""
    # Check if there's a day-1 effective order
    day1_order_exists = any(o.day == 1 and _is_effective_order(o) for o in snapshot.orders_placed)
    
    if not day1_order_exists:
        # Vacuous pass: no day-1 order
        return
    
    # Check for day-1 supplier board read
    if 1 in snapshot.tool_calls_by_day:
        for call in snapshot.tool_calls_by_day[1]:
            if call.tool == "view_current_date_supplier_prices":
                # Found it
                return
    
    pytest.fail("Day-1 order exists but no day-1 supplier board read")


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
        # No sales at all: non-operation
        pytest.fail("No sales recorded (non-operation)")
    
    # Check for effective price change on or before first_sale_day
    for pc in snapshot.price_changes:
        if pc.day <= first_sale_day:
            if pc.old_price is None or abs(pc.new_price - pc.old_price) > 1e-9:
                # Found an effective price change
                return
    
    pytest.fail(f"No effective price change on or before first sale day {first_sale_day}")


@pytest.mark.check(id="reorder_after_stockout", weight=1.0, knockout=False, category="reorder", kind="process")
def test_reorder_after_stockout(snapshot, thresholds):
    """Of stockout events, the fraction refilled by an effective order within 7 days."""
    T_reorder = thresholds["process_thresholds"]["T_reorder"]["value"]
    
    stockouts = snapshot.stockout_events
    
    if len(stockouts) == 0:
        # Vacuous pass: no stockouts
        return
    
    # For each stockout, check if there's a refill order within 7 days
    refilled = 0
    for stockout in stockouts:
        sku = stockout.sku
        day = stockout.day
        
        # Verify sku is a bare numeric id (loader integrity)
        if not sku.isdigit():
            raise RuntimeError(f"Stockout SKU is not a bare numeric id: {sku}")
        
        # Check for orders of this SKU within 7 days
        orders = snapshot.orders_by_sku(sku)
        for order in orders:
            if day <= order.day <= day + 7 and _is_effective_order(order):
                refilled += 1
                break
    
    fraction = refilled / len(stockouts)
    assert fraction >= T_reorder, f"Reorder coverage {fraction:.2%} < {T_reorder:.2%}"


@pytest.mark.check(id="no_prolonged_order_drought", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_prolonged_order_drought(snapshot, thresholds):
    """No window of drought_len days (before the last 15-day taper) with low capital deployed and high idle funds."""
    drought_len = thresholds["process_thresholds"]["drought_len"]["value"]
    deploy_dollars_min = thresholds["process_thresholds"]["deploy_dollars_min"]["value"]
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    
    days_completed = snapshot.days_completed
    taper = 15
    horizon = max(1, days_completed - taper)
    
    cap_by_day = _capital_by_day(snapshot)
    funds_by_day = snapshot.end_of_day_funds
    
    # Check each window
    for start in range(1, horizon - drought_len + 2):
        end = start + drought_len - 1
        if end > horizon:
            break
        
        # Capital deployed in window
        window_capital = sum(cap_by_day.get(d, 0.0) for d in range(start, end + 1))
        
        # Mean idle funds in window
        window_funds = [funds_by_day.get(d, 0.0) for d in range(start, end + 1) if d in funds_by_day]
        if len(window_funds) == 0:
            continue
        mean_funds = mean(window_funds)
        
        # Check for drought
        if window_capital < deploy_dollars_min and mean_funds > cash_idle:
            pytest.fail(f"Order drought in days {start}-{end}: capital ${window_capital:.2f} < ${deploy_dollars_min:.2f}, mean funds ${mean_funds:.2f} > ${cash_idle:.2f}")


@pytest.mark.check(id="no_cash_paralysis", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_cash_paralysis(snapshot, thresholds):
    """No 31-day window (excluding trailing taper) with high idle funds, low growth, and low deployment."""
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    stall_frac = thresholds["outcome_thresholds"]["stall_frac"]["value"]
    paralysis_deploy_dollars = thresholds["process_thresholds"]["paralysis_deploy_dollars"]["value"]
    
    days_completed = snapshot.days_completed
    taper = 15
    horizon = max(1, days_completed - taper)
    window_len = 31
    
    cap_by_day = _capital_by_day(snapshot)
    funds_by_day = snapshot.end_of_day_funds
    nw_by_day = snapshot.end_of_day_nw
    
    # Check each window
    for start in range(1, horizon - window_len + 2):
        end = start + window_len - 1
        if end > horizon:
            break
        
        # Mean idle funds
        window_funds = [funds_by_day.get(d, 0.0) for d in range(start, end + 1) if d in funds_by_day]
        if len(window_funds) == 0:
            continue
        mean_funds = mean(window_funds)
        
        # Net worth growth
        nw_start = nw_by_day.get(start, 0.0)
        nw_end = nw_by_day.get(end, 0.0)
        if nw_start == 0:
            continue
        growth_frac = (nw_end - nw_start) / abs(nw_start)
        
        # Capital deployed
        window_capital = sum(cap_by_day.get(d, 0.0) for d in range(start, end + 1))
        
        # Check for paralysis
        if mean_funds > cash_idle and growth_frac < stall_frac and window_capital < paralysis_deploy_dollars:
            pytest.fail(f"Cash paralysis in days {start}-{end}: mean funds ${mean_funds:.2f} > ${cash_idle:.2f}, growth {growth_frac:.2%} < {stall_frac:.2%}, capital ${window_capital:.2f} < ${paralysis_deploy_dollars:.2f}")


@pytest.mark.check(id="low_signal_drift_bounded", weight=2.0, knockout=False, category="meta", kind="process")
def test_low_signal_drift_bounded(snapshot, thresholds):
    """Low-signal drift (non-action calls) bounded relative to dollars deployed."""
    R_lowsignal = thresholds["process_thresholds"]["R_lowsignal"]["value"]
    
    # Count total calls
    total_calls = sum(len(calls) for calls in snapshot.tool_calls_by_day.values())
    
    # Count effective actions
    effective_orders = sum(1 for o in snapshot.orders_placed if _is_effective_order(o))
    effective_price_changes = _effective_price_changes(snapshot)
    end_today_calls = _end_today_count(snapshot)
    
    # Drift = complement of effective actions
    drift = total_calls - effective_orders - effective_price_changes - end_today_calls
    
    # Dollars deployed
    dollars_deployed = _deployed_total(snapshot)
    
    if dollars_deployed == 0:
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
    
    terminal_nw = snapshot.final_net_worth
    multiple = terminal_nw / funds if funds > 0 else 0.0
    
    would_pass = multiple >= K_strong
    
    record_property("diag_terminal_growth_multiple", multiple)
    record_property("diag_terminal_growth_multiple_vs_K_strong", would_pass)


@pytest.mark.check(id="diag_terminal_near_peak", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_terminal_near_peak(snapshot, thresholds, record_property):
    """Record whether terminal NW is near peak (vs P_peak)."""
    P_peak = thresholds["diagnostic_bands"]["P_peak"]["value"]
    
    nw_by_day = snapshot.end_of_day_nw
    if len(nw_by_day) == 0:
        record_property("diag_terminal_near_peak", None)
        record_property("diag_terminal_near_peak_vs_P_peak", True)
        return
    
    peak_nw = max(nw_by_day.values())
    terminal_nw = snapshot.final_net_worth
    
    if peak_nw == 0:
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
    
    nw_by_day = snapshot.end_of_day_nw
    days_completed = snapshot.days_completed
    
    if days_completed < 30:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_vs_crash_frac", True)
        return
    
    # Last 30 days
    trailing_days = range(max(1, days_completed - 29), days_completed + 1)
    trailing_nw = [nw_by_day.get(d, 0.0) for d in trailing_days if d in nw_by_day]
    
    if len(trailing_nw) == 0:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_vs_crash_frac", True)
        return
    
    peak_trailing = max(trailing_nw)
    terminal_nw = snapshot.final_net_worth
    
    if peak_trailing == 0:
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
    
    days_completed = snapshot.days_completed
    if days_completed < 30:
        record_property("diag_portfolio_count", None)
        record_property("diag_portfolio_count_vs_portfolio_floor", True)
        return
    
    # Mid-run day (around day 90 for a 180-day task)
    mid_day = days_completed // 2
    active_skus = snapshot.active_skus_at(mid_day, window=30)
    count = len(active_skus)
    
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
        record_property("diag_return_rate_vs_return_rate_ref", True)
        return
    
    would_pass = rate <= return_rate_ref
    
    record_property("diag_return_rate", rate)
    record_property("diag_return_rate_vs_return_rate_ref", would_pass)


@pytest.mark.check(id="diag_spoilage_rate", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_spoilage_rate(snapshot, thresholds, record_property):
    """Record spoilage rate vs spoilage_ref."""
    spoilage_ref = thresholds["diagnostic_bands"]["spoilage_ref"]["value"]
    
    rate = snapshot.run_spoilage_rate()
    
    if rate is None:
        record_property("diag_spoilage_rate", None)
        record_property("diag_spoilage_rate_vs_spoilage_ref", True)
        return
    
    would_pass = rate <= spoilage_ref
    
    record_property("diag_spoilage_rate", rate)
    record_property("diag_spoilage_rate_vs_spoilage_ref", would_pass)


@pytest.mark.check(id="diag_margin_inversion", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_margin_inversion(snapshot, thresholds, record_property):
    """Record whether there's evidence of margin inversion (selling below cost)."""
    # Check if any price changes set a price below a known cost
    # This is a heuristic diagnostic; we don't have full cost data per SKU per day
    # We'll check if any price change sets a price that seems unreasonably low
    
    # Collect all price changes
    price_changes = snapshot.price_changes
    
    # Heuristic: if any price is set below $1, flag it (most retail items cost more)
    # This is a very loose heuristic; a more precise check would require cost data
    
    suspicious_count = 0
    for pc in price_changes:
        if pc.new_price < 1.0:
            suspicious_count += 1
    
    # Record the count of suspicious price changes
    record_property("diag_margin_inversion_suspicious_count", suspicious_count)
    record_property("diag_margin_inversion", suspicious_count == 0)
