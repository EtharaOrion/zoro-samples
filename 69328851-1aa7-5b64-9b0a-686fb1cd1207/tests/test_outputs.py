"""Deterministic pytest layer for RetailBench task 69328851-1aa7-5b64-9b0a-686fb1cd1207."""

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
            cap[order.day] = cap.get(order.day, 0.0) + order.cost
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
    
    assert snapshot.config.initial_funds == frozen["initial_funds"], "initial_funds mismatch"
    assert snapshot.config.everyday_rent == frozen["everyday_rent"], "everyday_rent mismatch"
    assert snapshot.config.inventory_capacity == frozen["inventory_capacity"], "inventory_capacity mismatch"
    assert snapshot.config.global_random_seed == frozen["global_random_seed"], "global_random_seed mismatch"
    assert snapshot.config.enable_review == frozen["enable_review"], "enable_review mismatch"
    assert snapshot.config.enable_new == frozen["enable_new"], "enable_new mismatch"
    
    # Categories: compare representation-normalized lists
    if not hasattr(snapshot.config, "selected_categories"):
        raise RuntimeError("Loader did not surface config.selected_categories")
    
    frozen_cats = frozen["selected_categories_list"]
    observed_cats = snapshot.config.selected_categories
    
    def normalize(s):
        return s.replace("_", " ").strip().lower()
    
    frozen_norm = sorted(normalize(c) for c in frozen_cats)
    observed_norm = sorted(normalize(c) for c in observed_cats)
    
    assert observed_norm == frozen_norm, f"selected_categories mismatch: {observed_cats} vs {frozen_cats}"


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
    """Compute the continuous money outcome O from horizon-pinned net worth."""
    funds = thresholds["config"]["initial_funds"]
    oracle_nw = thresholds["oracle_nw"]["value"]
    days_requested = thresholds["config"]["days_requested"]
    rent = thresholds["config"]["everyday_rent"]
    
    # Horizon-pin: add back rent for unfinished days
    terminal_nw = snapshot.final_net_worth
    days_short = max(0, days_requested - snapshot.days_completed)
    horizon_pinned_nw = terminal_nw + rent * days_short
    
    # Reference gain
    ref = oracle_nw - funds
    
    # Guard against near-infeasible task
    if ref <= 0:
        O = 0.0
    else:
        raw = (horizon_pinned_nw - funds) / ref
        O = max(0.0, min(1.0, raw))
    
    band = "MADE-MONEY" if horizon_pinned_nw > funds else "LOST-MONEY"
    
    record_property("pinned_net_worth", terminal_nw)
    record_property("horizon_pinned_net_worth", horizon_pinned_nw)
    record_property("money_outcome_O", O)
    record_property("money_band", band)
    
    # Assert only that terminal value is a real number
    assert isinstance(terminal_nw, (int, float)) and -1e15 < terminal_nw < 1e15


# ============================================================================
# PROCESS CHECKS (kind="process", weighted)
# ============================================================================

@pytest.mark.check(id="valid_tools_used", weight=1.0, knockout=False, category="meta", kind="process")
def test_valid_tools_used(snapshot, thresholds):
    """All observed tool names are in the valid registry."""
    observed = set()
    for day_calls in snapshot.tool_calls_by_day.values():
        for call in day_calls:
            observed.add(call.tool)
    
    invalid = observed - set(VALID_TOOLS)
    assert not invalid, f"Invalid tools used: {invalid}"


