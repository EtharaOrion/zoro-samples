"""Deterministic pytest layer for task d0f8ad74-049d-5646-baf6-430dc680c4bb."""

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
    """An order is effective if it placed units and was not an insufficient-funds no-op."""
    return order.order_id is not None and order.units > 0 and order.error is None


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
    """Map day -> capital deployed that day."""
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
    """Verify the run's config matches the frozen task config."""
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
    
    # Categories: compare as normalized lists
    if not hasattr(snapshot.config, "selected_categories"):
        raise RuntimeError("Required config field 'selected_categories' missing from loader")
    
    actual_cats = snapshot.config.selected_categories
    frozen_cats_list = frozen["selected_categories_list"]
    
    # Normalize: replace underscores with spaces for comparison
    actual_normalized = sorted([c.replace('_', ' ') for c in actual_cats])
    frozen_normalized = sorted([c.replace('_', ' ') for c in frozen_cats_list])
    
    assert actual_normalized == frozen_normalized, \
        f"Category mismatch: {actual_normalized} != {frozen_normalized}"


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
    
    # Horizon-pinned net worth: adjust for unfinished days
    days_short = max(0, days_requested - snapshot.days_completed)
    horizon_pinned_nw = snapshot.final_net_worth - rent * days_short
    
    # Reference gain
    ref = oracle_nw - funds
    
    # Guard against near-infeasible tasks
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
    """All tool names used are in the valid tool registry."""
    observed = set()
    for day_calls in snapshot.tool_calls_by_day.values():
        for call in day_calls:
            observed.add(call.tool)
    
    invalid = observed - set(VALID_TOOLS)
    assert len(invalid) == 0, f"Invalid tools used: {invalid}"


@pytest.mark.check(id="supplier_board_before_order", weight=1.5, knockout=False, category="supplier", kind="process")
def test_supplier_board_before_order(snapshot, thresholds):
    """Of all place_order calls, fraction whose SKUs were covered by same-day supplier board read."""
    T_supplier = thresholds["process_thresholds"]["T_supplier"]["value"]
    
    order_calls = []
    for day, calls in snapshot.tool_calls_by_day.items():
        for call in calls:
            if call.tool == "place_order":
                order_calls.append((day, call))
    
    if len(order_calls) == 0:
        # Non-operation: no orders placed
        assert False, "No orders placed (non-operation)"
    
    covered = 0
    for day, call in order_calls:
        # Extract SKUs from the order
        order_skus = set()
        if "skus" in call.args and isinstance(call.args["skus"], list):
            order_skus = set(call.args["skus"])
        
        # Check if there was a same-day supplier board read before this order
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        found_board = False
        for earlier_call in day_calls:
            if earlier_call.tool == "view_current_date_supplier_prices":
                found_board = True
                break
            if earlier_call is call:
                break
        
        if found_board:
            covered += 1
    
    rate = covered / len(order_calls)
    assert rate >= T_supplier, f"Supplier board coverage {rate:.2%} < {T_supplier:.2%}"


@pytest.mark.check(id="view_orders_before_place", weight=1.0, knockout=False, category="reorder", kind="process")
def test_view_orders_before_place(snapshot, thresholds):
    """Of order-days, fraction with an earlier same-day view_current_orders."""
    T_vieworders = thresholds["process_thresholds"]["T_vieworders"]["value"]
    
    order_days = set()
    for day, calls in snapshot.tool_calls_by_day.items():
        for call in calls:
            if call.tool == "place_order":
                order_days.add(day)
    
    if len(order_days) == 0:
        # Non-operation
        assert False, "No order days (non-operation)"
    
    covered = 0
    for day in order_days:
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        found_view = False
        found_order = False
        for call in day_calls:
            if call.tool == "view_current_orders":
                found_view = True
            if call.tool == "place_order":
                found_order = True
                if found_view:
                    covered += 1
                    break
    
    rate = covered / len(order_days)
    assert rate >= T_vieworders, f"View-orders-before-place rate {rate:.2%} < {T_vieworders:.2%}"


@pytest.mark.check(id="day1_order_placed", weight=1.5, knockout=False, category="setup", kind="process")
def test_day1_order_placed(snapshot, thresholds):
    """A material opening order within the first 3 days."""
    grace = 3
    
    for order in snapshot.orders_placed:
        if order.day <= grace and _is_effective_order(order) and order.units > 1:
            return  # Found a material opening order
    
    assert False, "No material opening order within first 3 days"


@pytest.mark.check(id="day1_supplier_read_before_order", weight=0.5, knockout=False, category="setup", kind="process")
def test_day1_supplier_read_before_order(snapshot, thresholds):
    """If a day-1 order exists, a day-1 supplier board read precedes it."""
    day1_calls = snapshot.tool_calls_by_day.get(1, [])
    
    found_order = False
    found_board_before_order = False
    
    for call in day1_calls:
        if call.tool == "view_current_date_supplier_prices":
            found_board_before_order = True
        if call.tool == "place_order":
            found_order = True
            break
    
    if not found_order:
        # No day-1 order: vacuous pass
        return
    
    assert found_board_before_order, "Day-1 order exists but no supplier board read precedes it"


