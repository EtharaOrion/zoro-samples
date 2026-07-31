"""Deterministic pytest layer for RetailBench task 614fe8a9-05ec-5fe4-9e42-e58032b9e045."""

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
    """Capital deployed by an order (0 if ineffective)."""
    return order.cost if _is_effective_order(order) else 0.0


def _effective_price_changes(snapshot):
    """Count price changes where |new - old| > 1e-9 or old_price is None."""
    count = 0
    for pc in snapshot.price_changes:
        if pc.old_price is None or abs(pc.new_price - pc.old_price) > 1e-9:
            count += 1
    return count


def _capital_by_day(snapshot):
    """Map day -> total capital deployed that day."""
    by_day = {}
    for order in snapshot.orders_placed:
        if _is_effective_order(order):
            by_day[order.day] = by_day.get(order.day, 0.0) + order.cost
    return by_day


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
    
    assert snapshot.config.initial_funds == frozen["initial_funds"], \
        f"initial_funds mismatch: {snapshot.config.initial_funds} != {frozen['initial_funds']}"
    assert snapshot.config.everyday_rent == frozen["everyday_rent"], \
        f"everyday_rent mismatch: {snapshot.config.everyday_rent} != {frozen['everyday_rent']}"
    assert snapshot.config.inventory_capacity == frozen["inventory_capacity"], \
        f"inventory_capacity mismatch: {snapshot.config.inventory_capacity} != {frozen['inventory_capacity']}"
    assert snapshot.config.global_random_seed == frozen["global_random_seed"], \
        f"global_random_seed mismatch: {snapshot.config.global_random_seed} != {frozen['global_random_seed']}"
    assert snapshot.config.enable_review == frozen["enable_review"], \
        f"enable_review mismatch: {snapshot.config.enable_review} != {frozen['enable_review']}"
    assert snapshot.config.enable_new == frozen["enable_new"], \
        f"enable_new mismatch: {snapshot.config.enable_new} != {frozen['enable_new']}"
    
    # Categories (list comparison, representation-normalized)
    if not hasattr(snapshot.config, "selected_categories"):
        raise RuntimeError("Loader did not surface config.selected_categories")
    
    frozen_cats = frozen["selected_categories_list"]
    observed_cats = snapshot.config.selected_categories
    
    def normalize_cat(c):
        return c.replace("_", " ").strip().lower()
    
    frozen_norm = sorted(normalize_cat(c) for c in frozen_cats)
    observed_norm = sorted(normalize_cat(c) for c in observed_cats)
    
    assert observed_norm == frozen_norm, \
        f"selected_categories mismatch: {observed_cats} != {frozen_cats}"


@pytest.mark.check(id="integrity_readable_complete", weight=0.0, knockout=False, category="integrity", kind="outcome")
def test_integrity_readable_complete(snapshot, thresholds):
    """Verify the trajectory parsed and the terminal net worth is a finite real number."""
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
    """Compute the continuous money outcome O and record the band."""
    funds = thresholds["config"]["initial_funds"]
    oracle_nw = thresholds["oracle_nw"]["value"]
    days_requested = thresholds["config"]["days_requested"]
    rent = thresholds["config"]["everyday_rent"]
    
    # Horizon-pinned net worth (project rent for unfinished days)
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
    """All observed tool names are in the valid tool registry."""
    observed = set()
    for day_calls in snapshot.tool_calls_by_day.values():
        for call in day_calls:
            observed.add(call.tool)
    
    invalid = observed - set(VALID_TOOLS)
    assert not invalid, f"Invalid tools used: {invalid}"