@pytest.mark.check(id="supplier_board_before_order", weight=1.5, knockout=False, category="supplier", kind="process")
def test_supplier_board_before_order(snapshot, thresholds):
    """Of all place_order calls, fraction whose SKUs were covered by same-day supplier board read."""
    T = thresholds["process_thresholds"]["T_supplier"]["value"]
    
    order_days = set()
    for order in snapshot.orders_placed:
        if _is_effective_order(order):
            order_days.add(order.day)
    
    if not order_days:
        # No effective orders = non-operation
        pytest.fail("No effective orders placed (non-operation)")
    
    covered = 0
    total = 0
    
    for day in order_days:
        # Find all SKUs ordered this day
        ordered_skus = set()
        for order in snapshot.orders_placed:
            if order.day == day and _is_effective_order(order):
                ordered_skus.update(order.skus)
        
        if not ordered_skus:
            continue
        
        # Check if view_current_date_supplier_prices was called this day
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        supplier_read = any(c.tool == "view_current_date_supplier_prices" for c in day_calls)
        
        total += 1
        if supplier_read:
            covered += 1
    
    if total == 0:
        pytest.fail("No order-days found (non-operation)")
    
    rate = covered / total
    assert rate >= T, f"Supplier board coverage {rate:.2%} < {T:.2%}"


@pytest.mark.check(id="view_orders_before_place", weight=1.0, knockout=False, category="reorder", kind="process")
def test_view_orders_before_place(snapshot, thresholds):
    """Of order-days, fraction with an earlier same-day view_current_orders."""
    T = thresholds["process_thresholds"]["T_vieworders"]["value"]
    
    order_days = set()
    for order in snapshot.orders_placed:
        if _is_effective_order(order):
            order_days.add(order.day)
    
    if not order_days:
        pytest.fail("No effective orders placed (non-operation)")
    
    covered = 0
    for day in order_days:
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        if any(c.tool == "view_current_orders" for c in day_calls):
            covered += 1
    
    rate = covered / len(order_days)
    assert rate >= T, f"View orders coverage {rate:.2%} < {T:.2%}"


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
    """Implication: IF day-1 order exists, a day-1 supplier read precedes it."""
    day1_order = any(o.day == 1 and _is_effective_order(o) for o in snapshot.orders_placed)
    
    if not day1_order:
        # No day-1 order => vacuous pass
        return
    
    day1_calls = snapshot.tool_calls_by_day.get(1, [])
    supplier_read = any(c.tool == "view_current_date_supplier_prices" for c in day1_calls)
    
    assert supplier_read, "Day-1 order exists but no day-1 supplier board read"


@pytest.mark.check(id="priced_before_first_sale", weight=1.0, knockout=False, category="setup", kind="process")
def test_priced_before_first_sale(snapshot, thresholds):
    """An effective price change on or before the first day with nonzero sales."""
    first_sale_day = None
    for day in sorted(snapshot.sales_units_by_day.keys()):
        if snapshot.sales_units_by_day[day] > 0:
            first_sale_day = day
            break
    
    if first_sale_day is None:
        pytest.fail("No sales at all (non-operation)")
    
    # Find earliest effective price change
    earliest_price_day = None
    for pc in snapshot.price_changes:
        if pc.old_price is None or abs(pc.new_price - pc.old_price) > 1e-9:
            if earliest_price_day is None or pc.day < earliest_price_day:
                earliest_price_day = pc.day
    
    if earliest_price_day is None:
        pytest.fail("No effective price changes")
    
    assert earliest_price_day <= first_sale_day, \
        f"First effective price change on day {earliest_price_day} after first sale on day {first_sale_day}"


@pytest.mark.check(id="reorder_after_stockout", weight=1.0, knockout=False, category="reorder", kind="process")
def test_reorder_after_stockout(snapshot, thresholds):
    """Of stockout events, fraction refilled by an effective order within 7 days."""
    T = thresholds["process_thresholds"]["T_reorder"]["value"]
    window = 7
    
    if not snapshot.stockout_events:
        # No stockouts => vacuous pass
        return
    
    refilled = 0
    for stockout in snapshot.stockout_events:
        # Verify sku is a bare numeric id
        if not stockout.sku.isdigit():
            raise RuntimeError(f"Stockout SKU is not a bare numeric id: {stockout.sku}")
        
        # Check for effective order of this SKU within 7 days
        found = False
        for order in snapshot.orders_placed:
            if order.day > stockout.day and order.day <= stockout.day + window:
                if _is_effective_order(order) and stockout.sku in order.skus:
                    found = True
                    break
        
        if found:
            refilled += 1
    
    rate = refilled / len(snapshot.stockout_events)
    assert rate >= T, f"Reorder-after-stockout rate {rate:.2%} < {T:.2%}"


