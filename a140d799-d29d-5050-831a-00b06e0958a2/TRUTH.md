# Task truth: a140d799-d29d-5050-831a-00b06e0958a2

This document is a plain-language guide to the task, what a strong run looks like, and the requirements a good run must satisfy. The scoring machinery lives elsewhere and is not part of this file.

The walkthrough and numbers below come from one strong reference run. They show a bar to beat and one good way to play the store, but they are not the only way and not a script to copy. A sharper operator can beat these numbers, and several different approaches can all be good runs.

## The store you're running

You are running store 15 for 180 days starting September 7, 1991. You open with $30,000 in cash, pay $700 rent every day, and have a soft shelf capacity of 25,000 units. The store carries twenty categories: Bathroom Tissues, Beer, Bottled Juices, Canned Soup, Canned Tuna, Cereals, Cheeses, Cigarettes, Cookies, Crackers, Dish Detergent, Fabric Softeners, Front-end Candies, Frozen Entrees, Frozen Juices, Oatmeal, Paper Towels, Snack Crackers, Soft Drinks, and Toothpastes.

How this store works:

- **Net worth is the score.** Net worth equals cash on hand plus the value of unsold stock you are holding plus any orders still in transit. Unsold stock is valued at what you paid for it, then written down steadily as its shelf life runs out, and counts as zero once it expires. In-transit orders count at their cost. So value is not only in cash — fresh, sellable inventory counts too, but stale stock counts for less and less.
- **Everything is perishable.** Each item has a shelf life, typically a few weeks. Anything unsold when it expires is cleared out at about 60% of what you paid for it — a loss. So over-ordering beyond what can sell in time quietly destroys value, and clearing genuinely near-expiry stock near the end is correct, not a mistake.
- **Returns depend on supplier quality.** Customers return some of what they buy, and the store refunds them the full shelf price. The return rate is driven by the quality of the supplier the goods came from. The cheapest, lowest-quality suppliers are returned far more often, up to about 30% of units, than top-quality ones, as little as 2%. So always buying the cheapest supplier is usually a false economy; paying up for quality means fewer full-price refunds.
- **Crowding a category cannibalizes it.** Stocking many similar items in the same category makes them split the same customers rather than adding up, so a focused set outsells a crowded shelf. A lean product mix in each category performs better than a sprawling one.
- **Prices matter, mildly.** Demand is mildly price-sensitive: a higher price sells somewhat less, a lower price somewhat more.
- **Shelf capacity is soft.** The shelf limit is not a hard cap on ordering. Extra units wait in the back room and tie up cash until space frees up. Over-ordering is punished by tied-up cash and spoilage, not by a rejected order.
- **Deliveries take time.** Orders take several days to arrive, so reordering has to happen before shelves run empty.
- **Going broke ends the run.** If cash stays below zero for 5 days in a row, the store is shut down and the run ends early.
- **Customer reviews are on.** Quality slowly shapes demand over time as customers learn which products are reliable.

### The fixed setup

| Element | Value |
|---------|-------|
| Store | 15 |
| Length | 180 days (starting 09/07/91) |
| Starting cash | $30,000 |
| Daily rent | $700 |
| Shelf capacity | 25,000 units (soft) |
| Categories | 20 (Bathroom Tissues, Beer, Bottled Juices, Canned Soup, Canned Tuna, Cereals, Cheeses, Cigarettes, Cookies, Crackers, Dish Detergent, Fabric Softeners, Front-end Candies, Frozen Entrees, Frozen Juices, Oatmeal, Paper Towels, Snack Crackers, Soft Drinks, Toothpastes) |
| Customer reviews | On |
| News events | Off |

> The numbers cited throughout this document come from one reference run. They are ranges and properties to understand, not exact targets to hit.

## What a great run looks like

A strong run finishes the full 180 days with a terminal net worth near **$88,800**, roughly 3.0 times the opening cash. Cash at the close is about $73,200, with the rest in lean, sellable inventory. The run dips briefly into negative cash in the opening days, recovers quickly, and then climbs steadily at about $400 per day through the middle and late periods. A run that finishes below $75,000 has fallen short.

## How a strong operator plays it, step by step

This is one good way to run the store, not a fixed recipe.

**Opening (days 1–10).** The problem is to fix the unrealistic opening prices, stock the shelves with a focused product set, and survive the opening cash crunch. A strong operator reads the opening catalog to see what is available, chooses a lean set of items in each category to avoid crowding, and places opening orders that balance supplier quality against cost to limit returns. The operator corrects any wildly mispriced items before selling them, then advances the day to let deliveries arrive and sales begin. For reference, the strong run placed about 90 opening orders, dipped to a cash trough of about negative $17 on day 4, and recovered to positive cash by day 6.

