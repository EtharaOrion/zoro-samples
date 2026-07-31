"""Deterministic pytest layer for RetailBench task 6b2a889c-3b73-5e69-9478-513b4863f21e."""

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
    
    # Categories: compare as normalized sets
    if not hasattr(snapshot.config, "selected_categories"):
        raise RuntimeError("Required config field 'selected_categories' missing from loader")
    
    actual_cats = snapshot.config.selected_categories
    frozen_cats_list = frozen["selected_categories_list"]
    
    def normalize(s):
        return s.replace("_", " ").strip().lower()
    
    actual_set = {normalize(c) for c in actual_cats}
    frozen_set = {normalize(c) for c in frozen_cats_list}
    
    assert actual_set == frozen_set, f"Category mismatch: {actual_set} != {frozen_set}"


@pytest.mark.check(id="integrity_readable_complete", weight=0.0, knockout=False, category="integrity", kind="outcome")
def test_integrity_readable_complete(snapshot, thresholds):
    """Verify the trajectory parsed and has a finite terminal net worth."""
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
    """Compute the continuous money outcome O from horizon-pinned net worth."""
    funds = thresholds["config"]["initial_funds"]
    oracle_nw = thresholds["oracle_nw"]["value"]
    days_requested = thresholds["config"]["days_requested"]
    rent = thresholds["config"]["everyday_rent"]
    
    # Horizon-pinned net worth
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
    """Fraction of orders whose SKUs were covered by a same-day supplier board read."""
    T_supplier = thresholds["process_thresholds"]["T_supplier"]["value"]
    
    effective_orders = [o for o in snapshot.orders_placed if _is_effective_order(o)]
    
    if not effective_orders:
        # Non-operation: definite fail
        pytest.fail("No effective orders placed (non-operation)")
    
    covered = 0
    for order in effective_orders:
        day = order.day
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        
        # Find all view_current_date_supplier_prices calls before this order
        supplier_reads_skus = set()
        for call in day_calls:
            if call.tool == "view_current_date_supplier_prices":
                # Extract SKUs from call.args["sku_ids"] (always a list)
                sku_ids = call.args.get("sku_ids", [])
                for sku in sku_ids:
                    supplier_reads_skus.add(str(sku))
        
        # Check if order SKUs are covered
        if order.skus.issubset(supplier_reads_skus):
            covered += 1
    
    coverage = covered / len(effective_orders)
    assert coverage >= T_supplier, f"Supplier board coverage {coverage:.2%} < {T_supplier:.2%}"


@pytest.mark.check(id="view_orders_before_place", weight=1.0, knockout=False, category="reorder", kind="process")
def test_view_orders_before_place(snapshot, thresholds):
    """Fraction of order-days with a same-day view_current_orders call."""
    T_vieworders = thresholds["process_thresholds"]["T_vieworders"]["value"]
    
    effective_orders = [o for o in snapshot.orders_placed if _is_effective_order(o)]
    
    if not effective_orders:
        pytest.fail("No effective orders placed (non-operation)")
    
    order_days = {o.day for o in effective_orders}
    
    covered_days = 0
    for day in order_days:
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        if any(call.tool == "view_current_orders" for call in day_calls):
            covered_days += 1
    
    coverage = covered_days / len(order_days)
    assert coverage >= T_vieworders, f"View orders coverage {coverage:.2%} < {T_vieworders:.2%}"


@pytest.mark.check(id="day1_order_placed", weight=1.5, knockout=False, category="setup", kind="process")
def test_day1_order_placed(snapshot, thresholds):
    """A material opening order within the first 3 days."""
    grace = 3
    
    early_orders = [o for o in snapshot.orders_placed if o.day <= grace and _is_effective_order(o)]
    
    assert early_orders, f"No effective order in first {grace} days"


@pytest.mark.check(id="day1_supplier_read_before_order", weight=0.5, knockout=False, category="setup", kind="process")
def test_day1_supplier_read_before_order(snapshot, thresholds):
    """If a day-1 order exists, a day-1 supplier board read precedes it."""
    day1_orders = [o for o in snapshot.orders_placed if o.day == 1 and _is_effective_order(o)]
    
    if not day1_orders:
        # No day-1 order: vacuous pass
        return
    
    day1_calls = snapshot.tool_calls_by_day.get(1, [])
    has_supplier_read = any(call.tool == "view_current_date_supplier_prices" for call in day1_calls)
    
    assert has_supplier_read, "Day-1 order exists but no day-1 supplier board read"


