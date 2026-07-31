# Task truth: 68505b1a-e67f-5ad3-b5ba-071989370769

This document is a plain-language guide to the task, what a strong run looks like, and the properties a good run must satisfy. The scoring machinery that evaluates runs lives in separate files and is not part of this document.

The walkthrough and numbers below come from one strong reference run. They show a bar to beat and one good way to play the store, but they are not the only way and not a script to copy. A sharper operator can beat these numbers, and several different sound approaches can all be good.

## The store you're running

You are running store 15 for 180 days starting September 7, 1991. You open with $50,000 in cash and pay $1,000 rent every day. The shelf can hold about 40,000 units, though this is a soft limit — extra stock waits in the back room and ties up cash until space frees up. You stock 20 categories: Bathroom Tissues, Beer, Bottled Juices, Canned Soup, Canned Tuna, Cereals, Cheeses, Cigarettes, Cookies, Crackers, Dish Detergent, Fabric Softeners, Front-end Candies, Frozen Entrees, Frozen Juices, Oatmeal, Paper Towels, Snack Crackers, Soft Drinks, and Toothpastes.

How this store works:

- **Net worth is the score.** Net worth equals cash on hand plus the value of unsold stock you are holding plus any orders still in transit. Unsold stock is valued at what you paid for it, then written down steadily as its shelf life runs out, and counts as zero once it expires. In-transit orders count at their cost. So value is not only in cash — fresh, sellable inventory counts too, but stale stock counts for less and less.
- **Everything is perishable.** Each item has a shelf life, typically a few weeks. Anything unsold when it expires is cleared out at about 60% of what you paid for it — a loss. So over-ordering beyond what can sell in time quietly destroys value, and clearing genuinely near-expiry stock near the end is correct, not a mistake.
- **Returns depend on supplier quality.** Customers return some of what they buy, and the store refunds them the full shelf price. The return rate is driven by the quality of the supplier the goods came from. The cheapest, lowest-quality suppliers are returned far more often, up to about 30% of units, than top-quality ones, as little as 2%. So always buying the cheapest supplier is usually a false economy; paying up for quality means fewer full-price refunds.
- **Crowding a category cannibalizes it.** Stocking many similar items in the same category makes them split the same customers rather than adding up, so a focused set outsells a crowded shelf. A handful of well-chosen items in each category will outperform a sprawling assortment.
- **Prices matter, mildly.** Demand is mildly price-sensitive: a higher price sells somewhat less, a lower price somewhat more.
- **Deliveries take time.** Orders take several days to arrive, so reordering has to happen before shelves run empty.
- **Going broke ends the run.** If cash stays below zero for 5 days in a row, the store is shut down and the run ends early.
- **Reviews and news are on.** Customer reviews slowly shape demand over time as quality builds or erodes reputation. News events can shift demand unpredictably.

### The fixed setup

| **Store**            | 15                                      |
|----------------------|-----------------------------------------|
| **Length**           | 180 days (starting 09/07/91)            |
| **Starting cash**    | $50,000                                 |
| **Daily rent**       | $1,000                                  |
| **Shelf capacity**   | 40,000 units (soft limit)               |
| **Categories**       | 20 (listed above)                       |
| **Customer reviews** | On                                      |
| **News events**      | On                                      |

> The numbers cited in this document come from one reference run and describe ranges and properties, not exact targets to hit.

## What a great run looks like

The reference run finished all 180 days with a terminal net worth of **$133,000**, about 2.7 times the opening cash. At the close, the operator held roughly $121,000 in cash and about $12,000 in lean, sellable inventory. Cash dipped sharply in the opening week as the operator stocked the shelves, recovered quickly, then climbed steadily through the horizon. A run that finishes below about $110,000 has fallen short.

## How a strong operator plays it, step by step

This is one good way to play the store, not a fixed recipe.

**Opening (days 1–10).** The problem is to stock the shelves without going broke and to fix the unrealistic opening prices before selling anything. A strong operator reads the catalog, identifies a focused set of items across all 20 categories — typically 3 to 5 items per category — and places opening orders choosing suppliers on a balance of quality and cost to limit returns. The operator sets realistic shelf prices before advancing the first day, because the opening prices are often wildly off and selling at those prices destroys value. Cash drops sharply as orders arrive and are paid for; the reference run bottomed at about $2,300 on day 7. The operator does not panic at this dip — it is the cost of stocking the shelves and recovers quickly as sales begin.

