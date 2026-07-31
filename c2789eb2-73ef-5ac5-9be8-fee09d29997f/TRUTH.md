# Task truth: c2789eb2-73ef-5ac5-9be8-fee09d29997f

This document describes what the task is, how the store works, what a strong run looks like, and the ways runs go wrong. It is a plain-language guide, not a scoring file. The scoring machinery lives elsewhere.

The walkthrough and numbers below come from one strong reference run that finished with a terminal net worth of **$28,770.52** after 180 days. That run is a bar to beat and one good way to play the store, but it is not the only way and not a script to copy. A sharper operator can beat those numbers, and several different sound approaches can all reach good results.

## The store you're running

You are running store 15 for 180 days starting September 7, 1991. You open with $5,000 in cash and pay $120 rent every day. The shelf can hold about 6,000 units, though that is a soft limit — extra stock waits in the back room and ties up cash until space opens up. You stock four categories: Cheeses, Frozen Entrees, Snack Crackers, and Soft Drinks.

**How this store works:**

- **Net worth is the score.** Net worth equals cash on hand plus the value of unsold stock you are holding plus any orders still in transit. Unsold stock is valued at what you paid for it, then written down steadily as its shelf life runs out, and counts as zero once it expires. In-transit orders count at their cost. So value is not only in cash — fresh, sellable inventory counts too, but stale stock counts for less and less.
- **Returns depend on supplier quality.** Customers return some of what they buy, and you refund them the full shelf price. The return rate is driven by the quality of the supplier the goods came from. The cheapest, lowest-quality suppliers see return rates as high as 30% of units sold, while top-quality suppliers see rates as low as 2%. So always buying the cheapest supplier is usually a false economy; paying up for quality means fewer full-price refunds.
- **Everything is perishable.** Each item has a shelf life, typically a few weeks. Anything unsold when it expires is cleared out at about 60% of what you paid for it — a loss. So over-ordering beyond what can sell in time quietly destroys value, and clearing genuinely near-expiry stock near the end is correct, not a mistake.
- **Crowding a category cannibalizes it.** Stocking many similar items in the same category makes them split the same customers rather than adding up, so a focused set outsells a crowded shelf. When you stock multiple products in one category, they compete for the same pool of demand. A lean, well-chosen lineup performs better than a sprawling one.
- **Prices matter, mildly.** Demand is mildly price-sensitive. A higher price sells somewhat less; a lower price sells somewhat more. Adjust prices based on what you learn about demand, but do not chase every small fluctuation.
- **Shelf capacity is soft.** The 6,000-unit shelf limit is not a hard cap on ordering. Extra units wait in the back room and tie up cash until space frees up. Over-ordering is punished by tied-up cash and spoilage, not by a rejected order.
- **Deliveries take time.** Orders take several days to arrive, so reordering has to happen before shelves run empty.
- **Going broke ends the run.** If cash stays below zero for 5 days in a row, the store is shut down and the run ends early.
- **Customer reviews are on.** Quality slowly shapes demand over time as customers learn which products are good.

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

> The numbers cited in this document come from one reference run and describe ranges and properties, not exact targets to hit.

## What a great run looks like

The reference run finished with a terminal net worth of **$28,770.52**, about 5.8 times the opening cash, after completing all 180 days. At the close, the operator held about $23,478 in cash and roughly $5,293 in sellable inventory and in-transit orders. The run dipped into the red briefly in the opening days, recovered quickly, and then climbed steadily through the horizon. A run that finishes below about $20,000 has fallen short.

## How a strong operator plays it, step by step

This is one good way to run the store, not a fixed recipe.

**Opening (days 1–10).** The problem is to fix the unrealistic opening prices, stock the shelves with a focused product set, and survive the opening cash crunch without going broke. A strong operator reads the catalog to understand what is available, picks a lean lineup of about 8 to 12 products spread across the four categories, chooses suppliers balancing cost and quality to limit returns, sets realistic prices based on cost and the category, and places opening orders sized to fill the shelves without over-ordering. Cash dips into the red briefly — the reference run bottomed at about negative $98 on day 3 — but recovers as sales begin. The operator does not panic and does not waste turns re-reading unchanging catalog data.