@pytest.mark.check(id="priced_before_first_sale", weight=1.0, knockout=False, category="setup", kind="process")
def test_priced_before_first_sale(snapshot, thresholds):
    """An effective price change on or before the first day with nonzero sales."""
    first_sale_day = None
    for day in sorted(snapshot.sales_units_by_day.keys()):
        if snapshot.sales_units_by_day[day] > 0:
            first_sale_day = day
            break
    
    if first_sale_day is None:
        # No sales at all: non-operation
        assert False, "No sales (non-operation)"
    
    for pc in snapshot.price_changes:
        if pc.day <= first_sale_day:
            if pc.old_price is None or abs(pc.new_price - pc.old_price) > 1e-9:
                return  # Found an effective price change
    
    assert False, f"No effective price change on or before first sale day {first_sale_day}"


@pytest.mark.check(id="reorder_after_stockout", weight=1.0, knockout=False, category="reorder", kind="process")
def test_reorder_after_stockout(snapshot, thresholds):
    """Of stockout events, fraction refilled by an effective order within 7 days."""
    T_reorder = thresholds["process_thresholds"]["T_reorder"]["value"]
    
    if len(snapshot.stockout_events) == 0:
        # No stockouts: vacuous pass
        return
    
    refilled = 0
    for stockout in snapshot.stockout_events:
        sku = stockout.sku
        day = stockout.day
        
        # Verify sku is a bare numeric id
        if not isinstance(sku, str) or not sku.isdigit():
            raise RuntimeError(f"Stockout SKU is not a bare numeric id: {sku}")
        
        # Check for an effective order of this SKU within 7 days
        found = False
        for order in snapshot.orders_by_sku(sku):
            if day < order.day <= day + 7 and _is_effective_order(order):
                found = True
                break
        
        if found:
            refilled += 1
    
    rate = refilled / len(snapshot.stockout_events)
    assert rate >= T_reorder, f"Reorder-after-stockout rate {rate:.2%} < {T_reorder:.2%}"