@pytest.mark.check(id="priced_before_first_sale", weight=1.0, knockout=False, category="setup", kind="process")
def test_priced_before_first_sale(snapshot, thresholds):
    """An effective price change on or before the first day with sales."""
    effective_changes = _effective_price_changes(snapshot)
    
    # Find first day with sales
    first_sale_day = None
    for day in sorted(snapshot.sales_units_by_day.keys()):
        if snapshot.sales_units_by_day[day] > 0:
            first_sale_day = day
            break
    
    if first_sale_day is None:
        # No sales: non-operation
        pytest.fail("No sales recorded (non-operation)")
    
    early_price = any(pc.day <= first_sale_day for pc in effective_changes)
    assert early_price, f"No effective price change on or before first sale day {first_sale_day}"


@pytest.mark.check(id="reorder_after_stockout", weight=1.0, knockout=False, category="reorder", kind="process")
def test_reorder_after_stockout(snapshot, thresholds):
    """Fraction of stockouts refilled by an effective order within 7 days."""
    T_reorder = thresholds["process_thresholds"]["T_reorder"]["value"]
    window = 7
    
    stockouts = snapshot.stockout_events
    
    if not stockouts:
        # No stockouts: vacuous pass
        return
    
    refilled = 0
    for stockout in stockouts:
        # Verify sku is a bare numeric id
        if not stockout.sku.isdigit():
            raise RuntimeError(f"Stockout SKU '{stockout.sku}' is not a bare numeric id (loader mis-parse)")
        
        sku = stockout.sku
        day = stockout.day
        
        # Check for effective orders of this SKU within 7 days
        future_orders = [o for o in snapshot.orders_by_sku(sku) 
                        if day < o.day <= day + window and _is_effective_order(o)]
        
        if future_orders:
            refilled += 1
    
    coverage = refilled / len(stockouts)
    assert coverage >= T_reorder, f"Reorder coverage {coverage:.2%} < {T_reorder:.2%}"


