# Task truth: 626f0435-a919-5ee8-8e2a-82c886a789b6

This document describes the task, what a strong run looks like, and the properties a good run must satisfy. The scoring machinery lives elsewhere and is not part of this file.

The walkthrough and numbers below come from one strong reference run. They show a bar to beat and one good way to play the store, but they are not the only way and not a script to copy. A sharper operator can beat these numbers, and several different approaches can all be good.

## The store you're running

You are running store 15 for 180 days starting September 7, 1991. You open with $5000 in cash and pay $120 in rent every day. The shelf can hold about 6000 units, though this is a soft limit — extra stock waits in the back room and ties up cash until space frees up. You stock four categories: Cheeses, Frozen Entrees, Snack Crackers, and Soft Drinks.

How this store works:

- **Net worth is the score.** Net worth equals cash on hand plus the value of unsold stock you are holding plus any orders still in transit. Unsold stock is valued at what you paid for it, then written down steadily as its shelf life runs out, and counts as zero once it expires. In-transit orders count at their cost. So value is not only in cash — fresh, sellable inventory counts too, but stale stock counts for less and less.
- **Returns depend on supplier quality.** Customers return some of what they buy, and the store refunds them the full shelf price. The return rate is driven by the quality of the supplier the goods came from. The cheapest, lowest-quality suppliers are returned far more often (up to about 30% of units) than top-quality ones (as little as 2%). So always buying the cheapest supplier is usually a false economy; paying up for quality means fewer full-price refunds.
- **Everything is perishable.** Each item has a shelf life, typically a few weeks. Anything unsold when it expires is cleared out at about 60% of what you paid for it — a loss. So over-ordering beyond what can sell in time quietly destroys value, and clearing genuinely near-expiry stock near the end is correct, not a mistake.
- **Crowding a category cannibalizes it.** Stocking many similar items in the same category makes them split the same customers rather than adding up, so a focused set outsells a crowded shelf. When you raise the price on one item, some of its demand shifts to other active items in the same category, and vice versa. A lean, focused product set avoids this splitting.
- **Prices matter, mildly.** Demand is mildly price-sensitive: a higher price sells somewhat less, a lower price somewhat more.
- **Shelf capacity is soft.** The shelf limit is not a hard cap on ordering. Extra units wait in the back room and tie up cash until space frees up. Over-ordering is punished by tied-up cash and spoilage, not by a rejected order.
- **Deliveries take time.** Orders take several days to arrive, so reordering has to happen before shelves run empty.
- **Going broke ends the run.** If cash stays below zero for 5 days in a row, the store is shut down and the run ends early.
- **Customer reviews are on.** Quality slowly shapes demand over time as customers learn which products are good.

### The fixed setup

| **Store**            | 15                                      |
|----------------------|-----------------------------------------|
| **Length**           | 180 days (starting 09/07/91)            |
| **Starting cash**    | $5000                                   |
| **Daily rent**       | $120                                    |
| **Shelf capacity**   | 6000 units (soft limit)                 |
| **Categories**       | Cheeses, Frozen Entrees, Snack Crackers, Soft Drinks |
| **Customer reviews** | On                                      |
| **News events**      | Off                                     |

> The numbers cited below come from one reference run and are ranges or properties to aim for, not exact targets to hit.

## What a great run looks like

The reference run closed at **$22,066** in net worth, more than four times the opening cash, after completing all 180 days. At the close, about $20,000 was in cash and the rest in lean, sellable inventory. The run dipped briefly into the red in the first few days, recovered quickly, and then climbed steadily at roughly $120 per day through the middle and late stages. A run that falls short of about $18,000 has left significant value on the table.

## How a strong operator plays it, step by step

This is one good way to play the store, not a fixed recipe.

**Opening (days 1–5).** The problem is that the catalog's default prices are often wildly unrealistic, and the opening cash is tight. A strong operator reads the catalog, fixes the obviously broken prices before selling anything, and places a careful first order that stocks the shelves without draining the bank. The reference run touched prices on most SKUs in the first day or two, keeping about 93% of them unchanged and correcting the rest. The first orders went to mid-to-high-quality suppliers to limit returns, and the operator sized them to fit the shelf and the budget. Cash dipped briefly below zero on day 3 (to about negative $100) but recovered within a day as the first sales came in.