**Steady state (days 11–160).** The problem is to keep shelves stocked, reorder ahead of stockouts, and grow net worth steadily without tying up cash in excess inventory. A strong operator starts each day by reading sales and stock levels, identifies items running low, and places reorders sized to shelf life and recent demand. The operator adjusts prices only when durable signals justify it, not on one-day blips, and keeps the confirmation rate high to avoid churn. The operator monitors cash and net worth to confirm the store is climbing. For reference, the strong run placed about 1,600 orders across the full horizon, roughly 9 per day, and grew net worth at about **$400 per day** through the middle period. The operator kept **92% of price touches** at the existing price, confirming stability. Stockouts happened on about 104 days, handled calmly by reordering rather than panic.

**Ending (days 161–180).** The problem is to finish the horizon without a fire-sale or a pile of expiring stock. A strong operator continues normal operations, lets natural selldown reduce inventory, and clears genuinely near-expiry stock near the close. The operator does not slash prices across the board or stop reordering too early. For reference, the strong run closed with about $73,200 in cash and the rest in lean, sellable inventory, for a terminal net worth of about $88,800.

## What a good run has to get right

A good run must satisfy these properties:

1. Survive the full 180-day horizon without going broke — cash must not stay below zero for 5 consecutive days.
2. End with a terminal net worth near or above the reference band of about $75,000, ideally approaching $88,800.
3. Fix any unrealistic opening prices before selling, so the store does not give away value or repel customers on day one.
4. Stock shelves with opening orders before advancing the first day, so the store has something to sell.
5. Keep a focused product set in each category, avoiding a crowded shelf that cannibalizes itself.
6. Adjust prices on durable signals, not one-day noise, keeping most price touches as confirmations of stability.
7. Choose suppliers balancing quality and cost to limit returns — the cheapest supplier is often a false economy when returns hit 30%.
8. Reorder ahead of stockouts, since deliveries take several days, and handle occasional stockouts calmly by reordering rather than panic.
9. Size orders to shelf life and recent demand, so stock sells before it expires and does not tie up cash in the back room.
10. Let natural selldown reduce inventory near the end, clearing genuinely near-expiry stock, but avoid an endgame fire-sale that destroys value.
11. Ground decisions in data actually read each day — sales, stock levels, and cash — not guesses or stale information.
12. Avoid wasting turns re-reading unchanging catalog data or repeatedly confirming the same prices without reason.
13. Grow net worth steadily through the middle period, showing the store is building value, not just treading water.
14. Close with a lean inventory of sellable stock and strong cash, not a pile of expiring goods or an empty shelf.

## How runs fail

Runs fail in characteristic ways:

- **Ignoring opening prices.** The operator advances the day without correcting wildly mispriced items, giving away value or repelling customers, and never recovers the lost ground.
- **Crowding categories.** The operator stocks too many similar items in the same category, cannibalizing sales and tying up cash in a sprawling product set that underperforms a focused one.
- **Chasing the cheapest supplier.** The operator always buys the lowest-cost supplier, ignoring quality, and bleeds value through 30% return rates and full-price refunds.
- **Reordering too late.** The operator waits until shelves are empty to reorder, misses sales during the multi-day delivery window, and never catches up.
- **Over-ordering beyond shelf life.** The operator places large orders that cannot sell before expiry, quietly destroying value as stock is written down and cleared out at 60% of cost.
- **Price churn.** The operator adjusts prices on one-day blips or re-reads unchanging data repeatedly, wasting turns and creating noise instead of stability.
- **Endgame fire-sale.** The operator slashes prices across the board in the final weeks, destroying value in a panic instead of letting natural selldown work.
- **Running out of cash early.** The operator over-orders in the opening days, stays below zero for 5 consecutive days, and the store is shut down before the horizon.
- **Ignoring data.** The operator makes decisions without reading sales or stock levels, guessing instead of grounding choices in what is actually happening.
- **Treading water.** The operator keeps the store alive but does not grow net worth, ending far below the reference band because no value was built.

A strong run avoids all of these.

## The bottom line

A strong run finishes the full 180 days with a terminal net worth near **$88,800**, about 3.0 times the opening cash. Cash at the close is about $73,200, with the rest in lean, sellable inventory. A run that finishes below $75,000 has fallen short.

---

*This file describes the task and what a good run looks like. The checks used to score a run live in separate files and are not part of this document. A different, equally sound approach reaching the same kind of result is just as good.*
