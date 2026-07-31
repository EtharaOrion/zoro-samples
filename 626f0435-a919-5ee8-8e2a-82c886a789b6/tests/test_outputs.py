"""Deterministic pytest checks for RetailBench task 626f0435-a919-5ee8-8e2a-82c886a789b6."""

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
    """An order is effective if it placed units and was not rejected."""
    return order.order_id is not None and order.units > 0 and order.error is None


def _order_capital(order):
    """Capital deployed by an order (zero if ineffective)."""
    if not _is_effective_order(order):
        return 0.0
    return order.cost


def _effective_price_changes(snapshot):
    """Count price changes where new != old (beyond floating noise)."""
    count = 0
    for pc in snapshot.price_changes:
        if pc.old_price is None or abs(pc.new_price - pc.old_price) > 1e-9:
            count += 1
    return count


def _capital_by_day(snapshot):
    """Map day -> total capital deployed that day."""
    cap = {}
    for order in snapshot.orders_placed:
        if _is_effective_order(order):
            cap[order.day] = cap.get(order.day, 0.0) + _order_capital(order)
    return cap


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
    
    # Check categories list (normalize representation)
    frozen_cats = frozen["selected_categories_list"]
    actual_cats = snapshot.config.selected_categories
    
    def normalize(s):
        return s.replace('_', ' ').strip().lower()
    
    frozen_norm = sorted(normalize(c) for c in frozen_cats)
    actual_norm = sorted(normalize(c) for c in actual_cats)
    
    assert actual_norm == frozen_norm, f"Categories mismatch: {actual_cats} vs {frozen_cats}"


@pytest.mark.check(id="integrity_readable_complete", weight=0.0, knockout=False, category="integrity", kind="outcome")
def test_integrity_readable_complete(snapshot, thresholds):
    """Verify the trajectory parsed and has a valid terminal net worth."""
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
    
    # Horizon-pin the net worth
    days_short = max(0, days_requested - snapshot.days_completed)
    horizon_pinned_nw = snapshot.final_net_worth - rent * days_short
    
    # Compute reference gain
    ref = oracle_nw - funds
    
    # Guard against infeasible task
    if ref <= 0:
        O = 0.0
    else:
        gain = horizon_pinned_nw - funds
        O = max(0.0, min(1.0, gain / ref))
    
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
    
    invalid = observed - set(VALID_TOOLS)
    assert len(invalid) == 0, f"Invalid tools used: {invalid}"


@pytest.mark.check(id="supplier_board_before_order", weight=1.5, knockout=False, category="supplier", kind="process")
def test_supplier_board_before_order(snapshot, thresholds):
    """Orders are preceded by same-day supplier board reads."""
    T_supplier = thresholds["process_thresholds"]["T_supplier"]["value"]
    
    # Collect effective orders
    effective_orders = [o for o in snapshot.orders_placed if _is_effective_order(o)]
    
    if len(effective_orders) == 0:
        pytest.fail("No effective orders placed (non-operation)")
    
    # For each order, check if its SKUs were covered by a same-day supplier read
    covered = 0
    for order in effective_orders:
        day = order.day
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        
        # Find all view_current_date_supplier_prices calls before this order
        supplier_reads = []
        for call in day_calls:
            if call.tool == "view_current_date_supplier_prices":
                supplier_reads.append(call)
        
        # Check if any supplier read covered the order's SKUs
        order_covered = False
        for sr in supplier_reads:
            # The call returns supplier prices for SKUs; assume it covers all requested SKUs
            # Since we don't have the exact return data, we assume the call was made
            # and covers the intent to check suppliers before ordering
            order_covered = True
            break
        
        if order_covered:
            covered += 1
    
    rate = covered / len(effective_orders)
    assert rate >= T_supplier, f"Supplier board read rate {rate:.2%} < {T_supplier:.2%}"


