# Task truth: 000632bd-192b-5d23-8a13-b9af919b1542

This document describes what the task is, how a strong operator runs it, what a good result looks like, and the ways runs fail. The scoring machinery that evaluates a run lives in separate files and is not part of this guide.

The walkthrough and numbers below come from one strong reference run. They show one good way to play the store and set a bar to beat, but they are not the only way and not a script to copy. A sharper operator can beat these numbers, and several different sound approaches can all reach a good result.

## The store you're running

You are running store 15 for 180 days starting September 7, 1991. You open with $30,000 in cash and pay $700 rent every day. The shelf can hold about 25,000 units, though this is a soft limit — extra stock waits in the back room and ties up cash until space opens. You stock twenty categories: Bathroom Tissues, Beer, Bottled Juices, Canned Soup, Canned Tuna, Cereals, Cheeses, Cigarettes, Cookies, Crackers, Dish Detergent, Fabric Softeners, Front-end Candies, Frozen Entrees, Frozen Juices, Oatmeal, Paper Towels, Snack Crackers, Soft Drinks, and Toothpastes.

**How this store works:**

- **Your score is net worth at the end.** Net worth equals cash on hand plus the value of unsold stock you are holding plus any orders still in transit. Unsold stock is valued at what you paid for it, then written down steadily as its shelf life runs out, and counts as zero once it expires. In-transit orders count at their cost. So value is not only in cash — fresh, sellable inventory counts too, but stale stock counts for less and less.
- **Everything is perishable.** Each item has a shelf life, typically a few weeks. Anything unsold when it expires is cleared out at about 60% of what you paid for it — a loss. Over-ordering beyond what can sell in time quietly destroys value, and clearing genuinely near-expiry stock near the end is correct, not a mistake.
- **Returns depend on supplier quality.** Customers return some of what they buy, and you refund them the full shelf price. The return rate is driven by the quality of the supplier the goods came from. The cheapest, lowest-quality suppliers see returns of up to about 30% of units, while top-quality ones see as little as 2%. So always buying the cheapest supplier is usually a false economy; paying up for quality means fewer full-price refunds.
- **Crowding a category cannibalizes it.** Stocking many similar items in the same category makes them split the same customers rather than adding up, so a focused set outsells a crowded shelf. Keeping the product count lean in each category lets each item reach more of its potential.
- **Prices matter, mildly.** Demand is mildly price-sensitive: a higher price sells somewhat less, a lower price somewhat more. The effect is gentle, not dramatic.
- **Deliveries take time.** Orders take several days to arrive, so reordering has to happen before shelves run empty.
- **Customer reviews are on.** Quality slowly shapes demand over time as customers learn which products are reliable.
- **Going broke ends the run.** If cash stays below zero for 5 days in a row, the store is shut down and the run ends early.

### The fixed setup

| **Store** | 15 |
| **Length** | 180 days (from 09/07/91) |
| **Starting cash** | $30,000 |
| **Daily rent** | $700 |
| **Shelf capacity** | 25,000 units (soft limit) |
| **Categories** | 20 categories |
| **Customer reviews** | On |
| **News events** | Off |

> The numbers cited throughout this document come from one reference run. They are ranges and properties to understand, not exact targets to hit.

## What a great run looks like

The reference run closed at **$94,245** net worth after the full 180 days — more than triple the opening cash. Of that, about $81,000 was cash and the rest was lean, sellable inventory still on the shelf. The run dipped briefly in the first few days as opening orders arrived, then recovered and climbed steadily at roughly $440 per day through the middle and late phases. A run that finishes below about $75,000 has fallen short.

## How a strong operator plays it, step by step

This is one good way to run the store, not a fixed recipe. A different sound approach reaching the same kind of result is just as good.

**Opening (days 1–10).** The problem is to fix the unrealistic opening prices, stock the shelves with a focused product set, and survive the cash dip as opening orders arrive. A strong operator reads the catalog to see what is available, picks one or two strong items per category (avoiding a crowded shelf), checks supplier quality and balances cost against return rates, sets sensible prices on everything before selling begins, and places opening orders sized to fill the shelf without tying up too much cash in slow movers. The reference run placed about 90 orders in the first ten days and saw cash dip to about $32 on day 4 before recovering. The operator does not advance the day until prices are set and shelves are stocked, because customers arrive as soon as the day advances.