**Steady state (days 6–160).** The problem is to keep shelves stocked, prices stable, and the product set focused while the store grows. A strong operator settles into a daily rhythm: check for stockouts and reorder ahead of them, adjust prices only when demand or cost signals are clear and durable (not one-day blips), and keep the active product count lean to avoid cannibalizing sales within each category. The reference run placed about 340 orders across the full 180 days, roughly two per day, and confirmed existing prices on about 93% of the touches it made. It ran stockouts on about 36 days, handling them calmly by reordering and moving on. The net worth climbed steadily at about $120 per day through this phase, compounding the opening stake into a growing cash cushion.

**Ending (days 161–180).** The problem is to convert the remaining inventory into cash without a fire sale. A strong operator stops placing large new orders, lets the shelves run down naturally, and clears genuinely near-expiry stock at a modest discount if needed. The reference run closed with about $20,000 in cash and a small amount of fresh inventory still on hand, not an empty store sold at a loss.

## What a good run has to get right

A good run must satisfy these properties:

1. Survive the full 180-day horizon without going broke (cash below zero for 5 consecutive days).
2. End near or above the reference band of about $18,000 to $22,000 in net worth.
3. Fix the unrealistic opening prices in the catalog before selling significant volume.
4. Stock the shelves with a focused product set before advancing through the early days.
5. Keep the active product count lean in each category to avoid splitting demand across too many similar items.
6. Adjust prices on durable signals (sustained demand shifts, cost changes, quality trends), not on one-day blips or noise.
7. Choose suppliers on a balance of quality and cost to limit returns — the cheapest supplier is rarely the best value.
8. Reorder ahead of stockouts so deliveries arrive before shelves run empty.
9. Size orders to shelf life so stock sells before it expires and loses value.
10. Handle stockouts calmly when they happen — reorder and move on, do not panic or over-correct.
11. Avoid an endgame fire sale — let inventory run down naturally and clear only genuinely near-expiry stock.
12. Ground pricing and ordering decisions in data actually read from the tools, not guesses.
13. Do not waste turns re-reading static data that has not changed since the last check.
14. Let the net worth climb steadily through the middle of the run, compounding the opening stake into a growing cushion.

## How runs fail

How runs typically fail:

- **Ignoring the opening prices.** Selling at the catalog's broken default prices for days or weeks bleeds value through mispriced sales and missed margin.
- **Over-ordering in the opening.** Draining the bank on a huge first order leaves no cash to survive the first week, and the run goes broke before sales recover it.
- **Crowding the shelves.** Stocking too many similar items in the same category splits their demand and lowers total sales, leaving cash tied up in slow-moving stock.
- **Chasing noise.** Adjusting prices or orders based on one-day blips rather than durable signals creates churn and destroys stable growth.
- **Always buying the cheapest supplier.** The lowest-cost supplier often has the highest return rate, and refunding 30% of sales at full shelf price is a quiet disaster.
- **Reordering too late.** Waiting until shelves are empty means deliveries arrive after days of lost sales, and the missed revenue never comes back.
- **Over-ordering beyond shelf life.** Ordering more than can sell before expiry ties up cash in stock that will be cleared at a 40% loss.
- **Panicking at stockouts.** Over-correcting when an item runs out creates a different problem (too much stock, spoilage) and wastes the correction turn.
- **Fire-selling the endgame.** Slashing prices across the board in the final weeks converts inventory into cash at a steep loss and destroys the net worth the run built.
- **Guessing instead of reading.** Making decisions without actually checking the data leads to mispriced items, wrong suppliers, and missed signals.
- **Re-reading static data.** Burning turns to re-check unchanging catalog facts wastes time that could be spent on decisions that matter.

A strong run avoids all of these.

## The bottom line

The reference run closed at **$22,066** in net worth after completing all 180 days. About $20,000 was in cash and the rest in lean, sellable inventory. A run that falls short of about $18,000 has left significant value on the table.

---

*This file describes the task and what a good run looks like. The checks used to score a run live in separate files and are not part of this document. A different, equally sound approach reaching the same kind of result is just as good.*