**Steady state (days 11–160).** The problem is to keep shelves stocked, manage prices and suppliers based on what you learn, and grow net worth steadily. A strong operator reorders ahead of stockouts, sizes orders to what can sell before expiry, adjusts prices based on durable demand signals rather than one-day blips, and switches suppliers when quality or cost improves. The reference run placed about 371 orders across the horizon, roughly two per day, and kept prices stable most of the time — about 90% of price touches confirmed the existing price rather than changing it. Stockouts happen occasionally — the reference run saw stockouts on about 41 days — but the operator handles them calmly by reordering and does not let them spiral. Net worth climbs at a steady pace, roughly $150 per day in the reference run's middle stretch.

**Ending (days 161–180).** The problem is to finish with cash and sellable inventory, not a pile of expiring stock. A strong operator continues normal operations, reorders conservatively as the horizon approaches, and clears genuinely near-expiry stock if needed. The reference run finished with about $23,478 in cash and roughly $5,293 in inventory and in-transit orders, a lean but still-selling position. There is no endgame fire sale of healthy stock.

## What a good run has to get right

A good run must satisfy these properties:

1. Survive the full 180-day horizon without going broke (cash below zero for 5 consecutive days).
2. End with a net worth near or above the reference band of about $20,000 to $29,000.
3. Fix the unrealistic opening prices before selling, setting them based on cost and category rather than leaving them at arbitrary defaults.
4. Stock the shelves with a focused product set before advancing through the opening days, rather than running an empty store.
5. Keep a lean, focused product lineup that avoids crowding any one category with too many similar items that split the same demand.
6. Price products on durable demand signals learned over multiple days, not on one-day blips or arbitrary guesses.
7. Choose suppliers balancing cost and quality to limit return rates, rather than always buying the cheapest and eating the refunds.
8. Reorder ahead of stockouts so deliveries arrive before shelves run empty, accounting for the multi-day lead time.
9. Size orders to what can sell before expiry, rather than over-ordering and letting stock spoil or tying up cash in the back room.
10. Handle occasional stockouts calmly by reordering, rather than panicking or abandoning products that sell well.
11. Finish with a lean but still-selling inventory position, not a pile of expiring stock and not an endgame fire sale of healthy products.
12. Ground pricing, ordering, and supplier decisions in data actually read from the tools, not guesses.
13. Avoid wasting turns re-reading unchanging catalog data or checking the same static information repeatedly.

## How runs fail

Runs fail in characteristic ways:

- **Leaving opening prices at unrealistic defaults** and selling at arbitrary prices unrelated to cost destroys margin and confuses demand signals.
- **Running an empty or nearly-empty store in the opening days** because the operator never stocked shelves wastes the early horizon and leaves money on the table.
- **Crowding one category with too many similar products** splits demand and underperforms a focused lineup.
- **Chasing one-day demand blips with price changes** creates noise and instability rather than learning what prices work.
- **Always buying the cheapest supplier** to save pennies on cost eats dollars in full-price refunds when return rates hit 30%.
- **Reordering only after stockouts happen** means shelves sit empty for days waiting for deliveries, losing sales.
- **Over-ordering beyond what can sell before expiry** ties up cash in the back room and destroys value when stock spoils.
- **Panicking during stockouts** and abandoning good products or making wild changes disrupts the steady climb.
- **Running the store into the ground with 5 consecutive days of negative cash** ends the run early and forfeits the remaining horizon.
- **Finishing with a pile of expiring stock** or **fire-selling healthy inventory in the endgame** destroys value that should have been preserved.
- **Making decisions on guesses rather than data actually read** leads to poor choices that compound over time.
- **Wasting turns re-reading unchanging catalog data** burns time that should be spent managing the store.

A strong run avoids all of these.

## The bottom line

The reference run finished with a terminal net worth of **$28,770.52** after completing all 180 days, holding about $23,478 in cash and roughly $5,293 in lean, sellable inventory and in-transit orders. A run finishing below about $20,000 has fallen short.

---

*This document describes the task and what a good run looks like. The checks used to score a run live in separate files and are not part of this document. A different, equally sound approach reaching the same kind of result is just as good.*
