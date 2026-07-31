# Task truth: 657e8b9d-a8a5-58c4-94d2-b0f0636027dc

This document is a plain-language guide to the task, what a strong run looks like, and the properties a good run must satisfy. The scoring machinery lives in separate files and is not part of this document.

The walkthrough and numbers below come from one strong reference run. They show a bar to beat and one good way to play, not the only way and not a script to copy. A sharper operator can beat these numbers, and several different approaches can all be good.

## The store you're running

You are running store 15 for 180 days starting September 7, 1991. You open with $5,000 in cash and pay $120 in rent every day. The shelf holds about 6,000 units, though this is a soft limit — extra stock waits in the back room and ties up cash until space frees up. You sell four categories: Cheeses, Frozen Entrees, Snack Crackers, and Soft Drinks.

**How this store works:**

- **Net worth is the score.** Net worth equals cash on hand plus the value of unsold stock you are holding plus any orders still in transit. Unsold stock is valued at what you paid for it, then written down steadily as its shelf life runs out, and counts as zero once it expires. In-transit orders count at their cost. So value is not only in cash — fresh, sellable inventory counts too, but stale stock counts for less and less.
- **Returns depend on supplier quality.** Customers return some of what they buy, and you refund them the full shelf price. The return rate is driven by the quality of the supplier the goods came from. The cheapest, lowest-quality suppliers are returned far more often (up to about 30% of units) than top-quality ones (as little as 2%). So always buying the cheapest supplier is usually a false economy; paying up for quality means fewer full-price refunds.
- **Everything is perishable.** Each item has a shelf life, typically a few weeks. Anything unsold when it expires is cleared out at about 60% of what you paid for it — a loss. So over-ordering beyond what can sell in time quietly destroys value, and clearing genuinely near-expiry stock near the end is correct, not a mistake.
- **Crowding a category cannibalizes it.** Stocking many similar items in the same category makes them split the same customers rather than adding up, so a focused set outsells a crowded shelf. When you raise the price on one item, some of its demand shifts to other active items in the same category, and vice versa. A lean product line in each category performs better than a crowded one.
- **Prices matter, mildly.** Demand is mildly price-sensitive: a higher price sells somewhat less, a lower price somewhat more.
- **Shelf capacity is soft.** The shelf limit is not a hard cap on ordering. Extra units wait in the back room and tie up cash until space frees up. Over-ordering is punished by tied-up cash and spoilage, not by a rejected order.
- **Deliveries take time.** Orders take several days to arrive, so reordering has to happen before shelves run empty.
- **Going broke ends the run.** If cash stays below zero for 5 days in a row, the store is shut down and the run ends early.
- **Customer reviews are on.** Quality slowly shapes demand over time as customers learn which products are reliable.

### The fixed setup

| **Store**            | 15                                      |
|----------------------|-----------------------------------------|
| **Length**           | 180 days (starting 09/07/91)            |
| **Starting cash**    | $5,000                                  |
| **Daily rent**       | $120                                    |
| **Shelf capacity**   | 6,000 units (soft limit)                |
| **Categories**       | Cheeses, Frozen Entrees, Snack Crackers, Soft Drinks |
| **Customer reviews** | On                                      |
| **News events**      | Off                                     |

> The numbers cited throughout this document come from one reference run and describe ranges and properties, not exact targets to hit.

## What a great run looks like

The reference run finished all 180 days with a terminal net worth of **$22,743**, about 4.5 times the opening cash. Cash dipped briefly below zero in the first week, then recovered and climbed steadily through the rest of the run. At the close, the store held about $19,100 in cash and $3,600 in fresh, sellable inventory. A run that falls short of about $18,000 in terminal net worth has left significant value on the table.

## How a strong operator plays it, step by step

This is one good way to run the store, not a fixed recipe.

**Opening (days 1–7): Fix prices, stock shelves, survive the cash dip.** The store opens with unrealistic default prices on many items. A strong operator reads the catalog, identifies the items with the best combination of supplier quality and cost, and sets sensible shelf prices before selling anything. Then they place opening orders to stock the shelves with a focused product set — perhaps 8 to 12 items across the four categories, not a crowded shelf. These orders arrive over the next few days and tie up cash, so the store dips into the red briefly (the reference hit about negative $100 on day 4). This is normal and not a crisis. The operator keeps the dip shallow and short, and cash recovers as sales begin.