**Steady state (days 11–160).** The problem is to keep shelves stocked, prices stable, and cash growing without over-ordering or chasing noise. A strong operator settles into a daily rhythm: check for stockouts and place small reorders ahead of running empty, review sales and adjust prices only when a durable signal emerges, and avoid crowding categories with too many similar items. The reference run placed about 1,200 orders across the horizon, roughly 7 per day, and kept prices stable — over 90% of price touches confirmed the existing price rather than changing it. The operator sizes orders to shelf life so stock sells before it expires, chooses suppliers on quality to keep returns low, and handles occasional stockouts calmly rather than over-correcting. Net worth climbs steadily; the reference run grew at about $800 per day through this phase.

**Ending (days 161–180).** The problem is to finish with lean, sellable inventory and maximum cash without a fire-sale. A strong operator tapers ordering in the final weeks so stock runs down naturally as the horizon approaches, clears genuinely near-expiry items at a reasonable discount, and avoids the twin mistakes of ending with a warehouse full of unsold goods or slashing prices across the board in the final days. The reference run closed with about $12,000 in inventory — enough to keep selling through the end, not so much that value was left on the table.

## What a good run has to get right

A good run must satisfy these properties:

1. Survive the full 180-day horizon without going broke — cash must not stay below zero for 5 consecutive days.
2. End near or above the reference band, roughly $110,000 to $135,000 in terminal net worth.
3. Fix the unrealistic opening prices before selling anything — the opening prices are often wildly off and must be corrected immediately.
4. Stock the shelves before advancing through the opening days — orders must be placed and prices set before sales begin in earnest.
5. Keep a focused product set — a handful of well-chosen items in each category outperforms a crowded shelf that cannibalizes itself.
6. Price on durable signals, not one-day blips — most price reviews confirm the existing price; changes happen only when a clear, sustained pattern emerges.
7. Choose suppliers on a balance of quality and cost to limit returns — the cheapest supplier is usually a false economy because high return rates destroy value.
8. Reorder ahead of stockouts — deliveries take several days, so waiting until shelves are empty means lost sales.
9. Size orders to shelf life — stock must sell before it expires, or value is destroyed in clearance.
10. Handle stockouts calmly — occasional stockouts are normal; over-correcting with huge orders ties up cash and risks spoilage.
11. No endgame fire-sale — finish with lean, sellable inventory, not a warehouse full of unsold goods or across-the-board price slashing in the final days.
12. Ground decisions in data actually read — prices, orders, and supplier choices must reflect the catalog, sales, and stock levels the operator has examined.
13. Do not waste turns re-reading unchanging data — the catalog does not change; reading it once is enough.
14. Keep cash positive through the opening dip — the sharp drop in the first week as shelves are stocked is normal and recovers quickly; the operator must not panic and under-stock.

## How runs fail

Runs fail in characteristic ways:

- **Going broke in the opening week** — ordering too much too fast or setting prices too low drains cash below zero for 5 days and shuts the store down early.
- **Ending with a warehouse full of unsold stock** — over-ordering or failing to taper in the final weeks leaves value tied up in inventory that counts for less than cash.
- **Always buying the cheapest supplier** — ignoring quality means return rates of 20% to 30%, and refunding customers the full shelf price destroys value faster than the low cost saves it.
- **Crowding categories with too many items** — stocking a dozen similar items in one category makes them split the same customers, and total sales fall below what a focused set would achieve.
- **Chasing one-day noise with price changes** — changing prices every day in response to small blips creates instability and erodes margins without improving sales.
- **Waiting until stockouts happen to reorder** — deliveries take several days, so reacting to an empty shelf means lost sales for the entire lead time.
- **Ordering more than can sell before expiry** — stock that expires is cleared at about 60% of cost, a guaranteed loss.
- **Fire-sale pricing in the final days** — slashing prices across the board at the end converts sellable inventory into cash at a loss rather than finishing cleanly.
- **Ignoring the opening price problem** — selling at the unrealistic opening prices, which are often far too high or far too low, destroys value before the operator realizes the mistake.
- **Re-reading the catalog every day** — the catalog does not change; wasting turns on repeated reads leaves less time for the decisions that matter.

A strong run avoids all of these.

## The bottom line

The reference run finished all 180 days with a terminal net worth of **$133,000**, holding about $121,000 in cash and $12,000 in lean, sellable inventory. A run that finishes below about $110,000 has fallen short.

---

*This file describes the task and what a good run looks like. The checks used to score a run live in separate files and are not part of this document. A different, equally sound approach reaching the same kind of result is just as good.*