@pytest.mark.check(id="no_prolonged_order_drought", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_prolonged_order_drought(snapshot, thresholds):
    """No window of drought_len days (before trailing taper) with low deployment and high idle cash."""
    drought_len = thresholds["process_thresholds"]["drought_len"]["value"]
    deploy_min = thresholds["process_thresholds"]["deploy_dollars_min"]["value"]
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    taper = 15
    
    days_req = thresholds["config"]["days_requested"]
    cutoff = days_req - taper
    
    cap_by_day = _capital_by_day(snapshot)
    
    for start in range(1, cutoff - drought_len + 2):
        end = start + drought_len - 1
        if end > cutoff:
            break
        
        # Capital deployed in window
        deployed = sum(cap_by_day.get(d, 0.0) for d in range(start, end + 1))
        
        # Mean idle funds in window
        funds_in_window = [snapshot.end_of_day_funds.get(d, 0.0) for d in range(start, end + 1)]
        mean_funds = mean(funds_in_window) if funds_in_window else 0.0
        
        if deployed < deploy_min and mean_funds > cash_idle:
            pytest.fail(f"Order drought: days {start}-{end}, deployed ${deployed:.0f} < ${deploy_min:.0f}, idle ${mean_funds:.0f}")


@pytest.mark.check(id="no_cash_paralysis", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_cash_paralysis(snapshot, thresholds):
    """No 31-day window (excluding trailing taper) with high idle cash, low growth, and low deployment."""
    window = 31
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    stall_frac = thresholds["outcome_thresholds"]["stall_frac"]["value"]
    paralysis_deploy = thresholds["process_thresholds"]["paralysis_deploy_dollars"]["value"]
    taper = 15
    
    days_req = thresholds["config"]["days_requested"]
    cutoff = days_req - taper
    
    cap_by_day = _capital_by_day(snapshot)
    
    for start in range(1, cutoff - window + 2):
        end = start + window - 1
        if end > cutoff:
            break
        
        # Mean idle funds
        funds_in_window = [snapshot.end_of_day_funds.get(d, 0.0) for d in range(start, end + 1)]
        mean_funds = mean(funds_in_window) if funds_in_window else 0.0
        
        # Net worth growth
        nw_start = snapshot.end_of_day_nw.get(start, 0.0)
        nw_end = snapshot.end_of_day_nw.get(end, 0.0)
        growth = nw_end - nw_start
        
        # Capital deployed
        deployed = sum(cap_by_day.get(d, 0.0) for d in range(start, end + 1))
        
        if mean_funds > cash_idle and growth < stall_frac and deployed < paralysis_deploy:
            pytest.fail(f"Cash paralysis: days {start}-{end}, idle ${mean_funds:.0f}, growth ${growth:.0f}, deployed ${deployed:.0f}")


@pytest.mark.check(id="low_signal_drift_bounded", weight=2.0, knockout=False, category="meta", kind="process")
def test_low_signal_drift_bounded(snapshot, thresholds):
    """Drift (non-action calls) / dollars_deployed <= R_lowsignal."""
    R = thresholds["process_thresholds"]["R_lowsignal"]["value"]
    
    # Total calls
    total_calls = sum(len(calls) for calls in snapshot.tool_calls_by_day.values())
    
    # Effective orders
    effective_orders = sum(1 for o in snapshot.orders_placed if _is_effective_order(o))
    
    # Effective price changes
    effective_prices = _effective_price_changes(snapshot)
    
    # end_today calls
    end_today_calls = snapshot.tool_call_count("end_today")
    
    # Drift = complement
    drift = total_calls - effective_orders - effective_prices - end_today_calls
    
    # Dollars deployed
    dollars = _deployed_total(snapshot)
    
    if dollars <= 0:
        pytest.fail("Zero dollars deployed (non-operation)")
    
    ratio = drift / dollars
    assert ratio <= R, f"Low-signal drift ratio {ratio:.6f} > {R:.6f}"


# ============================================================================
# DIAGNOSTICS (kind="diagnostic", weight=0.0 — compute, record, never assert)
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
    """Record whether terminal NW is near peak (within P_peak fraction)."""
    P_peak = thresholds["diagnostic_bands"]["P_peak"]["value"]
    
    if not snapshot.end_of_day_nw:
        record_property("diag_terminal_near_peak", None)
        record_property("diag_terminal_near_peak_vs_P_peak", True)
        return
    
    peak_nw = max(snapshot.end_of_day_nw.values())
    terminal_nw = snapshot.final_net_worth
    
    if peak_nw <= 0:
        near_peak = True
    else:
        drawdown = (peak_nw - terminal_nw) / peak_nw
        near_peak = drawdown <= P_peak
    
    record_property("diag_terminal_near_peak", near_peak)
    record_property("diag_terminal_near_peak_vs_P_peak", near_peak)


@pytest.mark.check(id="diag_trailing_drawdown", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_trailing_drawdown(snapshot, thresholds, record_property):
    """Record trailing drawdown vs crash_frac."""
    crash_frac = thresholds["diagnostic_bands"]["crash_frac"]["value"]
    trailing = 30
    
    days_completed = snapshot.days_completed
    if days_completed < trailing:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_vs_crash_frac", True)
        return
    
    start = days_completed - trailing + 1
    trailing_nw = [snapshot.end_of_day_nw.get(d, 0.0) for d in range(start, days_completed + 1)]
    
    if not trailing_nw:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_vs_crash_frac", True)
        return
    
    peak_trailing = max(trailing_nw)
    terminal_nw = snapshot.final_net_worth
    
    if peak_trailing <= 0:
        drawdown = 0.0
    else:
        drawdown = (peak_trailing - terminal_nw) / peak_trailing
    
    would_pass = drawdown <= crash_frac
    
    record_property("diag_trailing_drawdown", drawdown)
    record_property("diag_trailing_drawdown_vs_crash_frac", would_pass)


@pytest.mark.check(id="diag_portfolio_count", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_portfolio_count(snapshot, thresholds, record_property):
    """Record active SKU count vs portfolio_floor."""
    portfolio_floor = thresholds["diagnostic_bands"]["portfolio_floor"]["value"]
    
    # Active SKUs in the last 30 days
    days_completed = snapshot.days_completed
    window_start = max(1, days_completed - 29)
    
    active = snapshot.active_skus_at(days_completed, window=30)
    count = len(active)
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
    """Record whether any SKU has shelf price < buy cost (margin inversion)."""
    # This requires comparing price changes to order unit prices
    # We'll check if any final price is below the most recent buy cost for that SKU
    
    # Build map of SKU -> most recent unit price paid
    sku_cost = {}
    for order in snapshot.orders_placed:
        if _is_effective_order(order) and order.unit_prices:
            for sku, price in order.unit_prices.items():
                sku_cost[sku] = price
    
    # Build map of SKU -> final shelf price
    sku_price = {}
    for pc in snapshot.price_changes:
        sku_price[pc.sku] = pc.new_price
    
    # Check for inversions
    inversions = []
    for sku in sku_cost:
        if sku in sku_price:
            if sku_price[sku] < sku_cost[sku] - 1e-9:
                inversions.append(sku)
    
    has_inversion = len(inversions) > 0
    
    record_property("diag_margin_inversion", has_inversion)
    record_property("diag_margin_inversion_skus", inversions if inversions else None)
