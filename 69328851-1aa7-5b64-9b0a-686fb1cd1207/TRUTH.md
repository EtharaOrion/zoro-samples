# Task truth: 69328851-1aa7-5b64-9b0a-686fb1cd1207

This document describes the task, what a strong run looks like, and the properties a good run must satisfy. The scoring machinery lives in separate files and is not part of this document.

The walkthrough and numbers below come from one strong reference run. They show a bar to beat and one good way to play, not the only way and not a script to copy. A sharper operator can beat these numbers, and several different approaches can all be good.

## The store you're running

You are running store 15 for 180 days starting September 7, 1991. You open with $5000 in cash and pay $120 in rent every day. The shelf can comfortably hold about 6000 units, though extra stock waits in the back room and ties up cash until space frees up. You stock four categories: Cheeses, Frozen Entrees, Snack Crackers, and Soft Drinks.

How this store works:

- **Net worth is the score.** Net worth equals cash on hand plus the value of unsold stock you are holding plus any orders still in transit. Unsold stock is valued at what you paid for it, then written down steadily as its shelf life runs out, and counts as zero once it expires. In-transit orders count at their cost. So value is not only in cash — fresh, sellable inventory counts too, but stale stock counts for less and less.
- **Returns depend on supplier quality.** Customers return some of what they buy, and the store refunds them the full shelf price. The return rate is driven by the quality of the supplier the goods came from. The cheapest, lowest-quality suppliers are returned far more often, up to about 30% of units, than top-quality ones, as little as 2%. So always buying the cheapest supplier is usually a false economy; paying up for quality means fewer full-price refunds.
- **Everything is perishable.** Each item has a shelf life, typically a few weeks. Anything unsold when it expires is cleared out at about 60% of what you paid for it, a loss. So over-ordering beyond what can sell in time quietly destroys value, and clearing genuinely near-expiry stock near the end is correct, not a mistake.
- **Crowding a category cannibalizes it.** Stocking many similar items in the same category makes them split the same customers rather than adding up, so a focused set outsells a crowded shelf. A run that tries to stock every available product will see each one sell less than it would alone.
- **Prices matter, mildly.** Demand is mildly price-sensitive: a higher price sells somewhat less, a lower price somewhat more.
- **Shelf capacity is soft.** The shelf limit is not a hard cap on ordering. Extra units wait in the back room and tie up cash until space frees up. Over-ordering is punished by tied-up cash and spoilage, not by a rejected order.
- **Deliveries take time.** Orders take several days to arrive, so reordering has to happen before shelves run empty.
- **Going broke ends the run.** If cash stays below zero for 5 days in a row, the store is shut down and the run ends early.
- **Customer reviews are on.** Quality slowly shapes demand over time as customers learn which products are reliable.

### The fixed setup

| **Store**            | 15                                      |
|----------------------|-----------------------------------------|
| **Length**           | 180 days (starting 09/07/91)            |
| **Starting cash**    | $5000                                   |
| **Daily rent**       | $120                                    |
| **Shelf capacity**   | 6000 units (soft)                       |
| **Categories**       | Cheeses, Frozen Entrees, Snack Crackers, Soft Drinks |
| **Customer reviews** | On                                      |
| **News events**      | Off                                     |

> The numbers cited throughout this document come from one reference run and describe ranges and properties, not exact targets to hit.

## What a great run looks like

The reference run closed at **$27,410** in net worth, about 5.5 times the opening cash, after completing all 180 days. At the close, the store held about $24,600 in cash and roughly $2,800 in fresh, sellable inventory. The net worth dipped briefly in the opening days as the first orders arrived and tied up cash, then recovered and climbed steadily through the horizon. A run that falls short of about $22,000 has left significant value on the table.

## How a strong operator plays it, step by step

This is one good way to run the store, not a fixed recipe.

**Opening (days 1–10).** The problem is to fix the unrealistic opening prices, stock the shelves with a focused product set, and survive the cash crunch as the first orders arrive. A strong operator reads the catalog to see what is available, picks a lean set of about 10–15 products spread across the four categories, chooses suppliers balancing cost and quality to limit returns, sets realistic shelf prices that will move stock, and places opening orders sized to fill the shelves without tying up too much cash. The first orders arrive over several days and net worth dips as cash converts to inventory, but sales begin immediately and the store recovers. For reference, the opening orders in the strong run totaled about 3,000–4,000 units and net worth bottomed near break-even on day 3 before climbing back.