**Steady state (days 11–160).** The problem is to keep shelves stocked, reorder ahead of stockouts, keep prices stable on durable signals, and let net worth compound. A strong operator checks sales and stock levels each morning, reorders items running low (accounting for the delivery delay), adjusts prices only when a clear pattern emerges over several days (not on one-day blips), and keeps the product set lean so each item gets enough volume to stay fresh. The reference run placed about 9 orders per day, kept prices stable on over 90% of touches, and saw net worth climb at roughly $440 per day. Stockouts happen — the reference run had stockouts on about 108 days — but a strong operator handles them calmly by reordering promptly and not panicking into bad decisions. The operator reads sales and stock data to ground decisions, but does not waste turns re-reading unchanging catalog or supplier information.

**Ending (days 161–180).** The problem is to let inventory run down naturally without a fire sale, keep selling through the last day, and finish with lean but still-sellable stock. A strong operator stops placing large orders in the final weeks, lets the shelf thin as items sell, clears genuinely near-expiry stock at a modest discount if needed, but does not slash prices across the board or stop selling. The reference run closed with about $13,000 in fresh inventory still on the shelf — lean, but not empty. A premature shutdown or a desperate clearance destroys value.

## What a good run has to get right

A good run must satisfy these properties, in its own way:

1. Survive the full 180 days without going broke (cash below zero for 5 consecutive days).
2. End with net worth near or above the reference band, roughly $75,000 or better.
3. Fix the unrealistic opening prices before advancing the first day and letting customers arrive.
4. Stock the shelves with a focused product set before advancing — one or two strong items per category, not a crowded shelf that cannibalizes itself.
5. Choose suppliers by balancing cost and quality to limit returns, not by always picking the cheapest.
6. Reorder ahead of stockouts, accounting for the delivery delay, so popular items stay available.
7. Size orders to shelf life — do not over-order slow movers that will spoil before they sell.
8. Keep prices stable on durable signals, not jumping around on one-day blips or stale reads.
9. Handle stockouts calmly by reordering promptly, not by panicking into bad supplier switches or price cuts.
10. Let inventory run down naturally in the final weeks without a fire sale — finish lean but still selling.
11. Ground pricing and ordering decisions in sales and stock data actually read that day, not on stale or assumed information.
12. Do not waste turns re-reading unchanging catalog or supplier data — read it once early, then focus on the daily sales and stock signals.
13. Recognize that net worth includes cash, inventory, and in-transit orders — do not treat only cash as value.
14. Understand that a focused product set in each category outsells a crowded one, and that paying up for quality suppliers reduces costly returns.

## How runs fail

Runs fail in characteristic ways:

- **Advancing before stocking and pricing.** The operator advances the day before setting prices or placing opening orders, so customers arrive to an empty or mispriced shelf and the run never recovers.
- **Crowding the shelf.** The operator stocks many similar items in each category, so they cannibalize each other and none sells well, tying up cash in slow-moving inventory that spoils.
- **Always buying the cheapest supplier.** The operator chases the lowest cost without checking quality, so return rates soar and full-price refunds destroy margin.
- **Over-ordering slow movers.** The operator places large orders on items that sell slowly, so stock spoils before it sells and value is written down to zero.
- **Ignoring the delivery delay.** The operator waits until shelves are empty to reorder, so stockouts persist for days and sales are lost.
- **Chasing one-day noise.** The operator changes prices or switches suppliers based on a single day's blip, so decisions whipsaw and never settle on a sound strategy.
- **Panicking at stockouts.** The operator sees a stockout and slashes prices or switches to a bad supplier in a rush, destroying margin or inviting returns.
- **Fire-sale ending.** The operator slashes prices across the board in the final weeks to clear inventory, so the run closes with cash but no stock and leaves money on the table.
- **Re-reading unchanging data.** The operator wastes turns reading the catalog or supplier list over and over, so there is no time left to act on the daily sales and stock signals.
- **Treating only cash as value.** The operator believes net worth is only cash and tries to liquidate all inventory, so the run closes with no stock and misses the value in fresh, sellable goods.
- **Going broke early.** The operator over-orders in the opening or mismanages cash through the middle, so cash stays negative for 5 days and the run is shut down.

A strong run avoids all of these.

## The bottom line

The reference run closed at $94,245 net worth after the full 180 days, with about $81,000 in cash and $13,000 in lean, sellable inventory. It survived the opening dip, climbed steadily through the middle at roughly $440 per day, and finished strong without a fire sale. A run that finishes below about $75,000 has fallen short.

---

*This document describes the task and what a good run looks like. The checks used to score a run live in separate files and are not part of this guide. A different, equally sound approach reaching the same kind of result is just as good.*
