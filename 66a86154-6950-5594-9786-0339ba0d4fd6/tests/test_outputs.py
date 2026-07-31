"""Deterministic pytest layer for RetailBench task 66a86154-6950-5594-9786-0339ba0d4fd6."""

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
    """Return dict[day, capital_deployed] for each day with effective orders."""
    cap_by_day = {}
    for order in snapshot.orders_placed:
        if _is_effective_order(order):
            cap_by_day[order.day] = cap_by_day.get(order.day, 0.0) + order.cost
    return cap_by_day


def _deployed_total(snapshot):
    """Return total capital deployed across all effective orders."""
    return sum(_order_capital(o) for o in snapshot.orders_placed)


@pytest.mark.check(id="integrity_config_matches_frozen_task", weight=0.0, knockout=False, category="integrity", kind="outcome")
def test_integrity_config_matches_frozen_task(snapshot, thresholds):
    """Verify the run's config matches the frozen task config."""
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
    
    def normalize_cat(c):
        return c.replace("_", " ").strip().lower()
    
    frozen_norm = sorted(normalize_cat(c) for c in frozen_cats)
    observed_norm = sorted(normalize_cat(c) for c in observed_cats)
    
    assert observed_norm == frozen_norm, f"selected_categories mismatch: {observed_cats} vs {frozen_cats}"


@pytest.mark.check(id="integrity_readable_complete", weight=0.0, knockout=False, category="integrity", kind="outcome")
def test_integrity_readable_complete(snapshot, thresholds):
    """Verify the trajectory parsed and the terminal net worth is a finite real number."""
    nw = snapshot.final_net_worth
    if not isinstance(nw, (int, float)):
        raise RuntimeError(f"final_net_worth is not a number: {type(nw)}")
    if not (-1e15 < nw < 1e15):
        raise RuntimeError(f"final_net_worth is not finite: {nw}")


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
        raw_O = (horizon_pinned_nw - funds) / ref
        O = max(0.0, min(1.0, raw_O))
    
    band = "MADE-MONEY" if horizon_pinned_nw > funds else "LOST-MONEY"
    
    record_property("pinned_net_worth", pinned_nw)
    record_property("horizon_pinned_net_worth", horizon_pinned_nw)
    record_property("money_outcome_O", O)
    record_property("money_band", band)
    
    # Assert only that the pinned value is a real number
    assert isinstance(pinned_nw, (int, float)) and -1e15 < pinned_nw < 1e15


@pytest.mark.check(id="valid_tools_used", weight=1.0, knockout=False, category="meta", kind="process")
def test_valid_tools_used(snapshot, thresholds):
    """All observed tool names are in the valid tool set."""
    observed = set()
    for day_calls in snapshot.tool_calls_by_day.values():
        for call in day_calls:
            observed.add(call.tool)
    
    assert observed <= set(VALID_TOOLS), f"Invalid tools: {observed - set(VALID_TOOLS)}"


@pytest.mark.check(id="supplier_board_before_order", weight=1.5, knockout=False, category="supplier", kind="process")
def test_supplier_board_before_order(snapshot, thresholds):
    """Of all place_order calls, the fraction whose ordered SKUs were covered by an earlier same-day view_current_date_supplier_prices >= T_supplier."""
    T = thresholds["process_thresholds"]["T_supplier"]["value"]
    
    order_calls = []
    for day, calls in snapshot.tool_calls_by_day.items():
        for call in calls:
            if call.tool == "place_order":
                order_calls.append((day, call))
    
    if not order_calls:
        # No orders placed → definite FAIL (non-operation)
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
        same_day_calls = snapshot.tool_calls_by_day.get(day, [])
        read_skus = set()
        for call in same_day_calls:
            if call.tool == "view_current_date_supplier_prices":
                sku_ids = call.args.get("sku_ids", [])
                for sid in sku_ids:
                    read_skus.add(str(sid))
            if call.tool == "place_order" and call is order_call:
                # Stop at this order call
                break
        
        if order_skus <= read_skus:
            covered += 1
    
    coverage = covered / len(order_calls)
    assert coverage >= T, f"Supplier board coverage {coverage:.2%} < {T:.2%}"


@pytest.mark.check(id="view_orders_before_place", weight=1.0, knockout=False, category="reorder", kind="process")
def test_view_orders_before_place(snapshot, thresholds):
    """Of order-days, the fraction with an earlier same-day view_current_orders >= T_vieworders."""
    T = thresholds["process_thresholds"]["T_vieworders"]["value"]
    
    order_days = set()
    for order in snapshot.orders_placed:
        if _is_effective_order(order):
            order_days.add(order.day)
    
    if not order_days:
        # No effective orders → definite FAIL (non-operation)
        assert False, "No effective orders placed (non-operation)"
    
    covered = 0
    for day in order_days:
        same_day_calls = snapshot.tool_calls_by_day.get(day, [])
        view_before_order = False
        for call in same_day_calls:
            if call.tool == "view_current_orders":
                view_before_order = True
            if call.tool == "place_order":
                break
        if view_before_order:
            covered += 1
    
    coverage = covered / len(order_days)
    assert coverage >= T, f"view_current_orders before place coverage {coverage:.2%} < {T:.2%}"


