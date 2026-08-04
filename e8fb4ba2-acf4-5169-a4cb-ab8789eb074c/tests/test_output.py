"""Deterministic pytest layer for RetailBench task e8fb4ba2-acf4-5169-a4cb-ab8789eb074c."""

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
    """Return dict[day, float] of capital deployed per day."""
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
    
    # Categories list (normalize representation: '_' vs ' ')
    if not hasattr(snapshot.config, 'selected_categories'):
        raise RuntimeError("snapshot.config.selected_categories missing")
    
    frozen_cats_list = frozen.get("selected_categories_list")
    if frozen_cats_list is None:
        raise RuntimeError("thresholds['config']['selected_categories_list'] missing")
    
    def normalize_cat(c):
        return c.replace('_', ' ').replace(' ', '_').strip()
    
    observed = sorted(normalize_cat(c) for c in snapshot.config.selected_categories)
    expected = sorted(normalize_cat(c) for c in frozen_cats_list)
    
    assert observed == expected, f"selected_categories mismatch: {observed} != {expected}"


@pytest.mark.check(id="integrity_readable_complete", weight=0.0, knockout=False, category="integrity", kind="outcome")
def test_integrity_readable_complete(snapshot, thresholds):
    """Verify the trajectory parsed and the terminal net worth is a finite real number."""
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
    """Compute the continuous money outcome O from the horizon-pinned net worth."""
    funds = thresholds["config"]["initial_funds"]
    oracle_nw = thresholds["oracle_nw"]["value"]
    days_requested = thresholds["config"]["days_requested"]
    rent = thresholds["config"]["everyday_rent"]
    
    # Horizon-pinned net worth: adjust for unfinished days
    days_short = max(0, days_requested - snapshot.days_completed)
    horizon_pinned_nw = snapshot.final_net_worth - rent * days_short
    
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
    assert -1e15 < snapshot.final_net_worth < 1e15


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
    
    invalid = observed - set(VALID_TOOLS)
    assert not invalid, f"Invalid tools used: {invalid}"


@pytest.mark.check(id="supplier_board_before_order", weight=1.5, knockout=False, category="supplier", kind="process")
def test_supplier_board_before_order(snapshot, thresholds):
    """Of all place_order calls, the fraction whose ordered SKUs were covered by an earlier same-day view_current_date_supplier_prices."""
    T_supplier = thresholds["process_thresholds"]["T_supplier"]["value"]
    
    effective_orders = [o for o in snapshot.orders_placed if _is_effective_order(o)]
    
    if not effective_orders:
        # Non-operation: definite FAIL
        pytest.fail("No effective orders placed (non-operation)")
    
    covered_count = 0
    
    for order in effective_orders:
        day = order.day
        order_skus = order.skus
        
        # Find all view_current_date_supplier_prices calls on the same day before this order
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        
        read_skus = set()
        for call in day_calls:
            if call.tool == "view_current_date_supplier_prices":
                # Extract SKUs from call.args["sku_ids"] (always a list)
                sku_ids = call.args.get("sku_ids", [])
                for sku in sku_ids:
                    read_skus.add(str(sku))
        
        # Check if order SKUs are a subset of read SKUs
        if order_skus.issubset(read_skus):
            covered_count += 1
    
    coverage = covered_count / len(effective_orders)
    assert coverage >= T_supplier, f"Supplier board coverage {coverage:.2%} < {T_supplier:.2%}"


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
        if any(call.tool == "view_current_orders" for call in day_calls):
            covered_days += 1
    
    coverage = covered_days / len(order_days)
    assert coverage >= T_vieworders, f"View orders coverage {coverage:.2%} < {T_vieworders:.2%}"


@pytest.mark.check(id="day1_order_placed", weight=1.5, knockout=False, category="setup", kind="process")
def test_day1_order_placed(snapshot, thresholds):
    """A material (effective) opening order within the first 3 days."""
    grace = 3
    
    early_orders = [o for o in snapshot.orders_placed if o.day <= grace and _is_effective_order(o)]
    
    assert early_orders, f"No effective order placed within first {grace} days"


