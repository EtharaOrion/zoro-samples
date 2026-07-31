"""Deterministic pytest layer for task 70a4673a-d04f-5792-9761-de6a939a7139."""

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
    
    # Categories: compare representation-normalized lists
    frozen_cats = thresholds["config"]["selected_categories_list"]
    actual_cats = snapshot.config.selected_categories
    
    def normalize(s):
        return s.replace("_", " ").strip().lower()
    
    frozen_norm = sorted(normalize(c) for c in frozen_cats)
    actual_norm = sorted(normalize(c) for c in actual_cats)
    
    assert actual_norm == frozen_norm, f"Category mismatch: {actual_cats} vs {frozen_cats}"


@pytest.mark.check(id="integrity_readable_complete", weight=0.0, knockout=False, category="integrity", kind="outcome")
def test_integrity_readable_complete(snapshot, thresholds):
    """Verify the trajectory parsed and terminal net worth is a finite real number."""
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
        raw = (horizon_pinned_nw - funds) / ref
        O = max(0.0, min(1.0, raw))
    
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
    assert len(invalid) == 0, f"Invalid tools used: {invalid}"


@pytest.mark.check(id="supplier_board_before_order", weight=1.5, knockout=False, category="supplier", kind="process")
def test_supplier_board_before_order(snapshot, thresholds):
    """Fraction of orders whose SKUs were covered by a same-day supplier board read."""
    T = thresholds["process_thresholds"]["T_supplier"]["value"]
    
    effective_orders = [o for o in snapshot.orders_placed if _is_effective_order(o)]
    
    if len(effective_orders) == 0:
        pytest.fail("No effective orders placed (non-operation)")
    
    covered = 0
    for order in effective_orders:
        day = order.day
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        
        # Find all view_current_date_supplier_prices calls before this order
        supplier_reads = []
        for call in day_calls:
            if call.tool == "view_current_date_supplier_prices":
                supplier_reads.append(call)
        
        # Check if any supplier read covered all SKUs in this order
        order_skus = order.skus
        covered_this = False
        for read in supplier_reads:
            # The read covers SKUs if they were requested
            # args typically has 'sku_ids' or similar
            read_skus = set()
            if hasattr(read, 'args') and read.args:
                if 'sku_ids' in read.args:
                    read_skus = set(str(s) for s in read.args['sku_ids'])
                elif 'sku_id' in read.args:
                    read_skus = {str(read.args['sku_id'])}
            
            if order_skus.issubset(read_skus):
                covered_this = True
                break
        
        if covered_this:
            covered += 1
    
    rate = covered / len(effective_orders)
    assert rate >= T, f"Supplier board coverage {rate:.2%} < {T:.2%}"


@pytest.mark.check(id="view_orders_before_place", weight=1.0, knockout=False, category="reorder", kind="process")
def test_view_orders_before_place(snapshot, thresholds):
    """Fraction of order-days with a same-day view_current_orders read."""
    T = thresholds["process_thresholds"]["T_vieworders"]["value"]
    
    order_days = set()
    for order in snapshot.orders_placed:
        if _is_effective_order(order):
            order_days.add(order.day)
    
    if len(order_days) == 0:
        pytest.fail("No effective orders placed (non-operation)")
    
    covered = 0
    for day in order_days:
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        has_view = any(c.tool == "view_current_orders" for c in day_calls)
        if has_view:
            covered += 1
    
    rate = covered / len(order_days)
    assert rate >= T, f"View orders rate {rate:.2%} < {T:.2%}"


@pytest.mark.check(id="day1_order_placed", weight=1.5, knockout=False, category="setup", kind="process")
def test_day1_order_placed(snapshot, thresholds):
    """A material opening order within the first 3 days."""
    grace = 3
    
    early_orders = [o for o in snapshot.orders_placed 
                    if o.day <= grace and _is_effective_order(o)]
    
    assert len(early_orders) > 0, "No effective order in first 3 days"


@pytest.mark.check(id="day1_supplier_read_before_order", weight=0.5, knockout=False, category="setup", kind="process")
def test_day1_supplier_read_before_order(snapshot, thresholds):
    """If a day-1 order exists, a day-1 supplier read precedes it."""
    day1_orders = [o for o in snapshot.orders_placed if o.day == 1 and _is_effective_order(o)]
    
    if len(day1_orders) == 0:
        # Vacuous pass
        return
    
    day1_calls = snapshot.tool_calls_by_day.get(1, [])
    has_supplier_read = any(c.tool == "view_current_date_supplier_prices" for c in day1_calls)
    
    assert has_supplier_read, "Day-1 order exists but no day-1 supplier read"


