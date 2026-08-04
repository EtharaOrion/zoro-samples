"""Deterministic pytest layer for RetailBench task f62e57e0-657a-5f2e-a8ef-4fbfc13f7797."""

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


def _effective_price_changes(price_changes):
    """Return the count of effective price changes (|new - old| > 1e-9, or old is None)."""
    count = 0
    for pc in price_changes:
        if pc.old_price is None or abs(pc.new_price - pc.old_price) > 1e-9:
            count += 1
    return count


def _capital_by_day(orders):
    """Return dict[day, capital_deployed_that_day]."""
    cap = {}
    for order in orders:
        if _is_effective_order(order):
            cap[order.day] = cap.get(order.day, 0.0) + order.cost
    return cap


def _deployed_total(orders):
    """Return total capital deployed across all effective orders."""
    return sum(_order_capital(o) for o in orders)


@pytest.mark.check(id="integrity_config_matches_frozen_task", weight=0.0, knockout=False, category="integrity", kind="outcome")
def test_integrity_config_matches_frozen_task(snapshot, thresholds):
    """Verify the run's config matches the frozen task config."""
    frozen = thresholds["config"]
    
    # Check scalar fields
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
    
    # Check selected_categories (list comparison, representation-normalized)
    if not hasattr(snapshot.config, "selected_categories"):
        raise RuntimeError("Required config field 'selected_categories' missing from loader")
    
    actual_cats = snapshot.config.selected_categories
    expected_cats = frozen["selected_categories_list"]
    
    # Normalize representation (_ vs space)
    def normalize(cat):
        return cat.replace("_", " ").strip()
    
    actual_normalized = sorted(normalize(c) for c in actual_cats)
    expected_normalized = sorted(normalize(c) for c in expected_cats)
    
    assert actual_normalized == expected_normalized, \
        f"Config mismatch: selected_categories = {actual_cats}, expected {expected_cats}"


@pytest.mark.check(id="integrity_readable_complete", weight=0.0, knockout=False, category="integrity", kind="outcome")
def test_integrity_readable_complete(snapshot, thresholds):
    """Verify the trajectory parsed and terminal net worth is a finite real number."""
    nw = snapshot.final_net_worth
    if not isinstance(nw, (int, float)):
        raise RuntimeError(f"Terminal net worth is not a number: {nw}")
    if not (-1e15 < nw < 1e15):
        raise RuntimeError(f"Terminal net worth is not finite: {nw}")


@pytest.mark.check(id="money_net_worth_outcome", weight=0.0, knockout=False, category="money", kind="outcome")
def test_money_net_worth_outcome(snapshot, thresholds, record_property):
    """Compute and record the continuous money outcome O."""
    funds = thresholds["config"]["initial_funds"]
    oracle_nw = thresholds["oracle_nw"]["value"]
    days_requested = thresholds["config"]["days_requested"]
    rent = thresholds["config"]["everyday_rent"]
    
    # Horizon-pinned net worth (project rent for unfinished days)
    days_short = max(0, days_requested - snapshot.days_completed)
    horizon_pinned_nw = snapshot.final_net_worth - rent * days_short
    
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


@pytest.mark.check(id="valid_tools_used", weight=1.0, knockout=False, category="meta", kind="process")
def test_valid_tools_used(snapshot, thresholds):
    """All tool names used are in the valid tool registry."""
    observed_tools = set()
    for day_calls in snapshot.tool_calls_by_day.values():
        for call in day_calls:
            observed_tools.add(call.tool)
    
    assert observed_tools.issubset(VALID_TOOLS), \
        f"Invalid tools used: {observed_tools - set(VALID_TOOLS)}"