**Steady state (days 11–160).** The problem is to keep shelves stocked, reorder ahead of stockouts, and grow net worth steadily without over-ordering or letting stock spoil. A strong operator checks inventory daily, places small reorders when stock runs low (typically one to two orders per day, for reference), adjusts prices only when demand or cost signals change meaningfully (not on one-day blips), and keeps the product set focused to avoid cannibalizing sales within each category. Orders are sized to what can sell before expiry, and suppliers are chosen to balance cost and return rates. The store runs lean but never runs out for long. For reference, the strong run saw about 35 days with at least one stockout, kept prices stable most of the time (over 90% of price touches confirmed the existing price), and grew net worth at about $150 per day through the middle of the horizon.

**Ending (days 161–180).** The problem is to wind down inventory without a fire sale and finish with cash in hand and a small amount of fresh stock. A strong operator stops placing large orders, lets inventory run down naturally through sales, and clears any genuinely near-expiry stock at a modest discount near the very end. The goal is to finish lean but still selling, not to dump everything at a loss. For reference, the strong run closed with about $2,800 in fresh inventory, not zero.

## What a good run has to get right

A good run must satisfy these properties:

1. Survive the full 180-day horizon without going broke (cash below zero for 5 consecutive days).
2. End with net worth near or above the reference band of about $22,000, ideally closer to $27,000 or better.
3. Fix the unrealistic opening prices before selling, setting shelf prices that will actually move stock.
4. Stock the shelves with a focused product set before advancing through the opening days, not leaving them empty.
5. Keep the product set lean and focused within each category to avoid cannibalizing sales across similar items.
6. Adjust prices on durable signals like cost changes or sustained demand shifts, not on one-day blips or noise.
7. Choose suppliers balancing cost and quality to limit return rates, not always picking the cheapest option.
8. Reorder ahead of stockouts so deliveries arrive before shelves run empty, accounting for the several-day lead time.
9. Size orders to what can sell before expiry, not over-ordering and letting stock spoil or tying up cash in the back room.
10. Handle occasional stockouts calmly as a normal part of running lean, not panicking or over-correcting.
11. Wind down inventory naturally at the end without a fire sale, finishing lean but still selling with some fresh stock on hand.
12. Ground pricing and ordering decisions in data actually read from the store, not guessing or using stale information.
13. Avoid wasting turns re-reading unchanging catalog data or repeatedly confirming the same prices without reason.

## How runs fail

- **Over-ordering beyond shelf life.** The operator orders more than can sell before expiry, and spoilage quietly destroys value as stock is cleared at 60% of cost.
- **Always buying the cheapest supplier.** The operator chases low cost without regard to quality, and return rates spike to 30%, refunding customers the full shelf price and destroying margin.
- **Crowding the shelf with too many similar products.** The operator stocks every available item in a category, and they cannibalize each other, each selling far less than a focused set would.
- **Chasing one-day price signals.** The operator adjusts prices constantly on noise, confusing customers and missing the durable trends that matter.
- **Ignoring stockouts until shelves are empty.** The operator does not reorder ahead of the delivery lead time, and the store runs out of stock for days, losing sales.
- **Fire-sale ending.** The operator panics near the end and dumps all inventory at deep discounts, converting sellable stock into cash at a loss.
- **Leaving shelves empty at the open.** The operator does not place opening orders promptly, and the store sits idle for days with nothing to sell.
- **Going broke in the opening crunch.** The operator over-orders at the start, cash stays negative for 5 days, and the run ends early.
- **Re-reading unchanging data.** The operator wastes turns repeatedly reading the catalog or confirming prices that have not changed, slowing progress without gaining information.

A strong run avoids all of these.

## The bottom line

The reference run closed at **$27,410** in net worth after completing all 180 days, holding about $24,600 in cash and roughly $2,800 in fresh, sellable inventory. A run that falls short of about $22,000 has left significant value on the table.

---

*This document describes the task and what a good run looks like. The checks used to score a run live in separate files and are not part of this document. A different, equally sound approach reaching the same kind of result is just as good.*
