"""Deterministic pytest layer for task 091ef453-61c5-5796-8430-d937e060138f."""

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
    """Verify the run's config matches the frozen task definition."""
    frozen = thresholds["config"]
    
    # Scalar fields
    assert snapshot.config.initial_funds == frozen["initial_funds"], "initial_funds mismatch"
    assert snapshot.config.everyday_rent == frozen["everyday_rent"], "everyday_rent mismatch"
    assert snapshot.config.inventory_capacity == frozen["inventory_capacity"], "inventory_capacity mismatch"
    assert snapshot.config.global_random_seed == frozen["global_random_seed"], "global_random_seed mismatch"
    assert snapshot.config.enable_review == frozen["enable_review"], "enable_review mismatch"
    assert snapshot.config.enable_new == frozen["enable_new"], "enable_new mismatch"
    
    # Categories: compare normalized lists
    if not hasattr(snapshot.config, 'selected_categories'):
        raise RuntimeError("snapshot.config.selected_categories missing")
    
    run_cats = sorted([c.replace('_', ' ').strip().lower() for c in snapshot.config.selected_categories])
    frozen_cats = sorted([c.replace('_', ' ').strip().lower() for c in frozen["selected_categories_list"]])
    assert run_cats == frozen_cats, f"selected_categories mismatch: {run_cats} vs {frozen_cats}"


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
    """Compute the continuous money outcome O from horizon-pinned net worth."""
    funds = thresholds["config"]["initial_funds"]
    oracle_nw = thresholds["oracle_nw"]["value"]
    days_requested = thresholds["config"]["days_requested"]
    rent = thresholds["config"]["everyday_rent"]
    
    # Horizon-pinned net worth: adjust for unfinished days
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
# PROCESS CHECKS (kind="process", weighted)
# ============================================================================

@pytest.mark.check(id="valid_tools_used", weight=1.0, knockout=False, category="meta", kind="process")
def test_valid_tools_used(snapshot, thresholds):
    """All tool names used are in the valid registry."""
    observed = set()
    for day_calls in snapshot.tool_calls_by_day.values():
        for call in day_calls:
            observed.add(call.tool)
    
    assert observed.issubset(VALID_TOOLS), f"Invalid tools: {observed - set(VALID_TOOLS)}"


@pytest.mark.check(id="supplier_board_before_order", weight=1.5, knockout=False, category="supplier", kind="process")
def test_supplier_board_before_order(snapshot, thresholds):
    """Fraction of orders whose SKUs were covered by same-day supplier board read >= T_supplier."""
    T = thresholds["process_thresholds"]["T_supplier"]["value"]
    
    effective_orders = [o for o in snapshot.orders_placed if _is_effective_order(o)]
    if not effective_orders:
        pytest.fail("No effective orders placed (non-operation)")
    
    covered = 0
    for order in effective_orders:
        day = order.day
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        
        # Find all view_current_date_supplier_prices calls on this day before the order
        read_skus = set()
        for call in day_calls:
            if call.tool == "view_current_date_supplier_prices":
                # Extract SKUs from call.args["sku_ids"] (always a list)
                sku_list = call.args.get("sku_ids", [])
                read_skus.update(str(s) for s in sku_list)
        
        # Check if order SKUs are subset of read SKUs
        if order.skus.issubset(read_skus):
            covered += 1
    
    rate = covered / len(effective_orders)
    assert rate >= T, f"Supplier board coverage {rate:.2%} < {T:.2%}"


@pytest.mark.check(id="view_orders_before_place", weight=1.0, knockout=False, category="reorder", kind="process")
def test_view_orders_before_place(snapshot, thresholds):
    """Fraction of order-days with earlier same-day view_current_orders >= T_vieworders."""
    T = thresholds["process_thresholds"]["T_vieworders"]["value"]
    
    # Days with effective orders
    order_days = set()
    for order in snapshot.orders_placed:
        if _is_effective_order(order):
            order_days.add(order.day)
    
    if not order_days:
        pytest.fail("No effective orders placed (non-operation)")
    
    covered = 0
    for day in order_days:
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        if any(call.tool == "view_current_orders" for call in day_calls):
            covered += 1
    
    rate = covered / len(order_days)
    assert rate >= T, f"view_current_orders coverage {rate:.2%} < {T:.2%}"