@pytest.mark.check(id="day1_order_placed", weight=1.5, knockout=False, category="setup", kind="process")
def test_day1_order_placed(snapshot, thresholds):
    """A material (effective) opening order within the first 3 days."""
    grace = 3
    early_orders = [o for o in snapshot.orders_placed if o.day <= grace and _is_effective_order(o)]
    assert early_orders, f"No effective order within first {grace} days"


@pytest.mark.check(id="day1_supplier_read_before_order", weight=0.5, knockout=False, category="setup", kind="process")
def test_day1_supplier_read_before_order(snapshot, thresholds):
    """Implication: IF a day-1 order exists, a day-1 supplier-board read precedes it."""
    day1_orders = [o for o in snapshot.orders_placed if o.day == 1 and _is_effective_order(o)]
    if not day1_orders:
        # No day-1 order → vacuous PASS
        return
    
    day1_calls = snapshot.tool_calls_by_day.get(1, [])
    supplier_read_before_order = False
    for call in day1_calls:
        if call.tool == "view_current_date_supplier_prices":
            supplier_read_before_order = True
        if call.tool == "place_order":
            break
    
    assert supplier_read_before_order, "Day-1 order exists but no day-1 supplier read precedes it"


@pytest.mark.check(id="priced_before_first_sale", weight=1.0, knockout=False, category="setup", kind="process")
def test_priced_before_first_sale(snapshot, thresholds):
    """An EFFECTIVE price change on or before the first day with nonzero sales."""
    first_sale_day = None
    for day in sorted(snapshot.sales_units_by_day.keys()):
        if snapshot.sales_units_by_day[day] > 0:
            first_sale_day = day
            break
    
    if first_sale_day is None:
        # No sales at all → definite FAIL (non-operation)
        assert False, "No sales recorded (non-operation)"
    
    effective_pcs = _effective_price_changes(snapshot)
    early_pcs = [pc for pc in effective_pcs if pc.day <= first_sale_day]
    
    assert early_pcs, f"No effective price change on or before first sale day {first_sale_day}"


@pytest.mark.check(id="reorder_after_stockout", weight=1.0, knockout=False, category="reorder", kind="process")
def test_reorder_after_stockout(snapshot, thresholds):
    """Of stockout events, the fraction refilled by an effective order within 7 days >= T_reorder."""
    T = thresholds["process_thresholds"]["T_reorder"]["value"]
    window = 7
    
    stockouts = snapshot.stockout_events
    if not stockouts:
        # No stockouts → vacuous PASS
        return
    
    refilled = 0
    for stockout in stockouts:
        # Verify the SKU is a bare numeric id
        if not isinstance(stockout.sku, str) or not stockout.sku.isdigit():
            raise RuntimeError(f"Stockout SKU is not a bare numeric id: {stockout.sku}")
        
        sku = stockout.sku
        day = stockout.day
        
        # Check for an effective order of this SKU within 7 days
        later_orders = [o for o in snapshot.orders_by_sku(sku) if day < o.day <= day + window and _is_effective_order(o)]
        if later_orders:
            refilled += 1
    
    coverage = refilled / len(stockouts)
    assert coverage >= T, f"Reorder after stockout coverage {coverage:.2%} < {T:.2%}"