@pytest.mark.check(id="day1_supplier_read_before_order", weight=0.5, knockout=False, category="setup", kind="process")
def test_day1_supplier_read_before_order(snapshot, thresholds):
    """Implication: IF a day-1 order exists, a day-1 supplier-board read precedes it."""
    day1_orders = [o for o in snapshot.orders_placed if o.day == 1 and _is_effective_order(o)]
    
    if not day1_orders:
        # Vacuous PASS
        return
    
    day1_calls = snapshot.tool_calls_by_day.get(1, [])
    has_supplier_read = any(call.tool == "view_current_date_supplier_prices" for call in day1_calls)
    
    assert has_supplier_read, "Day-1 order exists but no day-1 supplier board read"


@pytest.mark.check(id="priced_before_first_sale", weight=1.0, knockout=False, category="setup", kind="process")
def test_priced_before_first_sale(snapshot, thresholds):
    """An EFFECTIVE price change on or before the first day with nonzero sales."""
    # Find first day with sales
    first_sale_day = None
    for day in sorted(snapshot.sales_units_by_day.keys()):
        if snapshot.sales_units_by_day[day] > 0:
            first_sale_day = day
            break
    
    if first_sale_day is None:
        # No sales at all: definite FAIL (non-operation)
        pytest.fail("No sales recorded (non-operation)")
    
    effective_changes = _effective_price_changes(snapshot)
    early_changes = [pc for pc in effective_changes if pc.day <= first_sale_day]
    
    assert early_changes, f"No effective price change on or before first sale day {first_sale_day}"


@pytest.mark.check(id="reorder_after_stockout", weight=1.0, knockout=False, category="reorder", kind="process")
def test_reorder_after_stockout(snapshot, thresholds):
    """Of stockout events, the fraction refilled by an effective order within 7 days."""
    T_reorder = thresholds["process_thresholds"]["T_reorder"]["value"]
    reorder_window = 7
    
    stockouts = snapshot.stockout_events
    
    if not stockouts:
        # Vacuous PASS
        return
    
    refilled_count = 0
    
    for stockout in stockouts:
        sku = stockout.sku
        day = stockout.day
        
        # Verify sku is a bare numeric id (loader contract)
        if not isinstance(sku, str) or not sku.isdigit():
            raise RuntimeError(f"Stockout SKU is not a bare numeric id: {sku}")
        
        # Find orders for this SKU within the next 7 days
        window_end = day + reorder_window
        sku_orders = snapshot.orders_by_sku(sku)
        
        refilled = any(
            o.day > day and o.day <= window_end and _is_effective_order(o)
            for o in sku_orders
        )
        
        if refilled:
            refilled_count += 1
    
    coverage = refilled_count / len(stockouts)
    assert coverage >= T_reorder, f"Reorder coverage {coverage:.2%} < {T_reorder:.2%}"