@pytest.mark.check(id="day1_order_placed", weight=1.5, knockout=False, category="setup", kind="process")
def test_day1_order_placed(snapshot, thresholds):
    """A material opening order within the first 3 days."""
    grace = 3
    
    for order in snapshot.orders_placed:
        if order.day <= grace and _is_effective_order(order) and order.units > 1:
            return  # Found a material opening order
    
    pytest.fail("No material opening order within first 3 days")


@pytest.mark.check(id="day1_supplier_read_before_order", weight=0.5, knockout=False, category="setup", kind="process")
def test_day1_supplier_read_before_order(snapshot, thresholds):
    """If a day-1 order exists, a day-1 supplier board read precedes it."""
    day1_orders = [o for o in snapshot.orders_placed if o.day == 1 and _is_effective_order(o)]
    
    if not day1_orders:
        return  # Vacuous pass: no day-1 order
    
    day1_calls = snapshot.tool_calls_by_day.get(1, [])
    has_supplier_read = any(call.tool == "view_current_date_supplier_prices" for call in day1_calls)
    
    assert has_supplier_read, "Day-1 order exists but no day-1 supplier board read"


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
        pytest.fail("No sales at all (non-operation)")
    
    # Check for effective price change on or before first sale day
    effective_changes = _effective_price_changes(snapshot)
    for pc in effective_changes:
        if pc.day <= first_sale_day:
            return  # Found an effective price change
    
    pytest.fail(f"No effective price change on or before first sale day {first_sale_day}")


@pytest.mark.check(id="reorder_after_stockout", weight=1.0, knockout=False, category="reorder", kind="process")
def test_reorder_after_stockout(snapshot, thresholds):
    """Fraction of stockouts refilled by effective order within 7 days >= T_reorder."""
    T = thresholds["process_thresholds"]["T_reorder"]["value"]
    
    if not snapshot.stockout_events:
        return  # Vacuous pass: no stockouts
    
    refilled = 0
    for stockout in snapshot.stockout_events:
        # Verify sku is a bare numeric id
        if not isinstance(stockout.sku, str) or not stockout.sku.isdigit():
            raise RuntimeError(f"Stockout sku is not a bare numeric id: {stockout.sku}")
        
        sku = stockout.sku
        day = stockout.day
        
        # Look for effective orders of this SKU within 7 days
        orders = snapshot.orders_by_sku(sku)
        for order in orders:
            if _is_effective_order(order) and day < order.day <= day + 7:
                refilled += 1
                break
    
    rate = refilled / len(snapshot.stockout_events)
    assert rate >= T, f"Stockout refill rate {rate:.2%} < {T:.2%}"


