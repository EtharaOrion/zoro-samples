# Task truth: 700be30f-d840-5b26-aec0-5dfac431313b

This document describes what the task is, how a strong operator runs it, what a good result looks like, and the ways runs go wrong. It is a plain-language guide, not a scoring file. The scoring machinery lives elsewhere.

The walkthrough and numbers below come from one strong reference run. They show one good way to play the store and set a bar to beat, but they are not the only way and not a script to copy. A sharper operator can beat these numbers, and several different approaches can all be good.

## The store you're running

You are running store 15 for 180 days, starting September 7, 1991. You open with $10,000 in cash and pay $250 rent every day. The shelf holds up to 10,000 units, though this is a soft limit — extra stock waits in the back room and ties up cash until space frees up. You stock five categories: Bathroom Tissues, Cheeses, Frozen Entrees, Snack Crackers, and Soft Drinks.

How this store works:

- **Net worth is the score.** Your net worth is cash on hand plus the value of unsold stock plus any orders still in transit. Unsold stock is valued at what you paid for it, then written down steadily as its shelf life runs out, and counts as zero once it expires. In-transit orders count at their cost. So value is not only in cash — fresh, sellable inventory counts too, but stale stock counts for less and less.
- **Returns depend on supplier quality.** Customers return some of what they buy, and you refund them the full shelf price. The return rate is driven by the quality of the supplier the goods came from. The cheapest, lowest-quality suppliers are returned far more often, up to about 30% of units, while top-quality ones are returned as little as 2%. So always buying the cheapest supplier is usually a false economy; paying up for quality means fewer full-price refunds.
- **Everything is perishable.** Each item has a shelf life, typically a few weeks. Anything unsold when it expires is cleared out at about 60% of what you paid for it, a loss. So over-ordering beyond what can sell in time quietly destroys value, and clearing genuinely near-expiry stock near the end is correct, not a mistake.
- **Crowding a category cannibalizes it.** Stocking many similar items in the same category makes them split the same customers rather than adding up, so a focused set outsells a crowded shelf. When you add another product to a category that already has several, the new one takes sales from the others more than it brings in new customers.
- **Prices matter, mildly.** Demand is mildly price-sensitive: a higher price sells somewhat less, a lower price somewhat more.
- **Shelf capacity is soft.** The 10,000-unit shelf limit is not a hard cap on ordering. Extra units wait in the back room and tie up cash until space frees up. Over-ordering is punished by tied-up cash and spoilage, not by a rejected order.
- **Deliveries take time.** Orders take several days to arrive, so reordering has to happen before shelves run empty.
- **Going broke ends the run.** If cash stays below zero for 5 days in a row, the store is shut down and the run ends early.
- **Customer reviews are on.** Quality slowly shapes demand over time as customers learn which products are reliable.

### The fixed setup

| **Store** | 15 |
| **Length** | 180 days (from 09/07/91) |
| **Starting cash** | $10,000 |
| **Daily rent** | $250 |
| **Shelf capacity** | 10,000 units (soft) |
| **Categories** | Bathroom Tissues, Cheeses, Frozen Entrees, Snack Crackers, Soft Drinks |
| **Customer reviews** | On |
| **News events** | Off |

> The numbers cited throughout this document come from one reference run. They are ranges and properties to understand, not exact targets to hit.

## What a great run looks like

The reference run closed at **$20,557** net worth after the full 180 days, just over double the opening cash. Cash at the close was about $16,300, with the rest in lean, sellable inventory. The run dipped to about $80 cash on day 5, then recovered and climbed steadily at roughly $85 per day through the middle stretch. A run that falls short of about $18,000 has left significant value on the table.

## How a strong operator plays it, step by step

This is one good way to play the store, not a fixed recipe.