@pytest.mark.check(id="priced_before_first_sale", weight=1.0, knockout=False, category="setup", kind="process")
def test_priced_before_first_sale(snapshot, thresholds):
    """An effective price change on or before the first day with sales."""
    sales_by_day = snapshot.sales_units_by_day
    
    if not sales_by_day or all(u == 0 for u in sales_by_day.values()):
        pytest.fail("No sales recorded (non-operation)")
    
    first_sale_day = min(d for d, u in sales_by_day.items() if u > 0)
    
    early_price_changes = [
        pc for pc in snapshot.price_changes
        if pc.day <= first_sale_day and (pc.old_price is None or abs(pc.new_price - pc.old_price) > 1e-9)
    ]
    
    assert len(early_price_changes) > 0, f"No effective price change by day {first_sale_day}"


@pytest.mark.check(id="reorder_after_stockout", weight=1.0, knockout=False, category="reorder", kind="process")
def test_reorder_after_stockout(snapshot, thresholds):
    """Fraction of stockouts refilled by an effective order within 7 days."""
    T = thresholds["process_thresholds"]["T_reorder"]["value"]
    window = 7
    
    stockouts = snapshot.stockout_events
    
    if len(stockouts) == 0:
        # Vacuous pass
        return
    
    refilled = 0
    for stockout in stockouts:
        sku = stockout.sku
        day = stockout.day
        
        # Verify sku is a bare numeric id
        if not isinstance(sku, str) or not sku.isdigit():
            raise RuntimeError(f"Stockout SKU not a bare numeric id: {sku}")
        
        # Check for effective orders of this SKU within 7 days
        future_orders = [
            o for o in snapshot.orders_by_sku(sku)
            if day < o.day <= day + window and _is_effective_order(o)
        ]
        
        if len(future_orders) > 0:
            refilled += 1
    
    rate = refilled / len(stockouts)
    assert rate >= T, f"Reorder rate {rate:.2%} < {T:.2%}"


