# Task truth: f2200047-d5b4-58fe-b9d0-6367297ecd7a

This document describes what the task is, how a strong operator runs the store, what a good result looks like, and the ways runs fail. The scoring machinery that evaluates a run lives in separate files and is not part of this guide.

The walkthrough and numbers below come from one strong reference run. They show one good way to play the task and set a bar to beat, but they are not the only way and not a script to copy. A sharper operator can beat these numbers, and several different approaches can all be sound.

## The store you're running

You are running store 15 for 180 days, starting September 7, 1991. You open with $10,000 in cash and pay $250 rent every day. The shelf can hold up to 10,000 units, though this is a soft limit — extra stock waits in the back room and ties up cash until space frees up. You stock five categories: Bathroom Tissues, Cheeses, Frozen Entrees, Snack Crackers, and Soft Drinks.

**How this store works:**

- **Net worth is the score.** Net worth equals cash on hand plus the value of unsold stock you are holding plus any orders still in transit. Unsold stock is valued at what you paid for it, then written down steadily as its shelf life runs out, and counts as zero once it expires. In-transit orders count at their cost. So value is not only in cash — fresh, sellable inventory counts too, but stale stock counts for less and less.
- **Returns depend on supplier quality.** Customers return some of what they buy, and you refund them the full shelf price. The return rate is driven by the quality of the supplier the goods came from. The cheapest, lowest-quality suppliers are returned far more often (up to about 30% of units) than top-quality ones (as little as 2%). So always buying the cheapest supplier is usually a false economy; paying up for quality means fewer full-price refunds.
- **Everything is perishable.** Each item has a shelf life, typically a few weeks. Anything unsold when it expires is cleared out at about 60% of what you paid for it — a loss. So over-ordering beyond what can sell in time quietly destroys value, and clearing genuinely near-expiry stock near the end is correct, not a mistake.
- **Crowding a category cannibalizes it.** Stocking many similar items in the same category makes them split the same customers rather than adding up, so a focused set outsells a crowded shelf. When you add another product to a category that already has several, the new one takes sales from the existing ones more than it brings in new customers.
- **Prices matter, mildly.** Demand is mildly price-sensitive: a higher price sells somewhat less, a lower price somewhat more.
- **Shelf capacity is soft.** The shelf limit is not a hard cap on ordering. Extra units wait in the back room and tie up cash until space frees up. Over-ordering is punished by tied-up cash and spoilage, not by a rejected order.
- **Deliveries take time.** Orders take several days to arrive, so reordering has to happen before shelves run empty.
- **Going broke ends the run.** If cash stays below zero for five days in a row, the store is shut down and the run ends early.
- **Customer reviews are on.** Quality slowly shapes demand over time as customers learn which products are reliable.

### The fixed setup

| **Store**            | 15                                      |
|----------------------|-----------------------------------------|
| **Length**           | 180 days (starting 09/07/91)            |
| **Starting cash**    | $10,000                                 |
| **Daily rent**       | $250                                    |
| **Shelf capacity**   | 10,000 units (soft limit)               |
| **Categories**       | Bathroom Tissues, Cheeses, Frozen Entrees, Snack Crackers, Soft Drinks |
| **Customer reviews** | On                                      |
| **News events**      | Off                                     |

> The numbers cited throughout this document come from one reference run and describe ranges and properties, not exact targets to hit.

## What a great run looks like

The reference run finished all 180 days with a terminal net worth of **$24,577.95**, about 2.5 times the opening cash. Cash at the close was $18,081.85, with the rest in lean, sellable inventory. The run dipped briefly into the red in the first week, recovered by day 10, and climbed steadily from there at about $106 per day through the middle stretch. A run that falls short of $20,000 has left significant value on the table.

## How a strong operator plays it, step by step

This is one good way to run the store, not a fixed recipe.

**Opening (days 1–10).** The problem is to fix the unrealistic opening prices, stock the shelves with a focused product set, and survive the cash crunch. A strong operator reads the catalog, picks about 15–20 products spread across the five categories (three to five per category, not more), chooses suppliers balancing cost and quality to limit returns, sets realistic shelf prices based on cost and competitor pricing, and places opening orders sized to fill the shelves without over-ordering. The first few days see negative cash as orders arrive and rent is paid, but sales begin immediately and cash recovers by day 10. For reference, the reference run dipped to about negative $50 on day 5 and was back in the black by day 10.