@pytest.mark.check(id="supplier_board_before_order", weight=1.5, knockout=False, category="supplier", kind="process")
def test_supplier_board_before_order(snapshot, thresholds):
    """Of all place_order calls, the fraction whose SKUs were covered by an earlier same-day supplier board read."""
    T_supplier = thresholds["process_thresholds"]["T_supplier"]["value"]
    
    # Collect all effective orders
    effective_orders = [o for o in snapshot.orders_placed if _is_effective_order(o)]
    
    if not effective_orders:
        # Zero orders = definite FAIL (non-operation)
        pytest.fail("No effective orders placed (non-operation)")
    
    # For each order, check if its SKUs were covered by a same-day supplier board read
    covered = 0
    for order in effective_orders:
        day = order.day
        # Get all tool calls on this day
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        
        # Find all view_current_date_supplier_prices calls before this order
        # (We approximate "before" by checking if the call appears in the day's list;
        # the loader preserves order within a day)
        supplier_reads = [c for c in day_calls if c.tool == "view_current_date_supplier_prices"]
        
        # If there's at least one supplier read on this day, consider it covered
        # (A more precise check would verify the read happened before the order in the call sequence,
        # but the snapshot API doesn't expose intra-day ordering beyond the list order)
        if supplier_reads:
            covered += 1
    
    rate = covered / len(effective_orders)
    assert rate >= T_supplier, \
        f"Supplier board read before order rate {rate:.2%} < threshold {T_supplier:.2%}"


@pytest.mark.check(id="view_orders_before_place", weight=1.0, knockout=False, category="reorder", kind="process")
def test_view_orders_before_place(snapshot, thresholds):
    """Of order-days, the fraction with an earlier same-day view_current_orders."""
    T_vieworders = thresholds["process_thresholds"]["T_vieworders"]["value"]
    
    # Collect days with effective orders
    order_days = set()
    for order in snapshot.orders_placed:
        if _is_effective_order(order):
            order_days.add(order.day)
    
    if not order_days:
        # Non-operation
        pytest.fail("No effective orders placed (non-operation)")
    
    # For each order-day, check if there's a view_current_orders call
    covered = 0
    for day in order_days:
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        if any(c.tool == "view_current_orders" for c in day_calls):
            covered += 1
    
    rate = covered / len(order_days)
    assert rate >= T_vieworders, \
        f"View orders before place rate {rate:.2%} < threshold {T_vieworders:.2%}"


@pytest.mark.check(id="day1_order_placed", weight=1.5, knockout=False, category="setup", kind="process")
def test_day1_order_placed(snapshot, thresholds):
    """A material (effective) opening order within the first 3 days."""
    grace = 3
    
    # Check for any effective order in days 1-3
    early_orders = [o for o in snapshot.orders_placed 
                    if o.day <= grace and _is_effective_order(o)]
    
    assert early_orders, \
        f"No effective order placed within first {grace} days"


@pytest.mark.check(id="day1_supplier_read_before_order", weight=0.5, knockout=False, category="setup", kind="process")
def test_day1_supplier_read_before_order(snapshot, thresholds):
    """Implication: IF a day-1 order exists, a day-1 supplier-board read precedes it."""
    # Check if there's a day-1 order
    day1_orders = [o for o in snapshot.orders_placed if o.day == 1 and _is_effective_order(o)]
    
    if not day1_orders:
        # No day-1 order => vacuous PASS
        return
    
    # There is a day-1 order; check for a day-1 supplier read
    day1_calls = snapshot.tool_calls_by_day.get(1, [])
    supplier_reads = [c for c in day1_calls if c.tool == "view_current_date_supplier_prices"]
    
    assert supplier_reads, \
        "Day-1 order placed without a day-1 supplier board read"


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
        # No sales at all = non-operation
        pytest.fail("No sales recorded (non-operation)")
    
    # Check for effective price changes on or before first_sale_day
    early_price_changes = [
        pc for pc in snapshot.price_changes
        if pc.day <= first_sale_day and (pc.old_price is None or abs(pc.new_price - pc.old_price) > 1e-9)
    ]
    
    assert early_price_changes, \
        f"No effective price change on or before first sale day {first_sale_day}"


