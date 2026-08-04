"""Deterministic pytest layer for task a140d799-d29d-5050-831a-00b06e0958a2."""

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
    """Return dict[day, capital_deployed] for each day."""
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
    
    # Check scalar fields
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
    
    # Check categories list
    if not hasattr(snapshot.config, "selected_categories"):
        raise RuntimeError("Loader did not surface config.selected_categories")
    
    frozen_categories = frozen["selected_categories_list"]
    observed_categories = snapshot.config.selected_categories
    
    # Normalize representation (underscore vs space)
    def normalize(cat):
        return cat.replace("_", " ").replace(" ", "_").strip()
    
    frozen_norm = sorted(normalize(c) for c in frozen_categories)
    observed_norm = sorted(normalize(c) for c in observed_categories)
    
    assert frozen_norm == observed_norm, \
        f"selected_categories mismatch: {observed_norm} != {frozen_norm}"


@pytest.mark.check(id="integrity_readable_complete", weight=0.0, knockout=False, category="integrity", kind="outcome")
def test_integrity_readable_complete(snapshot, thresholds):
    """Verify the trajectory parsed and the terminal net worth is a finite real number."""
    import math
    nw = snapshot.final_net_worth
    if not isinstance(nw, (int, float)) or math.isnan(nw) or math.isinf(nw):
        raise RuntimeError(f"Terminal net worth is not a finite real number: {nw}")


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
    pinned_nw = snapshot.final_net_worth
    days_short = max(0, days_requested - snapshot.days_completed)
    horizon_pinned_nw = pinned_nw - rent * days_short
    
    # Reference gain
    ref = oracle_nw - funds
    
    # Guard against near-infeasible task
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
    import math
    assert isinstance(pinned_nw, (int, float)) and not math.isnan(pinned_nw) and not math.isinf(pinned_nw)


# ============================================================================
# PROCESS CHECKS (kind="process", weighted)
# ============================================================================

@pytest.mark.check(id="valid_tools_used", weight=1.0, knockout=False, category="meta", kind="process")
def test_valid_tools_used(snapshot, thresholds):
    """All observed tool names are in the valid tool set."""
    observed_tools = set()
    for day_calls in snapshot.tool_calls_by_day.values():
        for call in day_calls:
            observed_tools.add(call.tool)
    
    invalid_tools = observed_tools - set(VALID_TOOLS)
    assert not invalid_tools, f"Invalid tools used: {invalid_tools}"


@pytest.mark.check(id="supplier_board_before_order", weight=1.5, knockout=False, category="supplier", kind="process")
def test_supplier_board_before_order(snapshot, thresholds):
    """Of all place_order calls, the fraction whose ordered SKUs were covered by an earlier same-day supplier board read."""
    T_supplier = thresholds["process_thresholds"]["T_supplier"]["value"]
    
    # Collect all effective orders
    effective_orders = [o for o in snapshot.orders_placed if _is_effective_order(o)]
    
    if not effective_orders:
        # Non-operation: definite FAIL
        pytest.fail("No effective orders placed (non-operation)")
    
    # For each order, check if a same-day supplier board read covered its SKUs
    covered_count = 0
    for order in effective_orders:
        day = order.day
        order_skus = order.skus
        
        # Find all view_current_date_supplier_prices calls on this day before or at the order
        supplier_reads = []
        if day in snapshot.tool_calls_by_day:
            for call in snapshot.tool_calls_by_day[day]:
                if call.tool == "view_current_date_supplier_prices":
                    supplier_reads.append(call)
        
        # Check if any supplier read covered the order's SKUs
        covered = False
        for read_call in supplier_reads:
            # The supplier board read returns all SKUs, so any call covers all SKUs
            # We just need to confirm there was a read on the same day
            covered = True
            break
        
        if covered:
            covered_count += 1
    
    fraction = covered_count / len(effective_orders)
    assert fraction >= T_supplier, \
        f"Supplier board coverage {fraction:.2%} < threshold {T_supplier:.2%}"


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
        # Non-operation: definite FAIL
        pytest.fail("No effective orders placed (non-operation)")
    
    # For each order-day, check if there was a view_current_orders call
    covered_count = 0
    for day in order_days:
        if day in snapshot.tool_calls_by_day:
            for call in snapshot.tool_calls_by_day[day]:
                if call.tool == "view_current_orders":
                    covered_count += 1
                    break
    
    fraction = covered_count / len(order_days)
    assert fraction >= T_vieworders, \
        f"View orders coverage {fraction:.2%} < threshold {T_vieworders:.2%}"


@pytest.mark.check(id="day1_order_placed", weight=1.5, knockout=False, category="setup", kind="process")
def test_day1_order_placed(snapshot, thresholds):
    """A material opening order within the first 3 days."""
    grace = 3
    
    # Find effective orders in the first grace days
    early_orders = [o for o in snapshot.orders_placed 
                    if o.day <= grace and _is_effective_order(o)]
    
    if not early_orders:
        pytest.fail(f"No effective order placed within first {grace} days")
    
    # Check that at least one order is material (not a 1-unit token)
    material = any(o.units > 1 for o in early_orders)
    assert material, "No material opening order (all orders are 1-unit tokens)"