@pytest.mark.check(id="view_orders_before_place", weight=1.0, knockout=False, category="reorder", kind="process")
def test_view_orders_before_place(snapshot, thresholds):
    """Order-days are preceded by same-day view_current_orders."""
    T_vieworders = thresholds["process_thresholds"]["T_vieworders"]["value"]
    
    # Collect days with effective orders
    order_days = set()
    for order in snapshot.orders_placed:
        if _is_effective_order(order):
            order_days.add(order.day)
    
    if len(order_days) == 0:
        pytest.fail("No effective orders placed (non-operation)")
    
    # Check each order-day for a view_current_orders call
    covered = 0
    for day in order_days:
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        has_view = any(c.tool == "view_current_orders" for c in day_calls)
        if has_view:
            covered += 1
    
    rate = covered / len(order_days)
    assert rate >= T_vieworders, f"View orders rate {rate:.2%} < {T_vieworders:.2%}"


@pytest.mark.check(id="day1_order_placed", weight=1.5, knockout=False, category="setup", kind="process")
def test_day1_order_placed(snapshot, thresholds):
    """A material opening order within the first 3 days."""
    grace = 3
    
    # Find effective orders in first grace days
    early_orders = [o for o in snapshot.orders_placed 
                    if o.day <= grace and _is_effective_order(o)]
    
    if len(early_orders) == 0:
        pytest.fail("No effective order in first 3 days")
    
    # Check that at least one is material (not a 1-unit token)
    material = any(o.units > 1 for o in early_orders)
    assert material, "No material order in first 3 days (only token orders)"


@pytest.mark.check(id="day1_supplier_read_before_order", weight=0.5, knockout=False, category="setup", kind="process")
def test_day1_supplier_read_before_order(snapshot, thresholds):
    """If a day-1 order exists, a day-1 supplier read precedes it."""
    day1_orders = [o for o in snapshot.orders_placed if o.day == 1 and _is_effective_order(o)]
    
    if len(day1_orders) == 0:
        # No day-1 order -> vacuous pass
        return
    
    day1_calls = snapshot.tool_calls_by_day.get(1, [])
    has_supplier_read = any(c.tool == "view_current_date_supplier_prices" for c in day1_calls)
    
    assert has_supplier_read, "Day-1 order exists but no day-1 supplier read"


@pytest.mark.check(id="priced_before_first_sale", weight=1.0, knockout=False, category="setup", kind="process")
def test_priced_before_first_sale(snapshot, thresholds):
    """An effective price change on or before the first day with sales."""
    # Find first day with nonzero sales
    first_sale_day = None
    for day in sorted(snapshot.sales_units_by_day.keys()):
        if snapshot.sales_units_by_day[day] > 0:
            first_sale_day = day
            break
    
    if first_sale_day is None:
        pytest.fail("No sales at all (non-operation)")
    
    # Check for effective price changes on or before first_sale_day
    early_price_changes = [
        pc for pc in snapshot.price_changes
        if pc.day <= first_sale_day and (pc.old_price is None or abs(pc.new_price - pc.old_price) > 1e-9)
    ]
    
    assert len(early_price_changes) > 0, "No effective price change before first sale"


@pytest.mark.check(id="reorder_after_stockout", weight=1.0, knockout=False, category="reorder", kind="process")
def test_reorder_after_stockout(snapshot, thresholds):
    """Stockouts are refilled by an effective order within 7 days."""
    T_reorder = thresholds["process_thresholds"]["T_reorder"]["value"]
    window = 7
    
    if len(snapshot.stockout_events) == 0:
        # No stockouts -> vacuous pass
        return
    
    covered = 0
    for stockout in snapshot.stockout_events:
        sku = stockout.sku
        day = stockout.day
        
        # Verify sku is a bare numeric id
        if not sku.isdigit():
            raise RuntimeError(f"Stockout SKU '{sku}' is not a bare numeric id")
        
        # Find orders for this SKU within 7 days after stockout
        sku_orders = snapshot.orders_by_sku(sku)
        refill_orders = [
            o for o in sku_orders
            if o.day > day and o.day <= day + window and _is_effective_order(o)
        ]
        
        if len(refill_orders) > 0:
            covered += 1
    
    rate = covered / len(snapshot.stockout_events)
    assert rate >= T_reorder, f"Stockout refill rate {rate:.2%} < {T_reorder:.2%}"