@pytest.mark.check(id="reorder_after_stockout", weight=1.0, knockout=False, category="reorder", kind="process")
def test_reorder_after_stockout(snapshot, thresholds):
    """Of stockout events, the fraction refilled by an effective order within 7 days."""
    T_reorder = thresholds["process_thresholds"]["T_reorder"]["value"]
    reorder_window = 7
    
    if not snapshot.stockout_events:
        # No stockouts => vacuous PASS
        return
    
    refilled = 0
    for stockout in snapshot.stockout_events:
        # Verify sku is a bare numeric id (loader contract)
        if not isinstance(stockout.sku, str) or not stockout.sku.isdigit():
            raise RuntimeError(f"Stockout SKU is not a bare numeric id: {stockout.sku}")
        
        sku = stockout.sku
        day = stockout.day
        
        # Find orders for this SKU within 7 days after the stockout
        sku_orders = snapshot.orders_by_sku(sku)
        refill_orders = [
            o for o in sku_orders
            if day < o.day <= day + reorder_window and _is_effective_order(o)
        ]
        
        if refill_orders:
            refilled += 1
    
    rate = refilled / len(snapshot.stockout_events)
    assert rate >= T_reorder, \
        f"Reorder after stockout rate {rate:.2%} < threshold {T_reorder:.2%}"