@pytest.mark.check(id="supplier_board_before_order", weight=1.5, knockout=False, category="supplier", kind="process")
def test_supplier_board_before_order(snapshot, thresholds):
    """Of all place_order calls, the fraction whose ordered SKUs were covered by an earlier same-day view_current_date_supplier_prices read."""
    T_supplier = thresholds["process_thresholds"]["T_supplier"]["value"]
    
    order_calls = []
    for day, calls in snapshot.tool_calls_by_day.items():
        for call in calls:
            if call.tool == "place_order":
                order_calls.append((day, call))
    
    if not order_calls:
        # Zero orders -> definite FAIL (non-operation)
        assert False, "No orders placed (non-operation)"
    
    covered = 0
    for day, order_call in order_calls:
        # Extract SKUs from the order
        items = order_call.args.get("items", [])
        order_skus = set()
        for item in items:
            if isinstance(item, dict) and "sku_id" in item:
                order_skus.add(str(item["sku_id"]))
        
        if not order_skus:
            continue
        
        # Check if a same-day view_current_date_supplier_prices covered these SKUs
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        read_skus = set()
        for call in day_calls:
            if call.tool == "view_current_date_supplier_prices":
                sku_ids = call.args.get("sku_ids", [])
                for sid in sku_ids:
                    read_skus.add(str(sid))
            if call == order_call:
                # Stop at the order call itself
                break
        
        if order_skus.issubset(read_skus):
            covered += 1
    
    coverage = covered / len(order_calls)
    assert coverage >= T_supplier, \
        f"Supplier board coverage {coverage:.2%} < {T_supplier:.2%}"


@pytest.mark.check(id="view_orders_before_place", weight=1.0, knockout=False, category="reorder", kind="process")
def test_view_orders_before_place(snapshot, thresholds):
    """Of order-days, the fraction with an earlier same-day view_current_orders."""
    T_vieworders = thresholds["process_thresholds"]["T_vieworders"]["value"]
    
    order_days = set()
    for order in snapshot.orders_placed:
        if _is_effective_order(order):
            order_days.add(order.day)
    
    if not order_days:
        # Non-operation -> FAIL
        assert False, "No effective orders placed (non-operation)"
    
    covered = 0
    for day in order_days:
        day_calls = snapshot.tool_calls_by_day.get(day, [])
        # Find first effective order on this day
        first_order_idx = None
        for i, call in enumerate(day_calls):
            if call.tool == "place_order":
                # Check if this order was effective
                items = call.args.get("items", [])
                if items:
                    first_order_idx = i
                    break
        
        if first_order_idx is None:
            continue
        
        # Check if view_current_orders appears before it
        for i in range(first_order_idx):
            if day_calls[i].tool == "view_current_orders":
                covered += 1
                break
    
    coverage = covered / len(order_days)
    assert coverage >= T_vieworders, \
        f"view_current_orders coverage {coverage:.2%} < {T_vieworders:.2%}"


@pytest.mark.check(id="day1_order_placed", weight=1.5, knockout=False, category="setup", kind="process")
def test_day1_order_placed(snapshot, thresholds):
    """A material (effective) opening order within the first 3 days."""
    grace = 3
    
    for order in snapshot.orders_placed:
        if order.day <= grace and _is_effective_order(order):
            return  # PASS
    
    assert False, f"No effective order placed within first {grace} days"


@pytest.mark.check(id="day1_supplier_read_before_order", weight=0.5, knockout=False, category="setup", kind="process")
def test_day1_supplier_read_before_order(snapshot, thresholds):
    """Implication: IF a day-1 order exists, a day-1 supplier-board read precedes it."""
    day1_calls = snapshot.tool_calls_by_day.get(1, [])
    
    # Find first day-1 order
    first_order_idx = None
    for i, call in enumerate(day1_calls):
        if call.tool == "place_order":
            items = call.args.get("items", [])
            if items:
                first_order_idx = i
                break
    
    if first_order_idx is None:
        # No day-1 order -> vacuous PASS
        return
    
    # Check if view_current_date_supplier_prices appears before it
    for i in range(first_order_idx):
        if day1_calls[i].tool == "view_current_date_supplier_prices":
            return  # PASS
    
    assert False, "Day-1 order placed without prior day-1 supplier board read"


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
        # No sales at all -> definite FAIL (non-operation)
        assert False, "No sales recorded (non-operation)"
    
    # Check for effective price change on or before first_sale_day
    for pc in snapshot.price_changes:
        if pc.day <= first_sale_day:
            if pc.old_price is None or abs(pc.new_price - pc.old_price) > 1e-9:
                return  # PASS
    
    assert False, f"No effective price change on or before first sale day {first_sale_day}"