@pytest.mark.check(id="no_prolonged_order_drought", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_prolonged_order_drought(snapshot, thresholds):
    """No window of drought_len days (before the last 15-day taper) with < deploy_dollars_min deployed while mean idle funds > cash_idle."""
    drought_len = thresholds["process_thresholds"]["drought_len"]["value"]
    deploy_dollars_min = thresholds["process_thresholds"]["deploy_dollars_min"]["value"]
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    taper = 15
    
    capital_by_day = _capital_by_day(snapshot)
    
    # Exclude the trailing taper
    horizon = snapshot.days_completed
    check_until = max(1, horizon - taper)
    
    for start_day in range(1, check_until - drought_len + 2):
        end_day = start_day + drought_len - 1
        if end_day > check_until:
            break
        
        window_days = range(start_day, end_day + 1)
        
        # Capital deployed in window
        window_capital = sum(capital_by_day.get(d, 0.0) for d in window_days)
        
        # Mean idle funds in window
        window_funds = [snapshot.end_of_day_funds.get(d, 0.0) for d in window_days if d in snapshot.end_of_day_funds]
        if not window_funds:
            continue
        mean_funds = mean(window_funds)
        
        # Check for drought
        if window_capital < deploy_dollars_min and mean_funds > cash_idle:
            pytest.fail(f"Order drought: days {start_day}-{end_day}, deployed ${window_capital:.0f} < ${deploy_dollars_min:.0f}, mean funds ${mean_funds:.0f}")


@pytest.mark.check(id="no_cash_paralysis", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_cash_paralysis(snapshot, thresholds):
    """No 31-day window (excluding trailing taper) where mean idle funds > cash_idle AND net-worth growth < stall_frac AND < paralysis_deploy_dollars deployed."""
    window_len = 31
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    stall_frac = thresholds["outcome_thresholds"]["stall_frac"]["value"]
    paralysis_deploy_dollars = thresholds["process_thresholds"]["paralysis_deploy_dollars"]["value"]
    taper = 15
    
    capital_by_day = _capital_by_day(snapshot)
    
    horizon = snapshot.days_completed
    check_until = max(1, horizon - taper)
    
    for start_day in range(1, check_until - window_len + 2):
        end_day = start_day + window_len - 1
        if end_day > check_until:
            break
        
        window_days = range(start_day, end_day + 1)
        
        # Mean idle funds
        window_funds = [snapshot.end_of_day_funds.get(d, 0.0) for d in window_days if d in snapshot.end_of_day_funds]
        if not window_funds:
            continue
        mean_funds = mean(window_funds)
        
        # Net worth growth
        nw_start = snapshot.end_of_day_nw.get(start_day)
        nw_end = snapshot.end_of_day_nw.get(end_day)
        if nw_start is None or nw_end is None or nw_start <= 0:
            continue
        growth = (nw_end - nw_start) / nw_start
        
        # Capital deployed
        window_capital = sum(capital_by_day.get(d, 0.0) for d in window_days)
        
        # Check for paralysis
        if mean_funds > cash_idle and growth < stall_frac and window_capital < paralysis_deploy_dollars:
            pytest.fail(f"Cash paralysis: days {start_day}-{end_day}, mean funds ${mean_funds:.0f}, growth {growth:.2%}, deployed ${window_capital:.0f}")


@pytest.mark.check(id="low_signal_drift_bounded", weight=2.0, knockout=False, category="meta", kind="process")
def test_low_signal_drift_bounded(snapshot, thresholds):
    """drift = total_calls - effective_orders - effective_price_changes - end_today_calls; ratio = drift / dollars_deployed; assert ratio <= R_lowsignal."""
    R_lowsignal = thresholds["process_thresholds"]["R_lowsignal"]["value"]
    
    # Total calls
    total_calls = sum(len(calls) for calls in snapshot.tool_calls_by_day.values())
    
    # Effective orders
    effective_orders_count = sum(1 for o in snapshot.orders_placed if _is_effective_order(o))
    
    # Effective price changes
    effective_price_changes_count = len(_effective_price_changes(snapshot))
    
    # end_today calls
    end_today_count = snapshot.tool_call_count("end_today")
    
    # Drift (the complement: everything that is NOT an effective action and NOT end_today)
    drift = total_calls - effective_orders_count - effective_price_changes_count - end_today_count
    
    # Dollars deployed
    dollars_deployed = _deployed_total(snapshot)
    
    if dollars_deployed <= 0:
        # Non-operation: definite FAIL
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
    
    would_pass = multiple >= K_strong
    
    record_property("diag_terminal_growth_multiple", multiple)
    record_property("diag_terminal_growth_multiple_vs_K_strong", would_pass)


@pytest.mark.check(id="diag_terminal_near_peak", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_terminal_near_peak(snapshot, thresholds, record_property):
    """Record whether terminal NW is near peak (within P_peak of max)."""
    P_peak = thresholds["diagnostic_bands"]["P_peak"]["value"]
    
    if not snapshot.end_of_day_nw:
        record_property("diag_terminal_near_peak", None)
        record_property("diag_terminal_near_peak_vs_P_peak", True)
        return
    
    peak_nw = max(snapshot.end_of_day_nw.values())
    terminal_nw = snapshot.final_net_worth
    
    if peak_nw <= 0:
        record_property("diag_terminal_near_peak", None)
        record_property("diag_terminal_near_peak_vs_P_peak", True)
        return
    
    drawdown = (peak_nw - terminal_nw) / peak_nw
    would_pass = drawdown <= P_peak
    
    record_property("diag_terminal_near_peak_drawdown", drawdown)
    record_property("diag_terminal_near_peak_vs_P_peak", would_pass)


@pytest.mark.check(id="diag_trailing_drawdown", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_trailing_drawdown(snapshot, thresholds, record_property):
    """Record trailing drawdown vs crash_frac."""
    crash_frac = thresholds["diagnostic_bands"]["crash_frac"]["value"]
    trailing_window = 30
    
    if not snapshot.end_of_day_nw or snapshot.days_completed < trailing_window:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_vs_crash_frac", True)
        return
    
    # Peak in trailing window
    trailing_days = range(snapshot.days_completed - trailing_window + 1, snapshot.days_completed + 1)
    trailing_nw = [snapshot.end_of_day_nw.get(d, 0.0) for d in trailing_days if d in snapshot.end_of_day_nw]
    
    if not trailing_nw:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_vs_crash_frac", True)
        return
    
    peak = max(trailing_nw)
    terminal = snapshot.final_net_worth
    
    if peak <= 0:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_vs_crash_frac", True)
        return
    
    drawdown = (peak - terminal) / peak
    would_pass = drawdown <= crash_frac
    
    record_property("diag_trailing_drawdown", drawdown)
    record_property("diag_trailing_drawdown_vs_crash_frac", would_pass)


@pytest.mark.check(id="diag_portfolio_count", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_portfolio_count(snapshot, thresholds, record_property):
    """Record active SKU count vs portfolio_floor."""
    portfolio_floor = thresholds["diagnostic_bands"]["portfolio_floor"]["value"]
    window = 30
    
    # Use mid-horizon day
    mid_day = snapshot.days_completed // 2
    
    active_skus = snapshot.active_skus_at(mid_day, window=window)
    count = len(active_skus)
    
    would_pass = count >= portfolio_floor
    
    record_property("diag_portfolio_count", count)
    record_property("diag_portfolio_count_vs_floor", would_pass)


@pytest.mark.check(id="diag_return_rate", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_return_rate(snapshot, thresholds, record_property):
    """Record return rate vs return_rate_ref."""
    return_rate_ref = thresholds["diagnostic_bands"]["return_rate_ref"]["value"]
    
    rate = snapshot.run_return_rate()
    
    if rate is None:
        record_property("diag_return_rate", None)
        record_property("diag_return_rate_vs_ref", True)
        return
    
    would_pass = rate <= return_rate_ref
    
    record_property("diag_return_rate", rate)
    record_property("diag_return_rate_vs_ref", would_pass)


@pytest.mark.check(id="diag_spoilage_rate", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_spoilage_rate(snapshot, thresholds, record_property):
    """Record spoilage rate vs spoilage_ref."""
    spoilage_ref = thresholds["diagnostic_bands"]["spoilage_ref"]["value"]
    
    rate = snapshot.run_spoilage_rate()
    
    if rate is None:
        record_property("diag_spoilage_rate", None)
        record_property("diag_spoilage_rate_vs_ref", True)
        return
    
    would_pass = rate <= spoilage_ref
    
    record_property("diag_spoilage_rate", rate)
    record_property("diag_spoilage_rate_vs_ref", would_pass)


@pytest.mark.check(id="diag_margin_inversion", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_margin_inversion(snapshot, thresholds, record_property):
    """Record whether margin inverted (terminal NW < opening funds)."""
    funds = thresholds["config"]["initial_funds"]
    nw = snapshot.final_net_worth
    
    inverted = nw < funds
    
    record_property("diag_margin_inversion", inverted)