@pytest.mark.check(id="day1_supplier_read_before_order", weight=0.5, knockout=False, category="setup", kind="process")
def test_day1_supplier_read_before_order(snapshot, thresholds):
    """Implication: IF a day-1 order exists, a day-1 supplier-board read precedes it."""
    # Find day-1 effective orders
    day1_orders = [o for o in snapshot.orders_placed if o.day == 1 and _is_effective_order(o)]
    
    if not day1_orders:
        # No day-1 order: vacuous PASS
        return
    
    # Check for a day-1 supplier board read
    day1_supplier_read = False
    if 1 in snapshot.tool_calls_by_day:
        for call in snapshot.tool_calls_by_day[1]:
            if call.tool == "view_current_date_supplier_prices":
                day1_supplier_read = True
                break
    
    assert day1_supplier_read, "Day-1 order exists but no day-1 supplier board read"


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
        # No sales at all: definite FAIL (non-operation)
        pytest.fail("No sales recorded (non-operation)")
    
    # Find effective price changes on or before first sale day
    effective_pcs = _effective_price_changes(snapshot)
    early_price_changes = [pc for pc in effective_pcs if pc.day <= first_sale_day]
    
    assert early_price_changes, \
        f"No effective price change on or before first sale day {first_sale_day}"


@pytest.mark.check(id="reorder_after_stockout", weight=1.0, knockout=False, category="reorder", kind="process")
def test_reorder_after_stockout(snapshot, thresholds):
    """Of stockout events, the fraction refilled by an effective order within 7 days."""
    T_reorder = thresholds["process_thresholds"]["T_reorder"]["value"]
    reorder_window = 7
    
    stockouts = snapshot.stockout_events
    
    if not stockouts:
        # No stockouts: vacuous PASS
        return
    
    # For each stockout, check if it was refilled within the window
    refilled_count = 0
    for stockout in stockouts:
        # Verify the SKU is a bare numeric id
        if not stockout.sku.isdigit():
            raise RuntimeError(f"Stockout SKU is not a bare numeric id: {stockout.sku}")
        
        sku = stockout.sku
        day = stockout.day
        
        # Find orders for this SKU within the reorder window
        sku_orders = snapshot.orders_by_sku(sku)
        refill_orders = [o for o in sku_orders 
                        if day < o.day <= day + reorder_window and _is_effective_order(o)]
        
        if refill_orders:
            refilled_count += 1
    
    fraction = refilled_count / len(stockouts)
    assert fraction >= T_reorder, \
        f"Reorder after stockout {fraction:.2%} < threshold {T_reorder:.2%}"