@pytest.mark.check(id="no_prolonged_order_drought", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_prolonged_order_drought(snapshot, thresholds):
    """No window of drought_len days (before the last 15-day taper) with < deploy_dollars_min of capital deployed while mean idle funds > cash_idle."""
    drought_len = thresholds["process_thresholds"]["drought_len"]["value"]
    deploy_min = thresholds["process_thresholds"]["deploy_dollars_min"]["value"]
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    taper = 15
    
    cap_by_day = _capital_by_day(snapshot)
    funds_by_day = snapshot.end_of_day_funds
    
    last_eval_day = snapshot.days_completed - taper
    if last_eval_day < drought_len:
        # Horizon too short to evaluate
        return
    
    for start in range(1, last_eval_day - drought_len + 2):
        end = start + drought_len - 1
        window_days = range(start, end + 1)
        
        deployed = sum(cap_by_day.get(d, 0.0) for d in window_days)
        funds_vals = [funds_by_day.get(d, 0.0) for d in window_days if d in funds_by_day]
        if not funds_vals:
            continue
        mean_funds = mean(funds_vals)
        
        if deployed < deploy_min and mean_funds > cash_idle:
            assert False, f"Prolonged order drought: days {start}-{end}, deployed ${deployed:.2f} < ${deploy_min:.2f}, mean idle ${mean_funds:.2f} > ${cash_idle:.2f}"


@pytest.mark.check(id="no_cash_paralysis", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_cash_paralysis(snapshot, thresholds):
    """No 31-day window (excluding trailing taper) where mean idle funds > cash_idle AND net-worth growth < stall_frac AND < paralysis_deploy_dollars of capital deployed."""
    window_len = 31
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    stall_frac = thresholds["outcome_thresholds"]["stall_frac"]["value"]
    paralysis_deploy = thresholds["process_thresholds"]["paralysis_deploy_dollars"]["value"]
    taper = 15
    
    cap_by_day = _capital_by_day(snapshot)
    funds_by_day = snapshot.end_of_day_funds
    nw_by_day = snapshot.end_of_day_nw
    
    last_eval_day = snapshot.days_completed - taper
    if last_eval_day < window_len:
        return
    
    for start in range(1, last_eval_day - window_len + 2):
        end = start + window_len - 1
        window_days = range(start, end + 1)
        
        deployed = sum(cap_by_day.get(d, 0.0) for d in window_days)
        funds_vals = [funds_by_day.get(d, 0.0) for d in window_days if d in funds_by_day]
        if not funds_vals:
            continue
        mean_funds = mean(funds_vals)
        
        nw_start = nw_by_day.get(start)
        nw_end = nw_by_day.get(end)
        if nw_start is None or nw_end is None or nw_start <= 0:
            continue
        growth = (nw_end - nw_start) / nw_start
        
        if mean_funds > cash_idle and growth < stall_frac and deployed < paralysis_deploy:
            assert False, f"Cash paralysis: days {start}-{end}, mean idle ${mean_funds:.2f} > ${cash_idle:.2f}, growth {growth:.2%} < {stall_frac:.2%}, deployed ${deployed:.2f} < ${paralysis_deploy:.2f}"


@pytest.mark.check(id="low_signal_drift_bounded", weight=2.0, knockout=False, category="meta", kind="process")
def test_low_signal_drift_bounded(snapshot, thresholds):
    """drift / dollars_deployed <= R_lowsignal, where drift = total_calls - effective_orders - effective_price_changes - end_today_calls."""
    R = thresholds["process_thresholds"]["R_lowsignal"]["value"]
    
    total_calls = sum(len(calls) for calls in snapshot.tool_calls_by_day.values())
    effective_orders = sum(1 for o in snapshot.orders_placed if _is_effective_order(o))
    effective_pcs = len(_effective_price_changes(snapshot))
    end_today_calls = snapshot.tool_call_count("end_today")
    
    drift = total_calls - effective_orders - effective_pcs - end_today_calls
    dollars_deployed = _deployed_total(snapshot)
    
    if dollars_deployed <= 0:
        # No capital deployed → definite FAIL (non-operation)
        assert False, "No capital deployed (non-operation)"
    
    ratio = drift / dollars_deployed
    assert ratio <= R, f"Low-signal drift ratio {ratio:.6f} > {R:.6f} (drift={drift}, deployed=${dollars_deployed:.2f})"


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
    record_property("diag_terminal_growth_multiple_ok", ok)


@pytest.mark.check(id="diag_terminal_near_peak", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_terminal_near_peak(snapshot, thresholds, record_property):
    """Record whether terminal NW is near peak (within P_peak of max)."""
    P_peak = thresholds["diagnostic_bands"]["P_peak"]["value"]
    
    nw_vals = list(snapshot.end_of_day_nw.values())
    if not nw_vals:
        record_property("diag_terminal_near_peak", None)
        record_property("diag_terminal_near_peak_ok", True)
        return
    
    peak = max(nw_vals)
    terminal = snapshot.final_net_worth
    
    if peak <= 0:
        record_property("diag_terminal_near_peak", None)
        record_property("diag_terminal_near_peak_ok", True)
        return
    
    drawdown = (peak - terminal) / peak
    ok = drawdown <= P_peak
    
    record_property("diag_terminal_near_peak_drawdown", drawdown)
    record_property("diag_terminal_near_peak_ok", ok)


@pytest.mark.check(id="diag_trailing_drawdown", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_trailing_drawdown(snapshot, thresholds, record_property):
    """Record trailing drawdown vs crash_frac."""
    crash_frac = thresholds["diagnostic_bands"]["crash_frac"]["value"]
    window = 30
    
    nw_by_day = snapshot.end_of_day_nw
    if snapshot.days_completed < window:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_ok", True)
        return
    
    trailing_days = range(snapshot.days_completed - window + 1, snapshot.days_completed + 1)
    trailing_vals = [nw_by_day.get(d) for d in trailing_days if d in nw_by_day]
    
    if not trailing_vals:
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
    window = 30
    
    if snapshot.days_completed < window:
        record_property("diag_portfolio_count", None)
        record_property("diag_portfolio_count_ok", True)
        return
    
    mid_day = snapshot.days_completed // 2
    active = snapshot.active_skus_at(mid_day, window=window)
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
    """Record whether any price changes inverted margin (new price < cost)."""
    inversions = []
    for pc in snapshot.price_changes:
        # We don't have cost data in the snapshot, so we cannot compute this diagnostic.
        # Record None and treat as ok.
        pass
    
    record_property("diag_margin_inversion", None)
    record_property("diag_margin_inversion_ok", True)