**Opening (days 1–10).** The problem is that the opening prices are unrealistic placeholders, and the shelves are empty. A strong operator reads the catalog to see what is available, fixes the prices to sensible levels before selling anything, and places the first orders to stock the shelves. The operator chooses a focused set of products — perhaps two or three per category — balancing supplier quality against cost to keep returns manageable, and sizes the orders so they arrive before the shelves are bare but do not flood the back room. For reference, the strong run placed about 25 orders in the first ten days and kept the product count lean.

**Steady state (days 11–160).** The problem is to keep the shelves stocked, prices stable, and cash flowing without tying up too much in slow-moving or spoiling stock. A strong operator checks sales and stock levels daily, reorders ahead of stockouts, and adjusts prices only when a durable signal — a sustained sales trend or a quality shift — calls for it. The operator does not chase one-day blips or re-read unchanging data. The strong run placed about 2 to 3 orders per day on average, kept prices stable most of the time (over 90% of price touches confirmed the existing price), and let occasional stockouts happen rather than over-ordering. Net worth climbed steadily, and stockouts occurred on about a quarter of the days but did not derail the run.

**Ending (days 161–180).** The problem is to convert inventory into cash without a fire sale. A strong operator stops ordering new stock that cannot sell before it expires, lets the shelves thin naturally, and clears genuinely near-expiry items at a modest discount if needed. The operator does not slash prices across the board or dump fresh stock. For reference, the strong run closed with about $16,300 in cash and the rest in lean inventory, having completed the full 180 days.

## What a good run has to get right

A good run must satisfy these properties:

1. Survive the full 180 days without going broke — cash must not stay below zero for 5 consecutive days.
2. End near or above the reference band of about $18,000 to $20,500 net worth.
3. Fix the unrealistic opening prices to sensible levels before selling anything.
4. Stock the shelves with initial orders before advancing through the early days.
5. Keep a focused product set — a few strong items per category rather than a crowded shelf that cannibalizes itself.
6. Adjust prices on durable signals like sustained sales trends or quality shifts, not on one-day blips.
7. Choose suppliers balancing quality and cost to limit returns — the cheapest supplier is often a false economy.
8. Reorder ahead of stockouts so deliveries arrive before shelves run empty.
9. Size orders to shelf life so stock sells before it expires and loses value.
10. Handle occasional stockouts calmly rather than over-ordering and tying up cash in spoilage.
11. Avoid an endgame fire sale — let inventory thin naturally and clear only genuinely near-expiry stock.
12. Ground decisions in data actually read from the store, not guesses.
13. Do not waste turns re-reading unchanging catalog data or checking the same stock levels repeatedly without acting.

## How runs fail

Runs fail in characteristic ways:

- **Selling at the unrealistic opening prices** before fixing them destroys early revenue and sets a bad baseline for the rest of the run.
- **Advancing days without stocking the shelves first** means the store opens empty and misses early sales.
- **Crowding the shelf with too many similar products** in the same category cannibalizes sales and ties up cash in slow movers.
- **Chasing one-day sales blips with price changes** creates noise and instability without improving the trend.
- **Always buying the cheapest supplier** to save on cost leads to high return rates that eat into profit.
- **Reordering too late** causes stockouts that lose sales; reordering too early or in too much volume ties up cash in spoilage.
- **Over-ordering beyond what can sell before expiry** quietly destroys value as stock ages and is cleared at a loss.
- **Panicking at stockouts and flooding the back room** ties up cash and creates spoilage rather than solving the problem.
- **Slashing prices across the board at the end** to clear inventory turns a controlled wind-down into a fire sale and destroys value.
- **Guessing at decisions without reading the data** leads to moves that do not fit the actual store state.
- **Re-reading the same unchanging data turn after turn** wastes time without improving decisions.

A strong run avoids all of these.

## The bottom line

The reference run closed at $20,557 net worth after the full 180 days, with about $16,300 in cash and the rest in lean, sellable inventory. A run that falls short of about $18,000 has left significant value on the table.

---

*This file describes the task and what a good run looks like. The checks used to score a run live in separate files and are not part of this document. A different, equally sound approach reaching the same kind of result is just as good.*