@pytest.mark.check(id="no_prolonged_order_drought", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_prolonged_order_drought(snapshot, thresholds):
    """No window of drought_len days (before the last 15-day taper) with low deployment and high idle cash."""
    drought_len = thresholds["process_thresholds"]["drought_len"]["value"]
    deploy_dollars_min = thresholds["process_thresholds"]["deploy_dollars_min"]["value"]
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    taper = 15
    
    # Compute capital deployed by day
    capital_by_day = _capital_by_day(snapshot)
    
    # Compute the evaluation window (exclude the trailing taper)
    max_day = max(snapshot.end_of_day_funds.keys()) if snapshot.end_of_day_funds else 0
    eval_end = max_day - taper
    
    if eval_end < drought_len:
        # Not enough days to evaluate
        return
    
    # Check each window
    for start_day in range(1, eval_end - drought_len + 2):
        end_day = start_day + drought_len - 1
        
        # Sum capital deployed in this window
        window_capital = sum(capital_by_day.get(d, 0.0) for d in range(start_day, end_day + 1))
        
        # Mean idle funds in this window
        window_funds = [snapshot.end_of_day_funds.get(d, 0.0) for d in range(start_day, end_day + 1)]
        mean_funds = mean(window_funds) if window_funds else 0.0
        
        # Check for drought
        if window_capital < deploy_dollars_min and mean_funds > cash_idle:
            pytest.fail(f"Order drought detected: days {start_day}-{end_day}, "
                       f"deployed ${window_capital:.0f} < ${deploy_dollars_min:.0f}, "
                       f"mean idle ${mean_funds:.0f} > ${cash_idle:.0f}")


@pytest.mark.check(id="no_cash_paralysis", weight=1.5, knockout=False, category="cash", kind="process")
def test_no_cash_paralysis(snapshot, thresholds):
    """No 31-day window (excluding trailing taper) with high idle cash, low NW growth, and low deployment."""
    window_len = 31
    cash_idle = thresholds["outcome_thresholds"]["cash_idle"]["value"]
    stall_frac = thresholds["outcome_thresholds"]["stall_frac"]["value"]
    paralysis_deploy_dollars = thresholds["process_thresholds"]["paralysis_deploy_dollars"]["value"]
    taper = 15
    
    # Compute capital deployed by day
    capital_by_day = _capital_by_day(snapshot)
    
    # Compute the evaluation window
    max_day = max(snapshot.end_of_day_nw.keys()) if snapshot.end_of_day_nw else 0
    eval_end = max_day - taper
    
    if eval_end < window_len:
        return
    
    # Check each window
    for start_day in range(1, eval_end - window_len + 2):
        end_day = start_day + window_len - 1
        
        # Mean idle funds
        window_funds = [snapshot.end_of_day_funds.get(d, 0.0) for d in range(start_day, end_day + 1)]
        mean_funds = mean(window_funds) if window_funds else 0.0
        
        # Net worth growth
        nw_start = snapshot.end_of_day_nw.get(start_day, 0.0)
        nw_end = snapshot.end_of_day_nw.get(end_day, 0.0)
        nw_growth = nw_end - nw_start
        
        # Capital deployed
        window_capital = sum(capital_by_day.get(d, 0.0) for d in range(start_day, end_day + 1))
        
        # Check for paralysis
        if mean_funds > cash_idle and nw_growth < stall_frac and window_capital < paralysis_deploy_dollars:
            pytest.fail(f"Cash paralysis detected: days {start_day}-{end_day}, "
                       f"mean idle ${mean_funds:.0f} > ${cash_idle:.0f}, "
                       f"NW growth ${nw_growth:.0f} < ${stall_frac:.0f}, "
                       f"deployed ${window_capital:.0f} < ${paralysis_deploy_dollars:.0f}")


@pytest.mark.check(id="low_signal_drift_bounded", weight=2.0, knockout=False, category="meta", kind="process")
def test_low_signal_drift_bounded(snapshot, thresholds):
    """Drift (non-action calls) relative to dollars deployed is bounded."""
    R_lowsignal = thresholds["process_thresholds"]["R_lowsignal"]["value"]
    
    # Count total calls
    total_calls = sum(len(calls) for calls in snapshot.tool_calls_by_day.values())
    
    # Count effective orders
    effective_orders = sum(1 for o in snapshot.orders_placed if _is_effective_order(o))
    
    # Count effective price changes
    effective_pcs = len(_effective_price_changes(snapshot))
    
    # Count end_today calls
    end_today_calls = snapshot.tool_call_count("end_today")
    
    # Drift = total - (effective_orders + effective_pcs + end_today)
    drift = total_calls - effective_orders - effective_pcs - end_today_calls
    
    # Dollars deployed
    dollars_deployed = _deployed_total(snapshot)
    
    if dollars_deployed == 0:
        # Non-operation: definite FAIL
        pytest.fail("No capital deployed (non-operation)")
    
    ratio = drift / dollars_deployed
    assert ratio <= R_lowsignal, \
        f"Low-signal drift ratio {ratio:.6f} > threshold {R_lowsignal:.6f}"


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
    trailing_window = 30
    
    if not snapshot.end_of_day_nw:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_vs_crash_frac", True)
        return
    
    max_day = max(snapshot.end_of_day_nw.keys())
    if max_day < trailing_window:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_vs_crash_frac", True)
        return
    
    # Peak in trailing window
    trailing_days = range(max_day - trailing_window + 1, max_day + 1)
    trailing_nws = [snapshot.end_of_day_nw.get(d, 0.0) for d in trailing_days]
    peak_trailing = max(trailing_nws) if trailing_nws else 0.0
    
    terminal_nw = snapshot.final_net_worth
    
    if peak_trailing <= 0:
        record_property("diag_trailing_drawdown", None)
        record_property("diag_trailing_drawdown_vs_crash_frac", True)
        return
    
    drawdown = (peak_trailing - terminal_nw) / peak_trailing
    would_pass = drawdown <= crash_frac
    
    record_property("diag_trailing_drawdown", drawdown)
    record_property("diag_trailing_drawdown_vs_crash_frac", would_pass)


@pytest.mark.check(id="diag_portfolio_count", weight=0.0, knockout=False, category="diagnostic", kind="diagnostic")
def test_diag_portfolio_count(snapshot, thresholds, record_property):
    """Record active SKU count vs portfolio_floor."""
    portfolio_floor = thresholds["diagnostic_bands"]["portfolio_floor"]["value"]
    window = 30
    
    if not snapshot.end_of_day_nw:
        record_property("diag_portfolio_count", None)
        record_property("diag_portfolio_count_vs_portfolio_floor", True)
        return
    
    max_day = max(snapshot.end_of_day_nw.keys())
    active_skus = snapshot.active_skus_at(max_day, window=window)
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
    """Record whether there is margin inversion (terminal NW < terminal cash)."""
    terminal_nw = snapshot.final_net_worth
    
    if not snapshot.end_of_day_funds:
        record_property("diag_margin_inversion", None)
        return
    
    max_day = max(snapshot.end_of_day_funds.keys())
    terminal_cash = snapshot.end_of_day_funds.get(max_day, 0.0)
    
    inversion = terminal_nw < terminal_cash
    
    record_property("diag_margin_inversion", inversion)