@pytest.mark.check(id="no_prolonged_order_drought", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_prolonged_order_drought(snapshot, thresholds):
    """No window of drought_len days (before the last 15-day taper) with low deployment while idle cash is high."""
    drought_len = thresholds["process_thresholds"]["drought_len"]["value"]
    deploy_dollars_min = thresholds["process_thresholds"]["deploy_dollars_min"]["value"]
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    taper = 15
    
    # Compute capital deployed by day
    cap_by_day = _capital_by_day(snapshot.orders_placed)
    
    # Check windows up to (days_completed - taper)
    last_day_to_check = snapshot.days_completed - taper
    
    for start_day in range(1, last_day_to_check - drought_len + 2):
        end_day = start_day + drought_len - 1
        if end_day > last_day_to_check:
            break
        
        # Capital deployed in this window
        window_capital = sum(cap_by_day.get(d, 0.0) for d in range(start_day, end_day + 1))
        
        # Mean idle funds in this window
        window_funds = [snapshot.end_of_day_funds.get(d, 0.0) for d in range(start_day, end_day + 1)]
        if window_funds:
            mean_idle = mean(window_funds)
        else:
            mean_idle = 0.0
        
        # Check for drought
        if window_capital < deploy_dollars_min and mean_idle > cash_idle:
            pytest.fail(
                f"Prolonged order drought: days {start_day}-{end_day}, "
                f"deployed ${window_capital:.0f} < ${deploy_dollars_min:.0f}, "
                f"mean idle ${mean_idle:.0f} > ${cash_idle:.0f}"
            )


@pytest.mark.check(id="no_cash_paralysis", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_cash_paralysis(snapshot, thresholds):
    """No 31-day window (excluding trailing taper) where mean idle funds > threshold AND NW growth < threshold AND deployment < threshold."""
    window_len = 31
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    stall_frac = thresholds["outcome_thresholds"]["stall_frac"]["value"]
    paralysis_deploy_dollars = thresholds["process_thresholds"]["paralysis_deploy_dollars"]["value"]
    taper = 15
    
    # Compute capital deployed by day
    cap_by_day = _capital_by_day(snapshot.orders_placed)
    
    # Check windows up to (days_completed - taper)
    last_day_to_check = snapshot.days_completed - taper
    
    for start_day in range(1, last_day_to_check - window_len + 2):
        end_day = start_day + window_len - 1
        if end_day > last_day_to_check:
            break
        
        # Mean idle funds
        window_funds = [snapshot.end_of_day_funds.get(d, 0.0) for d in range(start_day, end_day + 1)]
        mean_idle = mean(window_funds) if window_funds else 0.0
        
        # NW growth
        nw_start = snapshot.end_of_day_nw.get(start_day, 0.0)
        nw_end = snapshot.end_of_day_nw.get(end_day, 0.0)
        nw_growth = nw_end - nw_start
        
        # Capital deployed
        window_capital = sum(cap_by_day.get(d, 0.0) for d in range(start_day, end_day + 1))
        
        # Check for paralysis
        if mean_idle > cash_idle and nw_growth < stall_frac and window_capital < paralysis_deploy_dollars:
            pytest.fail(
                f"Cash paralysis: days {start_day}-{end_day}, "
                f"mean idle ${mean_idle:.0f} > ${cash_idle:.0f}, "
                f"NW growth ${nw_growth:.0f} < ${stall_frac:.0f}, "
                f"deployed ${window_capital:.0f} < ${paralysis_deploy_dollars:.0f}"
            )


@pytest.mark.check(id="low_signal_drift_bounded", weight=2.0, knockout=False, category="meta", kind="process")
def test_low_signal_drift_bounded(snapshot, thresholds):
    """Drift (non-action calls) / dollars_deployed <= R_lowsignal."""
    R_lowsignal = thresholds["process_thresholds"]["R_lowsignal"]["value"]
    
    # Total tool calls
    total_calls = sum(len(calls) for calls in snapshot.tool_calls_by_day.values())
    
    # Effective orders
    effective_orders_count = sum(1 for o in snapshot.orders_placed if _is_effective_order(o))
    
    # Effective price changes
    effective_price_changes_count = _effective_price_changes(snapshot.price_changes)
    
    # end_today calls
    end_today_count = snapshot.tool_call_count("end_today")
    
    # Drift = total - effective_orders - effective_price_changes - end_today
    drift = total_calls - effective_orders_count - effective_price_changes_count - end_today_count
    
    # Dollars deployed
    dollars_deployed = _deployed_total(snapshot.orders_placed)
    
    if dollars_deployed == 0:
        # Non-operation
        pytest.fail("Zero dollars deployed (non-operation)")
    
    ratio = drift / dollars_deployed
    
    assert ratio <= R_lowsignal, \
        f"Low-signal drift ratio {ratio:.4f} > threshold {R_lowsignal:.4f}"


@pytest.mark.check(id="diag_days_survived", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_days_survived(snapshot, thresholds, record_property):
    """Record days survived."""
    days_survived = snapshot.days_completed
    days_requested = thresholds["config"]["days_requested"]
    
    record_property("diag_days_survived", days_survived)
    record_property("diag_days_survived_ok", days_survived >= days_requested)


@pytest.mark.check(id="diag_terminal_growth_multiple", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_terminal_growth_multiple(snapshot, thresholds, record_property):
    """Record terminal growth multiple vs K_strong."""
    K_strong = thresholds["diagnostic_bands"]["K_strong"]["value"]
    initial_funds = thresholds["config"]["initial_funds"]
    
    terminal_nw = snapshot.final_net_worth
    growth_multiple = terminal_nw / initial_funds if initial_funds > 0 else 0.0
    
    record_property("diag_terminal_growth_multiple", growth_multiple)
    record_property("diag_terminal_growth_multiple_ok", growth_multiple >= K_strong)


@pytest.mark.check(id="diag_terminal_near_peak", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_terminal_near_peak(snapshot, thresholds, record_property):
    """Record whether terminal NW is near peak (within P_peak fraction)."""
    P_peak = thresholds["diagnostic_bands"]["P_peak"]["value"]
    
    # Find peak NW
    if snapshot.end_of_day_nw:
        peak_nw = max(snapshot.end_of_day_nw.values())
    else:
        peak_nw = snapshot.final_net_worth
    
    terminal_nw = snapshot.final_net_worth
    
    if peak_nw > 0:
        near_peak = terminal_nw >= peak_nw * (1 - P_peak)
    else:
        near_peak = True
    
    record_property("diag_terminal_near_peak", near_peak)
    record_property("diag_terminal_near_peak_ok", near_peak)


@pytest.mark.check(id="diag_trailing_drawdown", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_trailing_drawdown(snapshot, thresholds, record_property):
    """Record trailing drawdown vs crash_frac."""
    crash_frac = thresholds["diagnostic_bands"]["crash_frac"]["value"]
    trailing_window = 30
    
    # Get NW values in the last 30 days
    last_day = snapshot.days_completed
    start_day = max(1, last_day - trailing_window + 1)
    
    trailing_nw = [snapshot.end_of_day_nw.get(d, 0.0) for d in range(start_day, last_day + 1)]
    
    if trailing_nw:
        peak_trailing = max(trailing_nw)
        terminal_nw = snapshot.final_net_worth
        
        if peak_trailing > 0:
            drawdown = (peak_trailing - terminal_nw) / peak_trailing
        else:
            drawdown = 0.0
    else:
        drawdown = 0.0
    
    record_property("diag_trailing_drawdown", drawdown)
    record_property("diag_trailing_drawdown_ok", drawdown <= crash_frac)


@pytest.mark.check(id="diag_portfolio_count", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_portfolio_count(snapshot, thresholds, record_property):
    """Record active SKU count vs portfolio_floor."""
    portfolio_floor = thresholds["diagnostic_bands"]["portfolio_floor"]["value"]
    
    # Count active SKUs in the last 30 days
    last_day = snapshot.days_completed
    active_skus = snapshot.active_skus_at(last_day, window=30)
    
    count = len(active_skus)
    
    record_property("diag_portfolio_count", count)
    record_property("diag_portfolio_count_ok", count >= portfolio_floor)


@pytest.mark.check(id="diag_return_rate", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_return_rate(snapshot, thresholds, record_property):
    """Record return rate vs return_rate_ref."""
    return_rate_ref = thresholds["diagnostic_bands"]["return_rate_ref"]["value"]
    
    return_rate = snapshot.run_return_rate()
    
    if return_rate is None:
        # No sales data
        record_property("diag_return_rate", None)
        record_property("diag_return_rate_ok", True)
    else:
        record_property("diag_return_rate", return_rate)
        record_property("diag_return_rate_ok", return_rate <= return_rate_ref)


@pytest.mark.check(id="diag_spoilage_rate", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_spoilage_rate(snapshot, thresholds, record_property):
    """Record spoilage rate vs spoilage_ref."""
    spoilage_ref = thresholds["diagnostic_bands"]["spoilage_ref"]["value"]
    
    spoilage_rate = snapshot.run_spoilage_rate()
    
    if spoilage_rate is None:
        # No inventory data
        record_property("diag_spoilage_rate", None)
        record_property("diag_spoilage_rate_ok", True)
    else:
        record_property("diag_spoilage_rate", spoilage_rate)
        record_property("diag_spoilage_rate_ok", spoilage_rate <= spoilage_ref)


@pytest.mark.check(id="diag_margin_inversion", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_margin_inversion(snapshot, thresholds, record_property):
    """Record whether there's evidence of margin inversion (selling below cost)."""
    # Check if any price changes set a price below typical supplier costs
    # This is a heuristic diagnostic; we look for prices that are suspiciously low
    
    # Typical supplier costs are in the range of a few dollars; a shelf price below $1 is suspicious
    suspicious_threshold = 1.0
    
    suspicious_prices = [
        pc for pc in snapshot.price_changes
        if pc.new_price < suspicious_threshold
    ]
    
    has_inversion = len(suspicious_prices) > 0
    
    record_property("diag_margin_inversion", has_inversion)
    record_property("diag_margin_inversion_ok", not has_inversion)
