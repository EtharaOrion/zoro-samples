# Task truth: e8fb4ba2-acf4-5169-a4cb-ab8789eb074c

This document is a plain-language guide to the task, what a strong run looks like, and the properties a good run must satisfy. The scoring machinery lives in separate files and is not part of this document.

The walkthrough and numbers below come from one strong reference run. They show a bar to beat and one good way to play the store, not the only way and not a script to copy. A sharper operator can beat these numbers, and several different approaches can all be good.

## The store you're running

You are running store 15 for 180 days starting September 7, 1991. You open with $50,000 in cash and pay $1,000 rent every day. The shelf can comfortably hold about 40,000 units, though you can order more — extra stock waits in the back room and ties up cash until space frees up. You stock twenty categories: Bathroom Tissues, Beer, Bottled Juices, Canned Soup, Canned Tuna, Cereals, Cheeses, Cigarettes, Cookies, Crackers, Dish Detergent, Fabric Softeners, Front-end Candies, Frozen Entrees, Frozen Juices, Oatmeal, Paper Towels, Snack Crackers, Soft Drinks, and Toothpastes.

How this store works:

- **Net worth is the score.** Net worth equals cash on hand plus the value of unsold stock you are holding plus any orders still in transit. Unsold stock is valued at what you paid for it, then written down steadily as its shelf life runs out, and counts as zero once it expires. In-transit orders count at their cost. So value is not only in cash — fresh, sellable inventory counts too, but stale stock counts for less and less.
- **Everything is perishable.** Each item has a shelf life, typically a few weeks. Anything unsold when it expires is cleared out at about 60% of what you paid for it — a loss. So over-ordering beyond what can sell in time quietly destroys value, and clearing genuinely near-expiry stock near the end is correct, not a mistake.
- **Returns depend on supplier quality.** Customers return some of what they buy, and the store refunds them the full shelf price. The return rate is driven by the quality of the supplier the goods came from — the cheapest, lowest-quality suppliers are returned far more often, up to about 30% of units, than top-quality ones, as little as 2%. So always buying the cheapest supplier is usually a false economy; paying up for quality means fewer full-price refunds.
- **Crowding a category cannibalizes it.** Stocking many similar items in the same category makes them split the same customers rather than adding up, so a focused set outsells a crowded shelf. When you raise the price on one item, some of its demand shifts to other active items in the same category, and vice versa. A lean product set avoids this splitting.
- **Prices matter, mildly.** Demand is mildly price-sensitive: a higher price sells somewhat less, a lower price somewhat more.
- **Deliveries take time.** Orders take several days to arrive, so reordering has to happen before shelves run empty.
- **Reviews and news are on.** Customer reviews are enabled, so quality slowly shapes demand over time. News events are also enabled and can shift demand unpredictably.
- **Going broke ends the run.** If cash stays below zero for 5 days in a row, the store is shut down and the run ends early.

### The fixed setup

| **Store**            | 15                                      |
|----------------------|-----------------------------------------|
| **Length**           | 180 days (starting 09/07/91)            |
| **Starting cash**    | $50,000                                 |
| **Daily rent**       | $1,000                                  |
| **Shelf capacity**   | ~40,000 units (soft limit)              |
| **Categories**       | 20 (see list above)                     |
| **Customer reviews** | On                                      |
| **News events**      | On                                      |

> The numbers cited in this document come from one reference run and are ranges or properties to aim for, not exact targets to hit.

## What a great run looks like

The reference run closed at **$102,220** in net worth, just over double the opening cash, after completing all 180 days. Terminal cash was about $85,000, with the rest in lean, sellable inventory. The run dipped sharply in the first week as opening orders consumed cash, recovered through the second and third weeks, then climbed steadily through the rest of the horizon. A run that falls short of about $90,000 in terminal net worth has left significant value on the table.

## How a strong operator plays it, step by step

This is one good way to play the store, not a fixed recipe.

**Opening (days 1–10).** The problem is to fix the unrealistic opening prices, stock the shelves with a focused product set, and survive the cash crunch as opening orders arrive and consume funds. A strong operator reads the opening catalog, identifies the obviously mispriced items — those priced far below cost or far above what the market will bear — and corrects them before selling anything. Then they choose one or two strong items per category, favoring suppliers with good quality-to-cost ratios to limit returns, and place opening orders sized to fill the shelf without tying up too much cash in any one category. They advance time cautiously, checking cash daily, because the opening orders hit all at once and can drive cash very low. The reference run bottomed at about $850 on day 7, then recovered as sales began. The operator does not panic at the dip — it is expected — but watches to ensure cash does not stay negative for five consecutive days.