@pytest.mark.check(id="no_prolonged_order_drought", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_prolonged_order_drought(snapshot, thresholds):
    """No window of drought_len days (before trailing taper) with low deployment and high idle cash."""
    drought_len = thresholds["process_thresholds"]["drought_len"]["value"]
    deploy_dollars_min = thresholds["process_thresholds"]["deploy_dollars_min"]["value"]
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    
    taper = 15
    last_eval_day = snapshot.days_completed - taper
    
    capital_by_day = _capital_by_day(snapshot)
    
    for start_day in range(1, last_eval_day - drought_len + 2):
        end_day = start_day + drought_len - 1
        
        # Capital deployed in this window
        window_capital = sum(capital_by_day.get(d, 0.0) for d in range(start_day, end_day + 1))
        
        # Mean idle funds in this window
        window_funds = [snapshot.end_of_day_funds.get(d, 0.0) for d in range(start_day, end_day + 1)]
        mean_funds = mean(window_funds) if window_funds else 0.0
        
        if window_capital < deploy_dollars_min and mean_funds > cash_idle:
            assert False, f"Order drought: days {start_day}-{end_day}, deployed ${window_capital:.0f} < ${deploy_dollars_min:.0f}, idle ${mean_funds:.0f} > ${cash_idle:.0f}"


@pytest.mark.check(id="no_cash_paralysis", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_cash_paralysis(snapshot, thresholds):
    """No 31-day window (excluding trailing taper) with high idle cash, low growth, and low deployment."""
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    stall_frac = thresholds["outcome_thresholds"]["stall_frac"]["value"]
    paralysis_deploy_dollars = thresholds["process_thresholds"]["paralysis_deploy_dollars"]["value"]
    
    window_len = 31
    taper = 15
    last_eval_day = snapshot.days_completed - taper
    
    capital_by_day = _capital_by_day(snapshot)
    
    for start_day in range(1, last_eval_day - window_len + 2):
        end_day = start_day + window_len - 1
        
        # Mean idle funds
        window_funds = [snapshot.end_of_day_funds.get(d, 0.0) for d in range(start_day, end_day + 1)]
        mean_funds = mean(window_funds) if window_funds else 0.0
        
        # Net worth growth
        nw_start = snapshot.end_of_day_nw.get(start_day, 0.0)
        nw_end = snapshot.end_of_day_nw.get(end_day, 0.0)
        growth = nw_end - nw_start
        
        # Capital deployed
        window_capital = sum(capital_by_day.get(d, 0.0) for d in range(start_day, end_day + 1))
        
        if mean_funds > cash_idle and growth < stall_frac and window_capital < paralysis_deploy_dollars:
            assert False, f"Cash paralysis: days {start_day}-{end_day}, idle ${mean_funds:.0f}, growth ${growth:.0f}, deployed ${window_capital:.0f}"


@pytest.mark.check(id="low_signal_drift_bounded", weight=2.0, knockout=False, category="meta", kind="process")
def test_low_signal_drift_bounded(snapshot, thresholds):
    """Drift (non-action calls) / dollars deployed <= R_lowsignal."""
    R_lowsignal = thresholds["process_thresholds"]["R_lowsignal"]["value"]
    
    # Total calls
    total_calls = sum(len(calls) for calls in snapshot.tool_calls_by_day.values())
    
    # Effective orders
    effective_orders = sum(1 for o in snapshot.orders_placed if _is_effective_order(o))
    
    # Effective price changes
    effective_prices = _effective_price_changes(snapshot)
    
    # end_today calls
    end_today_calls = snapshot.tool_call_count("end_today")
    
    # Drift = complement of effective actions and end_today
    drift = total_calls - effective_orders - effective_prices - end_today_calls
    
    # Dollars deployed
    dollars_deployed = _deployed_total(snapshot)
    
    if dollars_deployed == 0:
        # Non-operation
        assert False, "Zero dollars deployed (non-operation)"
    
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
    
    multiple = snapshot.final_net_worth / funds if funds > 0 else 0.0
    would_pass = multiple >= K_strong
    
    record_property("diag_terminal_growth_multiple", multiple)
    record_property("diag_terminal_growth_multiple_ok", would_pass)


@pytest.mark.check(id="diag_terminal_near_peak", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_terminal_near_peak(snapshot, thresholds, record_property):
    """Record whether terminal NW is near peak (within crash_frac)."""
    crash_frac = thresholds["diagnostic_bands"]["crash_frac"]["value"]
    
    if len(snapshot.end_of_day_nw) == 0:
        record_property("diag_terminal_near_peak", None)
        record_property("diag_terminal_near_peak_ok", True)
        return
    
    peak_nw = max(snapshot.end_of_day_nw.values())
    terminal_nw = snapshot.final_net_worth
    
    drawdown = peak_nw - terminal_nw
    would_pass = drawdown <= crash_frac
    
    record_property("diag_terminal_near_peak_drawdown", drawdown)
    record_property("diag_terminal_near_peak_ok", would_pass)


@pytest.mark.check(id="diag_trailing_drawdown", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_trailing_drawdown(snapshot, thresholds, record_property):
    """Record trailing drawdown from recent peak."""
    crash_frac = thresholds["diagnostic_bands"]["crash_frac"]["value"]
    
    trailing_window = 30
    if snapshot.days_completed < trailing_window:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_ok", True)
        return
    
    recent_start = snapshot.days_completed - trailing_window + 1
    recent_nw = [snapshot.end_of_day_nw.get(d, 0.0) for d in range(recent_start, snapshot.days_completed + 1)]
    
    if not recent_nw:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_ok", True)
        return
    
    peak = max(recent_nw)
    terminal = snapshot.final_net_worth
    drawdown = peak - terminal
    would_pass = drawdown <= crash_frac
    
    record_property("diag_trailing_drawdown", drawdown)
    record_property("diag_trailing_drawdown_ok", would_pass)


@pytest.mark.check(id="diag_portfolio_count", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_portfolio_count(snapshot, thresholds, record_property):
    """Record active SKU count vs portfolio_floor."""
    portfolio_floor = thresholds["diagnostic_bands"]["portfolio_floor"]["value"]
    
    # Active SKUs in the last 30 days
    active = snapshot.active_skus_at(snapshot.days_completed, window=30)
    count = len(active)
    would_pass = count >= portfolio_floor
    
    record_property("diag_portfolio_count", count)
    record_property("diag_portfolio_count_ok", would_pass)


@pytest.mark.check(id="diag_return_rate", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_return_rate(snapshot, thresholds, record_property):
    """Record return rate vs return_rate_ref."""
    return_rate_ref = thresholds["diagnostic_bands"]["return_rate_ref"]["value"]
    
    rate = snapshot.run_return_rate()
    if rate is None:
        record_property("diag_return_rate", None)
        record_property("diag_return_rate_ok", True)
        return
    
    would_pass = rate <= return_rate_ref
    record_property("diag_return_rate", rate)
    record_property("diag_return_rate_ok", would_pass)


@pytest.mark.check(id="diag_spoilage_rate", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_spoilage_rate(snapshot, thresholds, record_property):
    """Record spoilage rate vs spoilage_ref."""
    spoilage_ref = thresholds["diagnostic_bands"]["spoilage_ref"]["value"]
    
    rate = snapshot.run_spoilage_rate()
    if rate is None:
        record_property("diag_spoilage_rate", None)
        record_property("diag_spoilage_rate_ok", True)
        return
    
    would_pass = rate <= spoilage_ref
    record_property("diag_spoilage_rate", rate)
    record_property("diag_spoilage_rate_ok", would_pass)


@pytest.mark.check(id="diag_margin_inversion", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_margin_inversion(snapshot, thresholds, record_property):
    """Record whether margin inverted (terminal NW < opening funds)."""
    funds = thresholds["config"]["initial_funds"]
    
    inverted = snapshot.final_net_worth < funds
    record_property("diag_margin_inversion", inverted)
    record_property("diag_margin_inversion_ok", not inverted)