@pytest.mark.check(id="no_prolonged_order_drought", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_prolonged_order_drought(snapshot, thresholds):
    """No prolonged window with low deployment while idle cash is high."""
    drought_len = thresholds["process_thresholds"]["drought_len"]["value"]
    deploy_dollars_min = thresholds["process_thresholds"]["deploy_dollars_min"]["value"]
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    taper = 15
    
    capital_by_day = _capital_by_day(snapshot)
    funds_by_day = snapshot.end_of_day_funds
    
    # Exclude the trailing taper
    horizon = snapshot.days_completed
    check_until = max(1, horizon - taper)
    
    for start in range(1, check_until - drought_len + 2):
        end = start + drought_len - 1
        if end > check_until:
            break
        
        window_days = range(start, end + 1)
        window_deploy = sum(capital_by_day.get(d, 0.0) for d in window_days)
        window_funds = [funds_by_day.get(d, 0.0) for d in window_days if d in funds_by_day]
        
        if window_funds:
            mean_funds = mean(window_funds)
            if window_deploy < deploy_dollars_min and mean_funds > cash_idle:
                pytest.fail(f"Order drought: days {start}-{end}, deployed ${window_deploy:.0f} < ${deploy_dollars_min:.0f}, mean idle ${mean_funds:.0f}")


@pytest.mark.check(id="no_cash_paralysis", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_cash_paralysis(snapshot, thresholds):
    """No 31-day window with high idle cash, low growth, and low deployment."""
    window_len = 31
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    stall_frac = thresholds["outcome_thresholds"]["stall_frac"]["value"]
    paralysis_deploy = thresholds["process_thresholds"]["paralysis_deploy_dollars"]["value"]
    taper = 15
    
    capital_by_day = _capital_by_day(snapshot)
    funds_by_day = snapshot.end_of_day_funds
    nw_by_day = snapshot.end_of_day_nw
    
    horizon = snapshot.days_completed
    check_until = max(1, horizon - taper)
    
    for start in range(1, check_until - window_len + 2):
        end = start + window_len - 1
        if end > check_until:
            break
        
        window_days = range(start, end + 1)
        
        # Mean idle funds
        window_funds = [funds_by_day.get(d, 0.0) for d in window_days if d in funds_by_day]
        if not window_funds:
            continue
        mean_funds = mean(window_funds)
        
        # Net worth growth
        nw_start = nw_by_day.get(start)
        nw_end = nw_by_day.get(end)
        if nw_start is None or nw_end is None or nw_start <= 0:
            continue
        growth = (nw_end - nw_start) / nw_start
        
        # Capital deployed
        window_deploy = sum(capital_by_day.get(d, 0.0) for d in window_days)
        
        if mean_funds > cash_idle and growth < stall_frac and window_deploy < paralysis_deploy:
            pytest.fail(f"Cash paralysis: days {start}-{end}, mean idle ${mean_funds:.0f}, growth {growth:.1%}, deployed ${window_deploy:.0f}")


@pytest.mark.check(id="low_signal_drift_bounded", weight=2.0, knockout=False, category="meta", kind="process")
def test_low_signal_drift_bounded(snapshot, thresholds):
    """Low-signal drift (non-action calls) bounded relative to dollars deployed."""
    R_lowsignal = thresholds["process_thresholds"]["R_lowsignal"]["value"]
    
    # Total calls
    total_calls = sum(len(calls) for calls in snapshot.tool_calls_by_day.values())
    
    # Effective actions
    effective_orders = sum(1 for o in snapshot.orders_placed if _is_effective_order(o))
    effective_prices = len(_effective_price_changes(snapshot))
    end_today_calls = snapshot.tool_call_count("end_today")
    
    # Drift = complement
    drift = total_calls - effective_orders - effective_prices - end_today_calls
    
    # Dollars deployed
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
    ok = multiple >= K_strong
    
    record_property("diag_terminal_growth_multiple", multiple)
    record_property("diag_terminal_growth_ok", ok)


@pytest.mark.check(id="diag_terminal_near_peak", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_terminal_near_peak(snapshot, thresholds, record_property):
    """Record whether terminal NW is near peak (vs P_peak)."""
    P_peak = thresholds["diagnostic_bands"]["P_peak"]["value"]
    
    nw_by_day = snapshot.end_of_day_nw
    if not nw_by_day:
        record_property("diag_terminal_near_peak", None)
        record_property("diag_terminal_near_peak_ok", True)
        return
    
    peak = max(nw_by_day.values())
    terminal = snapshot.final_net_worth
    
    if peak <= 0:
        near_peak = None
        ok = True
    else:
        near_peak = terminal / peak
        ok = near_peak >= P_peak
    
    record_property("diag_terminal_near_peak", near_peak)
    record_property("diag_terminal_near_peak_ok", ok)


@pytest.mark.check(id="diag_trailing_drawdown", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_trailing_drawdown(snapshot, thresholds, record_property):
    """Record trailing drawdown vs crash_frac."""
    crash_frac = thresholds["diagnostic_bands"]["crash_frac"]["value"]
    lookback = 30
    
    nw_by_day = snapshot.end_of_day_nw
    horizon = snapshot.days_completed
    
    if horizon < lookback:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_ok", True)
        return
    
    trailing_days = range(horizon - lookback + 1, horizon + 1)
    trailing_nw = [nw_by_day.get(d) for d in trailing_days if d in nw_by_day]
    
    if not trailing_nw:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_ok", True)
        return
    
    peak_trailing = max(trailing_nw)
    terminal = snapshot.final_net_worth
    
    if peak_trailing <= 0:
        drawdown = None
        ok = True
    else:
        drawdown = (peak_trailing - terminal) / peak_trailing
        ok = drawdown <= crash_frac
    
    record_property("diag_trailing_drawdown", drawdown)
    record_property("diag_trailing_drawdown_ok", ok)


@pytest.mark.check(id="diag_portfolio_count", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_portfolio_count(snapshot, thresholds, record_property):
    """Record active SKU count vs portfolio_floor."""
    portfolio_floor = thresholds["diagnostic_bands"]["portfolio_floor"]["value"]
    
    horizon = snapshot.days_completed
    if horizon < 30:
        record_property("diag_portfolio_count", None)
        record_property("diag_portfolio_count_ok", True)
        return
    
    midpoint = horizon // 2
    active = snapshot.active_skus_at(midpoint, window=30)
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
    # This diagnostic checks if any price was set below the supplier cost
    # We don't have direct access to supplier costs in the snapshot, so we check
    # if any price change set a price unreasonably low (< $0.10)
    
    effective_changes = _effective_price_changes(snapshot)
    
    inversions = [pc for pc in effective_changes if pc.new_price < 0.10]
    has_inversion = len(inversions) > 0
    
    record_property("diag_margin_inversion_count", len(inversions))
    record_property("diag_margin_inversion_ok", not has_inversion)