@pytest.mark.check(id="reorder_after_stockout", weight=1.0, knockout=False, category="reorder", kind="process")
def test_reorder_after_stockout(snapshot, thresholds):
    """Of stockout events, the fraction refilled by an effective order within 7 days."""
    T_reorder = thresholds["process_thresholds"]["T_reorder"]["value"]
    
    if not snapshot.stockout_events:
        # No stockouts -> vacuous PASS
        return
    
    refilled = 0
    for stockout in snapshot.stockout_events:
        sku = stockout.sku
        day = stockout.day
        
        # Verify sku is a bare numeric id
        if not isinstance(sku, str) or not sku.isdigit():
            raise RuntimeError(f"Stockout sku is not a bare numeric id: {sku}")
        
        # Check for effective order of this SKU within 7 days
        for order in snapshot.orders_by_sku(sku):
            if day < order.day <= day + 7 and _is_effective_order(order):
                refilled += 1
                break
    
    coverage = refilled / len(snapshot.stockout_events)
    assert coverage >= T_reorder, \
        f"Stockout refill rate {coverage:.2%} < {T_reorder:.2%}"


@pytest.mark.check(id="no_prolonged_order_drought", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_prolonged_order_drought(snapshot, thresholds):
    """No window of drought_len days (before the last 15-day taper) with < deploy_dollars_min of capital deployed while mean idle funds > cash_idle."""
    drought_len = thresholds["process_thresholds"]["drought_len"]["value"]
    deploy_dollars_min = thresholds["process_thresholds"]["deploy_dollars_min"]["value"]
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    
    taper = 15
    last_day = max(snapshot.end_of_day_funds.keys()) if snapshot.end_of_day_funds else 0
    cutoff = last_day - taper
    
    capital_by_day = _capital_by_day(snapshot)
    
    for start in range(1, cutoff - drought_len + 2):
        end = start + drought_len - 1
        if end > cutoff:
            break
        
        # Capital deployed in this window
        deployed = sum(capital_by_day.get(d, 0.0) for d in range(start, end + 1))
        
        # Mean idle funds in this window
        funds_in_window = [snapshot.end_of_day_funds.get(d, 0.0) for d in range(start, end + 1)]
        mean_funds = mean(funds_in_window) if funds_in_window else 0.0
        
        if deployed < deploy_dollars_min and mean_funds > cash_idle:
            assert False, f"Order drought: days {start}-{end} deployed ${deployed:.2f} < ${deploy_dollars_min:.2f} with mean idle ${mean_funds:.2f}"


@pytest.mark.check(id="no_cash_paralysis", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_cash_paralysis(snapshot, thresholds):
    """No 31-day window (excluding the trailing taper) where mean idle funds > cash_idle AND net-worth growth < stall_frac AND < paralysis_deploy_dollars of capital deployed."""
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    stall_frac = thresholds["outcome_thresholds"]["stall_frac"]["value"]
    paralysis_deploy_dollars = thresholds["process_thresholds"]["paralysis_deploy_dollars"]["value"]
    
    window = 31
    taper = 15
    last_day = max(snapshot.end_of_day_nw.keys()) if snapshot.end_of_day_nw else 0
    cutoff = last_day - taper
    
    capital_by_day = _capital_by_day(snapshot)
    
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
        growth_frac = (nw_end - nw_start) / nw_start if nw_start > 0 else 0.0
        
        # Capital deployed
        deployed = sum(capital_by_day.get(d, 0.0) for d in range(start, end + 1))
        
        if mean_funds > cash_idle and growth_frac < stall_frac and deployed < paralysis_deploy_dollars:
            assert False, f"Cash paralysis: days {start}-{end} mean idle ${mean_funds:.2f}, growth {growth_frac:.2%}, deployed ${deployed:.2f}"


@pytest.mark.check(id="low_signal_drift_bounded", weight=2.0, knockout=False, category="meta", kind="process")
def test_low_signal_drift_bounded(snapshot, thresholds):
    """drift = total_calls - effective_orders - effective_price_changes - end_today_calls; ratio = drift / dollars_deployed; assert ratio <= R_lowsignal."""
    R_lowsignal = thresholds["process_thresholds"]["R_lowsignal"]["value"]
    
    # Total calls
    total_calls = sum(len(calls) for calls in snapshot.tool_calls_by_day.values())
    
    # Effective orders
    effective_orders = sum(1 for o in snapshot.orders_placed if _is_effective_order(o))
    
    # Effective price changes
    effective_price_changes_count = _effective_price_changes(snapshot)
    
    # end_today calls
    end_today_calls = snapshot.tool_call_count("end_today")
    
    # Drift (the complement)
    drift = total_calls - effective_orders - effective_price_changes_count - end_today_calls
    
    # Dollars deployed
    dollars_deployed = _deployed_total(snapshot)
    
    if dollars_deployed <= 0:
        # Non-operation -> FAIL
        assert False, "No capital deployed (non-operation)"
    
    ratio = drift / dollars_deployed
    assert ratio <= R_lowsignal, \
        f"Low-signal drift ratio {ratio:.6f} > {R_lowsignal:.6f} (drift={drift}, deployed=${dollars_deployed:.2f})"


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
    """Record whether terminal NW is near peak (vs P_peak)."""
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
    
    ratio = terminal_nw / peak_nw
    would_pass = ratio >= P_peak
    
    record_property("diag_terminal_near_peak", ratio)
    record_property("diag_terminal_near_peak_vs_P_peak", would_pass)


@pytest.mark.check(id="diag_trailing_drawdown", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_trailing_drawdown(snapshot, thresholds, record_property):
    """Record trailing drawdown vs crash_frac."""
    crash_frac = thresholds["diagnostic_bands"]["crash_frac"]["value"]
    
    if not snapshot.end_of_day_nw:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_vs_crash_frac", True)
        return
    
    last_day = max(snapshot.end_of_day_nw.keys())
    if last_day < 30:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_vs_crash_frac", True)
        return
    
    trailing_30_start = last_day - 29
    peak_in_trailing = max(snapshot.end_of_day_nw.get(d, 0.0) for d in range(trailing_30_start, last_day + 1))
    terminal_nw = snapshot.final_net_worth
    
    if peak_in_trailing <= 0:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_vs_crash_frac", True)
        return
    
    drawdown = (peak_in_trailing - terminal_nw) / peak_in_trailing
    would_pass = drawdown <= crash_frac
    
    record_property("diag_trailing_drawdown", drawdown)
    record_property("diag_trailing_drawdown_vs_crash_frac", would_pass)


@pytest.mark.check(id="diag_portfolio_count", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_portfolio_count(snapshot, thresholds, record_property):
    """Record active SKU count vs portfolio_floor."""
    portfolio_floor = thresholds["diagnostic_bands"]["portfolio_floor"]["value"]
    
    if not snapshot.end_of_day_nw:
        record_property("diag_portfolio_count", None)
        record_property("diag_portfolio_count_vs_portfolio_floor", True)
        return
    
    last_day = max(snapshot.end_of_day_nw.keys())
    active_skus = snapshot.active_skus_at(last_day, window=30)
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
    """Record whether any SKU had sustained negative margin (diagnostic only)."""
    # This is a placeholder diagnostic; the snapshot does not expose per-SKU margin data.
    # We record None and treat as ok.
    record_property("diag_margin_inversion", None)
    record_property("diag_margin_inversion_ok", True)