**Steady state (days 8–160): Run the daily loop, grow net worth.** Each day, the operator checks what sold, what is running low, and what needs reordering. They place about two orders per day on average, sizing each to what can sell before it expires and choosing suppliers that balance cost and quality to limit returns. They adjust prices occasionally when demand or cost signals shift, but most days they leave prices alone — in the reference run, about 90% of price touches kept the existing price, meaning the operator confirmed the price was still right rather than changing it constantly. Stockouts happen now and then (the reference had stockouts on about 34 days), but a strong operator handles them calmly by reordering promptly, not by panic-buying or abandoning the item. Net worth climbs steadily through this phase, adding roughly $120 per day in the reference run.

**Ending (days 161–180): Wind down orders, sell through inventory, close lean.** As the horizon approaches, the operator stops ordering items that will not sell in time and lets the shelves thin out naturally. They do not fire-sale everything at the end — genuinely near-expiry stock is cleared at a modest discount, but fresh inventory is sold at normal prices or held as value. The reference closed with about $3,600 in fresh stock still on hand, not an empty store. This phase is about converting inventory to cash in an orderly way, not about zeroing out the shelves.

## What a good run has to get right

A good run must satisfy these properties:

1. Survive the full 180 days without going broke (cash below zero for 5 consecutive days).
2. End with a terminal net worth near or above the reference range of about $18,000 to $23,000.
3. Fix the unrealistic opening prices before selling, so the store does not give away inventory or scare off customers.
4. Stock the shelves with opening orders before advancing through the early days, so there is something to sell.
5. Keep a focused product set in each category — a lean shelf outsells a crowded one because similar items split the same customers.
6. Price on durable signals, not one-day blips — most price touches should confirm the existing price is still right, not chase noise.
7. Choose suppliers on the combination of quality and cost to limit returns — the cheapest supplier is often a false economy because of high return rates.
8. Reorder ahead of stockouts, since deliveries take several days — occasional stockouts are normal, but chronic empty shelves waste sales.
9. Size orders to shelf life, so inventory sells before it expires — over-ordering beyond what can move in time quietly destroys value through spoilage.
10. Handle stockouts calmly by reordering promptly, not by abandoning the item or panic-buying.
11. Wind down orders as the horizon approaches, but do not fire-sale everything — fresh inventory at the close is value, not a mistake.
12. Ground decisions in data actually read from the tools — prices, costs, sales, and stock levels must come from the current state, not guesses.
13. Do not waste turns re-reading unchanging data like the catalog or the same stock report multiple times in one day.
14. Keep the opening cash dip shallow and short — a brief dip into the red is normal as opening orders arrive, but it must recover quickly.

## How runs fail

A run fails when the operator makes one or more of these mistakes:

- **Sells at the unrealistic opening prices** — gives away inventory at a loss or scares off customers with absurd markups, destroying value from day one.
- **Stocks a crowded shelf** — tries to sell 20 or 30 items across four categories, so similar products split the same customers and the whole set underperforms.
- **Chases the cheapest supplier every time** — ignores quality and suffers high return rates that eat into profit through full-price refunds.
- **Over-orders beyond shelf life** — buys more than can sell before expiry, so spoilage quietly destroys value even as sales look fine.
- **Lets the opening cash dip spiral** — places too many opening orders at once or sizes them too large, so cash stays negative for 5 days and the run ends early.
- **Abandons items after one stockout** — treats a stockout as a permanent failure instead of reordering promptly, so the product set shrinks and sales fall.
- **Reprices constantly on noise** — changes prices every day chasing one-day blips, so the shelf is never stable and customers lose trust.
- **Fire-sales everything at the end** — clears all inventory at deep discounts in the final week, converting fresh stock to cash at a loss instead of holding it as value.
- **Guesses instead of reading** — sets prices or sizes orders without checking current costs, sales, or stock levels, so decisions drift away from reality.
- **Wastes turns on redundant reads** — re-reads the catalog or the same stock report multiple times in one day, burning time that could be spent on decisions.

A strong run avoids all of these.

## The bottom line

The reference run closed at **$22,743** in net worth after 180 days, with about $19,100 in cash and $3,600 in fresh, sellable inventory. A run that falls short of about $18,000 has left significant value on the table.

---

*This file describes the task and what a good run looks like. The checks used to score a run live in separate files and are not part of this document. A different, equally sound approach reaching the same kind of result is just as good.*