**Steady state (days 11–160).** The problem is to keep shelves stocked, prices stable on durable signals, and net worth climbing without over-ordering or letting stockouts linger. A strong operator settles into a daily rhythm: check for stockouts and reorder ahead of them, adjusting order sizes to what actually sells and to shelf life; review prices occasionally but change them only when demand or cost shifts durably, not on one-day blips; read reviews and news when they appear to catch quality problems or demand shifts early; and keep the product set focused, resisting the temptation to crowd categories with too many similar items. The reference run placed about 1,200 orders across the full horizon, roughly seven per day, and confirmed most existing prices without change — about 90% of price touches kept the price as it was, a sign of stable pricing grounded in real signals. Stockouts happened on about 77 days, handled calmly by reordering rather than by fire-sale substitutions. Net worth climbed at roughly $600 per day through this phase, compounding the opening cash into a growing cushion.

**Ending (days 161–180).** The problem is to close out cleanly without a fire-sale or a pile of unsold stock. A strong operator tapers ordering in the final three weeks, letting inventory run down naturally as items sell or expire, and clears genuinely near-expiry stock at a modest discount if needed. They do not slash prices across the board or stop ordering entirely — both destroy value. The reference run closed with about $85,000 in cash and the rest in lean inventory, a clean finish.

## What a good run has to get right

A good run must satisfy these properties:

1. Survive the full 180-day horizon without going broke — cash must not stay below zero for 5 consecutive days.
2. End near or above the reference band of about $90,000 to $105,000 in net worth, showing the operator compounded the opening cash effectively.
3. Fix the unrealistic opening prices before selling — items priced below cost or absurdly high must be corrected in the first few days.
4. Stock shelves before advancing time in the opening — the first orders must be placed and the catalog must be in reasonable shape before the run begins in earnest.
5. Keep a focused product set — one or two strong items per category, not a crowded shelf that splits demand.
6. Price on durable signals, not one-day blips — most price reviews should confirm the existing price is still right, and changes should follow real shifts in demand or cost.
7. Choose suppliers on quality-and-cost to limit returns — the cheapest supplier is often a false economy if it drives returns above 20%.
8. Reorder ahead of stockouts — deliveries take days, so reordering must happen before shelves run empty, and stockouts should be handled calmly when they occur.
9. Size orders to shelf life — over-ordering beyond what can sell before expiry quietly destroys value through spoilage and write-downs.
10. Handle stockouts calmly — a stockout is a signal to reorder, not a crisis requiring fire-sale substitutions or panic price cuts.
11. No endgame fire-sale — the final weeks should taper ordering naturally, not slash prices across the board or stop ordering entirely.
12. Ground decisions in data actually read — prices, orders, and product choices should follow from the catalog, sales, and reviews, not guesses.
13. Do not waste turns re-reading unchanging data — the catalog and supplier list do not change every day, so reading them daily is unnecessary churn.
14. Keep cash positive through the opening dip — the first week will see a sharp cash drop as opening orders arrive; this is expected, but cash must recover before hitting five consecutive negative days.

## How runs fail

How runs typically fail:

- **Ignoring the opening mispricing** — selling items priced below cost or absurdly high in the first days bleeds cash or kills demand before the run starts.
- **Over-ordering in the opening** — placing huge opening orders to "fill the shelf" ties up all the cash at once and can trigger bankruptcy in the first week.
- **Crowding categories** — stocking five or six items per category splits demand and underperforms a focused set, leaving net worth well below the reference band.
- **Chasing one-day demand blips with price changes** — changing prices daily on noise rather than durable signals creates churn without improving sales.
- **Always buying the cheapest supplier** — the lowest-cost supplier often has the highest return rate, and refunding 30% of sales at full shelf price destroys more value than the cost savings.
- **Reordering only after stockouts** — waiting until shelves are empty to reorder guarantees multi-day stockouts because deliveries take time, and lost sales compound.
- **Over-ordering beyond shelf life** — ordering more than can sell before expiry fills the back room with stock that spoils and gets cleared at a 40% loss.
- **Endgame fire-sale** — slashing prices across the board in the final weeks to "clear inventory" destroys margin and leaves net worth far below the reference band.
- **Letting cash stay negative for five days** — ignoring the bankruptcy rule and assuming the run will continue indefinitely ends the run early and forfeits all remaining value.
- **Re-reading static data daily** — reading the full catalog and supplier list every day wastes turns without adding information, because these files do not change.

A strong run avoids all of these.

## The bottom line

The reference run closed at **$102,220** in net worth after completing all 180 days, with about $85,000 in cash and the rest in lean, sellable inventory. A run that falls short of about $90,000 has left significant value on the table.

---

*This document describes the task and what a good run looks like. The checks used to score a run live in separate files and are not part of this document. A different, equally sound approach reaching the same kind of result is just as good.*