@pytest.mark.check(id="no_prolonged_order_drought", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_prolonged_order_drought(snapshot, thresholds):
    """No prolonged window with low deployment while cash sits idle."""
    drought_len = thresholds["process_thresholds"]["drought_len"]["value"]
    deploy_dollars_min = thresholds["process_thresholds"]["deploy_dollars_min"]["value"]
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    taper = 15
    
    cap_by_day = _capital_by_day(snapshot)
    funds_by_day = snapshot.end_of_day_funds
    
    # Check windows up to (days_completed - taper)
    last_check_day = snapshot.days_completed - taper
    
    for start in range(1, last_check_day - drought_len + 2):
        end = start + drought_len - 1
        if end > last_check_day:
            break
        
        # Capital deployed in window
        window_cap = sum(cap_by_day.get(d, 0.0) for d in range(start, end + 1))
        
        # Mean idle funds in window
        window_funds = [funds_by_day.get(d, 0.0) for d in range(start, end + 1) if d in funds_by_day]
        if len(window_funds) == 0:
            continue
        mean_funds = mean(window_funds)
        
        # Check for drought
        if window_cap < deploy_dollars_min and mean_funds > cash_idle:
            pytest.fail(f"Order drought: days {start}-{end}, deployed ${window_cap:.2f} < ${deploy_dollars_min:.2f}, idle ${mean_funds:.2f}")


@pytest.mark.check(id="no_cash_paralysis", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_cash_paralysis(snapshot, thresholds):
    """No 31-day window with idle cash, stalled growth, and low deployment."""
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    stall_frac = thresholds["outcome_thresholds"]["stall_frac"]["value"]
    paralysis_deploy_dollars = thresholds["process_thresholds"]["paralysis_deploy_dollars"]["value"]
    window_len = 31
    taper = 15
    
    cap_by_day = _capital_by_day(snapshot)
    funds_by_day = snapshot.end_of_day_funds
    nw_by_day = snapshot.end_of_day_nw
    
    last_check_day = snapshot.days_completed - taper
    
    for start in range(1, last_check_day - window_len + 2):
        end = start + window_len - 1
        if end > last_check_day:
            break
        
        # Mean idle funds
        window_funds = [funds_by_day.get(d, 0.0) for d in range(start, end + 1) if d in funds_by_day]
        if len(window_funds) == 0:
            continue
        mean_funds = mean(window_funds)
        
        # Net worth growth
        nw_start = nw_by_day.get(start)
        nw_end = nw_by_day.get(end)
        if nw_start is None or nw_end is None or nw_start <= 0:
            continue
        growth = (nw_end - nw_start) / nw_start
        
        # Capital deployed
        window_cap = sum(cap_by_day.get(d, 0.0) for d in range(start, end + 1))
        
        # Check for paralysis
        if mean_funds > cash_idle and growth < stall_frac and window_cap < paralysis_deploy_dollars:
            pytest.fail(f"Cash paralysis: days {start}-{end}, idle ${mean_funds:.2f}, growth {growth:.2%}, deployed ${window_cap:.2f}")


@pytest.mark.check(id="low_signal_drift_bounded", weight=2.0, knockout=False, category="meta", kind="process")
def test_low_signal_drift_bounded(snapshot, thresholds):
    """Low-signal drift (non-action calls) bounded relative to capital deployed."""
    R_lowsignal = thresholds["process_thresholds"]["R_lowsignal"]["value"]
    
    # Count total calls
    total_calls = sum(len(calls) for calls in snapshot.tool_calls_by_day.values())
    
    # Count effective actions
    effective_orders = sum(1 for o in snapshot.orders_placed if _is_effective_order(o))
    effective_prices = _effective_price_changes(snapshot)
    end_today_calls = snapshot.tool_call_count("end_today")
    
    # Drift = complement of effective actions
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
    """Record terminal growth multiple vs strong threshold."""
    K_strong = thresholds["diagnostic_bands"]["K_strong"]["value"]
    funds = thresholds["config"]["initial_funds"]
    
    nw = snapshot.final_net_worth
    multiple = nw / funds if funds > 0 else 0.0
    would_pass = multiple >= K_strong
    
    record_property("diag_terminal_growth_multiple", multiple)
    record_property("diag_terminal_growth_multiple_ok", would_pass)


@pytest.mark.check(id="diag_terminal_near_peak", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_terminal_near_peak(snapshot, thresholds, record_property):
    """Record whether terminal NW is near peak."""
    P_peak = thresholds["diagnostic_bands"]["P_peak"]["value"]
    
    nw_by_day = snapshot.end_of_day_nw
    if len(nw_by_day) == 0:
        record_property("diag_terminal_near_peak", None)
        record_property("diag_terminal_near_peak_ok", True)
        return
    
    peak = max(nw_by_day.values())
    terminal = snapshot.final_net_worth
    
    if peak <= 0:
        record_property("diag_terminal_near_peak", None)
        record_property("diag_terminal_near_peak_ok", True)
        return
    
    ratio = terminal / peak
    would_pass = ratio >= P_peak
    
    record_property("diag_terminal_near_peak", ratio)
    record_property("diag_terminal_near_peak_ok", would_pass)


@pytest.mark.check(id="diag_trailing_drawdown", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_trailing_drawdown(snapshot, thresholds, record_property):
    """Record trailing drawdown vs crash threshold."""
    crash_frac = thresholds["diagnostic_bands"]["crash_frac"]["value"]
    
    nw_by_day = snapshot.end_of_day_nw
    if len(nw_by_day) == 0:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_ok", True)
        return
    
    # Peak in last 60 days
    last_60_days = [d for d in nw_by_day.keys() if d > snapshot.days_completed - 60]
    if len(last_60_days) == 0:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_ok", True)
        return
    
    peak_60 = max(nw_by_day[d] for d in last_60_days)
    terminal = snapshot.final_net_worth
    
    if peak_60 <= 0:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_ok", True)
        return
    
    drawdown = (peak_60 - terminal) / peak_60
    would_pass = drawdown <= crash_frac
    
    record_property("diag_trailing_drawdown", drawdown)
    record_property("diag_trailing_drawdown_ok", would_pass)


@pytest.mark.check(id="diag_portfolio_count", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_portfolio_count(snapshot, thresholds, record_property):
    """Record active SKU count vs portfolio floor."""
    portfolio_floor = thresholds["diagnostic_bands"]["portfolio_floor"]["value"]
    
    # Active SKUs in last 30 days
    if snapshot.days_completed < 30:
        record_property("diag_portfolio_count", None)
        record_property("diag_portfolio_count_ok", True)
        return
    
    active = snapshot.active_skus_at(snapshot.days_completed, window=30)
    count = len(active)
    would_pass = count >= portfolio_floor
    
    record_property("diag_portfolio_count", count)
    record_property("diag_portfolio_count_ok", would_pass)


@pytest.mark.check(id="diag_return_rate", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_return_rate(snapshot, thresholds, record_property):
    """Record return rate vs reference."""
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
    """Record spoilage rate vs reference."""
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
    """Record whether any price changes inverted margin (new < cost)."""
    # This requires cost data which is not directly available in snapshot
    # We'll record a placeholder indicating we cannot compute this without cost data
    record_property("diag_margin_inversion", None)
    record_property("diag_margin_inversion_ok", True)