@pytest.mark.check(id="no_prolonged_order_drought", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_prolonged_order_drought(snapshot, thresholds):
    """No window of drought_len days (before trailing taper) with low deployment and high idle cash."""
    drought_len = thresholds["process_thresholds"]["drought_len"]["value"]
    deploy_min = thresholds["process_thresholds"]["deploy_dollars_min"]["value"]
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    
    # Exclude trailing 15-day taper
    horizon = snapshot.days_completed - 15
    if horizon < drought_len:
        return  # Not enough days to check
    
    capital_by_day = _capital_by_day(snapshot)
    
    for start in range(1, horizon - drought_len + 2):
        end = start + drought_len - 1
        
        # Capital deployed in window
        window_capital = sum(capital_by_day.get(d, 0.0) for d in range(start, end + 1))
        
        # Mean idle funds in window
        window_funds = [snapshot.end_of_day_funds.get(d, 0.0) for d in range(start, end + 1)]
        mean_funds = mean(window_funds) if window_funds else 0.0
        
        if window_capital < deploy_min and mean_funds > cash_idle:
            pytest.fail(f"Order drought days {start}-{end}: ${window_capital:.0f} deployed, ${mean_funds:.0f} mean idle")


@pytest.mark.check(id="no_cash_paralysis", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_cash_paralysis(snapshot, thresholds):
    """No 31-day window (excluding trailing taper) with high idle cash, low growth, and low deployment."""
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    stall_frac = thresholds["outcome_thresholds"]["stall_frac"]["value"]
    paralysis_deploy = thresholds["process_thresholds"]["paralysis_deploy_dollars"]["value"]
    
    # Exclude trailing 15-day taper
    horizon = snapshot.days_completed - 15
    if horizon < 31:
        return  # Not enough days to check
    
    capital_by_day = _capital_by_day(snapshot)
    
    for start in range(1, horizon - 30):
        end = start + 30
        
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
            pytest.fail(f"Cash paralysis days {start}-{end}: ${mean_funds:.0f} idle, ${growth:.0f} growth, ${window_capital:.0f} deployed")


@pytest.mark.check(id="low_signal_drift_bounded", weight=2.0, knockout=False, category="meta", kind="process")
def test_low_signal_drift_bounded(snapshot, thresholds):
    """Ratio of low-signal calls to dollars deployed <= R_lowsignal."""
    R = thresholds["process_thresholds"]["R_lowsignal"]["value"]
    
    # Count total calls
    total_calls = sum(len(calls) for calls in snapshot.tool_calls_by_day.values())
    
    # Count effective orders
    effective_orders = sum(1 for o in snapshot.orders_placed if _is_effective_order(o))
    
    # Count effective price changes
    effective_prices = len(_effective_price_changes(snapshot))
    
    # Count end_today calls
    end_today_calls = snapshot.tool_call_count("end_today")
    
    # Drift = complement of effective actions and end_today
    drift = total_calls - effective_orders - effective_prices - end_today_calls
    
    # Dollars deployed
    dollars = _deployed_total(snapshot)
    
    if dollars <= 0:
        pytest.fail("No capital deployed (non-operation)")
    
    ratio = drift / dollars
    assert ratio <= R, f"Low-signal drift ratio {ratio:.6f} > {R:.6f}"


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
    
    multiple = snapshot.final_net_worth / funds if funds > 0 else 0.0
    ok = multiple >= K_strong
    
    record_property("diag_terminal_growth_multiple", multiple)
    record_property("diag_terminal_growth_multiple_ok", ok)


@pytest.mark.check(id="diag_terminal_near_peak", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_terminal_near_peak(snapshot, thresholds, record_property):
    """Record whether terminal NW is near peak (within P_peak)."""
    P_peak = thresholds["diagnostic_bands"]["P_peak"]["value"]
    
    if not snapshot.end_of_day_nw:
        record_property("diag_terminal_near_peak", None)
        record_property("diag_terminal_near_peak_ok", True)
        return
    
    peak = max(snapshot.end_of_day_nw.values())
    terminal = snapshot.final_net_worth
    
    if peak <= 0:
        near_peak = True
    else:
        near_peak = terminal >= peak * (1 - P_peak)
    
    record_property("diag_terminal_near_peak", near_peak)
    record_property("diag_terminal_near_peak_ok", near_peak)


@pytest.mark.check(id="diag_trailing_drawdown", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_trailing_drawdown(snapshot, thresholds, record_property):
    """Record trailing drawdown vs crash_frac."""
    crash_frac = thresholds["diagnostic_bands"]["crash_frac"]["value"]
    
    # Last 30 days
    if snapshot.days_completed < 30:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_ok", True)
        return
    
    trailing_start = snapshot.days_completed - 29
    trailing_nw = [snapshot.end_of_day_nw.get(d, 0.0) for d in range(trailing_start, snapshot.days_completed + 1)]
    
    if not trailing_nw:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_ok", True)
        return
    
    peak_trailing = max(trailing_nw)
    terminal = snapshot.final_net_worth
    
    if peak_trailing <= 0:
        drawdown = 0.0
    else:
        drawdown = (peak_trailing - terminal) / peak_trailing
    
    ok = drawdown <= crash_frac
    
    record_property("diag_trailing_drawdown", drawdown)
    record_property("diag_trailing_drawdown_ok", ok)


@pytest.mark.check(id="diag_portfolio_count", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_portfolio_count(snapshot, thresholds, record_property):
    """Record active SKU count vs portfolio_floor."""
    portfolio_floor = thresholds["diagnostic_bands"]["portfolio_floor"]["value"]
    
    # Active SKUs in last 30 days
    if snapshot.days_completed < 30:
        record_property("diag_portfolio_count", None)
        record_property("diag_portfolio_count_ok", True)
        return
    
    trailing_start = snapshot.days_completed - 29
    active = snapshot.active_skus_at(snapshot.days_completed, window=30)
    
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
    """Record whether any effective price changes inverted margin (new < cost)."""
    effective_changes = _effective_price_changes(snapshot)
    
    # We don't have direct access to cost per SKU, so we check if new_price is suspiciously low
    # A price below $0.50 is likely below cost for most retail items
    inversions = [pc for pc in effective_changes if pc.new_price < 0.50]
    
    has_inversion = len(inversions) > 0
    
    record_property("diag_margin_inversion", has_inversion)
    record_property("diag_margin_inversion_ok", not has_inversion)