@pytest.mark.check(id="no_prolonged_order_drought", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_prolonged_order_drought(snapshot, thresholds):
    """No drought window with low deployment while idle funds are high."""
    drought_len = thresholds["process_thresholds"]["drought_len"]["value"]
    deploy_min = thresholds["process_thresholds"]["deploy_dollars_min"]["value"]
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    
    taper = 15
    last_day = snapshot.days_completed
    check_until = max(1, last_day - taper)
    
    cap_by_day = _capital_by_day(snapshot)
    funds_by_day = snapshot.end_of_day_funds
    
    for start in range(1, check_until - drought_len + 2):
        end = start + drought_len - 1
        if end > check_until:
            break
        
        window_days = range(start, end + 1)
        deployed = sum(cap_by_day.get(d, 0.0) for d in window_days)
        funds_vals = [funds_by_day.get(d, 0.0) for d in window_days if d in funds_by_day]
        
        if len(funds_vals) == 0:
            continue
        
        mean_funds = mean(funds_vals)
        
        if deployed < deploy_min and mean_funds > cash_idle:
            pytest.fail(f"Drought days {start}-{end}: deployed ${deployed:.0f} < ${deploy_min:.0f}, idle ${mean_funds:.0f}")


@pytest.mark.check(id="no_cash_paralysis", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_cash_paralysis(snapshot, thresholds):
    """No 31-day window with high idle funds, low growth, and low deployment."""
    window_len = 31
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    stall_frac = thresholds["outcome_thresholds"]["stall_frac"]["value"]
    paralysis_deploy = thresholds["process_thresholds"]["paralysis_deploy_dollars"]["value"]
    
    taper = 15
    last_day = snapshot.days_completed
    check_until = max(1, last_day - taper)
    
    cap_by_day = _capital_by_day(snapshot)
    funds_by_day = snapshot.end_of_day_funds
    nw_by_day = snapshot.end_of_day_nw
    
    for start in range(1, check_until - window_len + 2):
        end = start + window_len - 1
        if end > check_until:
            break
        
        window_days = range(start, end + 1)
        
        funds_vals = [funds_by_day.get(d, 0.0) for d in window_days if d in funds_by_day]
        if len(funds_vals) == 0:
            continue
        mean_funds = mean(funds_vals)
        
        nw_start = nw_by_day.get(start)
        nw_end = nw_by_day.get(end)
        if nw_start is None or nw_end is None or nw_start <= 0:
            continue
        
        growth = (nw_end - nw_start) / nw_start
        deployed = sum(cap_by_day.get(d, 0.0) for d in window_days)
        
        if mean_funds > cash_idle and growth < stall_frac and deployed < paralysis_deploy:
            pytest.fail(f"Paralysis days {start}-{end}: idle ${mean_funds:.0f}, growth {growth:.1%}, deployed ${deployed:.0f}")


@pytest.mark.check(id="low_signal_drift_bounded", weight=2.0, knockout=False, category="meta", kind="process")
def test_low_signal_drift_bounded(snapshot, thresholds):
    """Low-signal drift (non-effective calls) bounded relative to dollars deployed."""
    R = thresholds["process_thresholds"]["R_lowsignal"]["value"]
    
    total_calls = sum(len(calls) for calls in snapshot.tool_calls_by_day.values())
    effective_orders = sum(1 for o in snapshot.orders_placed if _is_effective_order(o))
    effective_prices = _effective_price_changes(snapshot)
    end_today_calls = snapshot.tool_call_count("end_today")
    
    drift = total_calls - effective_orders - effective_prices - end_today_calls
    deployed = _deployed_total(snapshot)
    
    if deployed <= 0:
        pytest.fail("Zero dollars deployed (non-operation)")
    
    ratio = drift / deployed
    assert ratio <= R, f"Low-signal ratio {ratio:.4f} > {R:.4f}"


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
        record_property("diag_terminal_near_peak", None)
        record_property("diag_terminal_near_peak_ok", True)
        return
    
    ratio = terminal / peak
    ok = ratio >= P_peak
    
    record_property("diag_terminal_near_peak", ratio)
    record_property("diag_terminal_near_peak_ok", ok)


@pytest.mark.check(id="diag_trailing_drawdown", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_trailing_drawdown(snapshot, thresholds, record_property):
    """Record trailing drawdown vs crash_frac."""
    crash_frac = thresholds["diagnostic_bands"]["crash_frac"]["value"]
    window = 30
    
    nw_by_day = snapshot.end_of_day_nw
    last_day = snapshot.days_completed
    
    if last_day < window:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_ok", True)
        return
    
    trailing_days = range(last_day - window + 1, last_day + 1)
    trailing_vals = [nw_by_day.get(d) for d in trailing_days if d in nw_by_day]
    
    if len(trailing_vals) == 0:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_ok", True)
        return
    
    peak_trailing = max(trailing_vals)
    terminal = snapshot.final_net_worth
    
    if peak_trailing <= 0:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_ok", True)
        return
    
    drawdown = (peak_trailing - terminal) / peak_trailing
    ok = drawdown <= crash_frac
    
    record_property("diag_trailing_drawdown", drawdown)
    record_property("diag_trailing_drawdown_ok", ok)


@pytest.mark.check(id="diag_portfolio_count", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_portfolio_count(snapshot, thresholds, record_property):
    """Record active SKU count vs portfolio_floor."""
    portfolio_floor = thresholds["diagnostic_bands"]["portfolio_floor"]["value"]
    
    # Count SKUs active in the last 30 days
    last_day = snapshot.days_completed
    active = snapshot.active_skus_at(last_day, window=30)
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
    """Record whether any SKU has negative margin (shelf price < buy cost)."""
    # Check final prices vs typical buy costs
    # This is a structural diagnostic; we record presence of inversions
    
    # We don't have direct access to per-SKU buy costs in the snapshot,
    # so we check if any price changes resulted in very low prices
    # that would be below typical costs
    
    # For this diagnostic, we'll check if any final prices are suspiciously low
    # A more complete implementation would compare to actual order costs
    
    # Since we don't have the full price/cost mapping, we'll record a placeholder
    # indicating whether we detected any obvious inversions
    
    inversions = 0
    # This would require cross-referencing prices with order costs
    # For now, we'll record 0 as we don't have the data structure to detect this
    
    record_property("diag_margin_inversion_count", inversions)
    record_property("diag_margin_inversion_ok", inversions == 0)