**Steady daily loop (days 11–160).** The problem is to keep shelves stocked, prices stable, and inventory fresh while growing net worth. A strong operator checks stock levels each day, reorders items that are running low (placing orders a few days before a stockout, since deliveries take time), and sizes each order to what can sell before it expires. Prices are touched only when a durable signal appears — a sustained change in competitor pricing or a clear shift in demand — not in response to one-day blips. The product set stays focused; adding more items to an already-stocked category cannibalizes sales rather than adding them. Occasional stockouts happen (the reference run had stockouts on about 43 days) and are handled calmly by reordering, not by panic over-ordering or abandoning the product. The reference run placed about 444 orders across the full 180 days, roughly 2.5 per day, and kept existing prices on about 93% of price touches, changing them only when the situation called for it. Net worth climbed steadily at about $106 per day through this stretch.

**Ending (days 161–180).** The problem is to finish with lean, sellable inventory and no fire-sale. A strong operator tapers ordering in the final weeks to avoid stock that will expire after the close, but does not stop ordering entirely or slash prices to clear the shelves. The goal is to end with some fresh inventory still on hand (it counts toward net worth) and cash from the final days of sales. The reference run closed with about $6,500 in inventory value and $18,000 in cash.

## What a good run has to get right

A good run must satisfy these properties, in its own way:

1. Survive the full 180 days without going broke (cash below zero for five consecutive days).
2. End with a net worth near or above the reference band of about $24,000 to $25,000.
3. Fix the unrealistic opening prices before selling begins, setting them based on cost and competitor pricing.
4. Stock the shelves with a focused product set before advancing through the opening days.
5. Keep the product set focused — about three to five items per category, not a crowded shelf that cannibalizes itself.
6. Price on durable signals, not one-day blips; most price touches confirm the existing price is still right.
7. Choose suppliers balancing cost and quality to limit returns; the cheapest supplier is rarely the best value.
8. Reorder ahead of stockouts, since deliveries take several days; occasional stockouts are normal and handled calmly.
9. Size orders to shelf life so stock sells before it expires; over-ordering ties up cash and leads to spoilage losses.
10. Handle stockouts calmly by reordering, not by abandoning the product or panic over-ordering.
11. Finish with lean, sellable inventory, not a fire-sale or empty shelves; inventory counts toward net worth.
12. Ground decisions in data actually read from the tools, not guesses.
13. Do not waste turns re-reading unchanging catalog data or repeatedly checking the same stock level within a single day.
14. Taper ordering in the final weeks to avoid stock that will expire after the close, but do not stop ordering entirely.

## How runs fail

Runs fail in characteristic ways:

- **Ignoring supplier quality** — always buying the cheapest supplier leads to return rates near 30%, destroying profit through full-price refunds.
- **Crowding categories** — stocking ten items in one category makes them split the same customers, so total sales are lower than a focused set of three to five would achieve.
- **Chasing one-day price blips** — changing prices in response to a single day's competitor move or sales number creates instability and wastes effort; prices should change only on durable signals.
- **Over-ordering** — placing orders larger than what can sell before expiry ties up cash in stock that will spoil, quietly destroying value.
- **Panic over stockouts** — treating a stockout as a crisis and over-ordering or abandoning the product, rather than calmly reordering to normal levels.
- **Endgame fire-sale** — slashing prices or stopping orders entirely in the final weeks, leaving the shelves empty and forfeiting the inventory value that counts toward net worth.
- **Ignoring shelf life** — ordering without checking how long stock will last leads to expired goods cleared at 60% of cost, a steady loss.
- **Going broke early** — running out of cash in the opening days and staying negative for five days in a row, ending the run before it can recover.
- **Guessing instead of reading** — making decisions without actually reading stock levels, competitor prices, or sales data leads to mispriced goods, stockouts, and wasted cash.

A strong run avoids all of these.

## The bottom line

The reference run finished all 180 days with a terminal net worth of $24,577.95, about 2.5 times the opening cash. Cash at the close was $18,081.85, with the rest in lean, sellable inventory. A run that falls short of $20,000 has left significant value on the table.

---

*This document describes the task and what a good run looks like. The checks used to score a run live in separate files and are not part of this document. A different, equally sound approach reaching the same kind of result is just as good.*
