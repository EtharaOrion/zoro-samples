# Task truth: defa01ea-8403-5732-afe2-ad19a98302b4

This document is a plain-language guide to the task, what a strong run looks like, and the properties a good run must satisfy. The scoring machinery lives in separate files and is not part of this document.

The walkthrough and numbers below come from one strong reference run. They show a bar to beat and one good way to play, not the only way and not a script to copy. A sharper operator can beat these numbers, and several different approaches can all be good.

## The store you're running

You are running store 15 for 180 days starting September 7, 1991. You open with $10,000 in cash and pay $250 rent every day. The shelf can hold about 10,000 units, though this is a soft limit — extra stock waits in the back room and ties up cash until space frees up. You stock five categories: Bathroom Tissues, Cheeses, Frozen Entrees, Snack Crackers, and Soft Drinks.

How this store works:

- **Net worth is the score.** Net worth equals cash on hand plus the value of unsold stock you are holding plus any orders still in transit. Unsold stock is valued at what you paid for it, then written down steadily as its shelf life runs out, and counts as zero once it expires. In-transit orders count at their cost. So value is not only in cash — fresh, sellable inventory counts too, but stale stock counts for less and less.
- **Returns depend on supplier quality.** Customers return some of what they buy, and the store refunds them the full shelf price. The return rate is driven by the quality of the supplier the goods came from. The cheapest, lowest-quality suppliers are returned far more often (up to about 30% of units) than top-quality ones (as little as 2%). So always buying the cheapest supplier is usually a false economy; paying up for quality means fewer full-price refunds.
- **Everything is perishable.** Each item has a shelf life, typically a few weeks. Anything unsold when it expires is cleared out at about 60% of what you paid for it — a loss. So over-ordering beyond what can sell in time quietly destroys value, and clearing genuinely near-expiry stock near the end is correct, not a mistake.
- **Crowding a category cannibalizes it.** Stocking many similar items in the same category makes them split the same customers rather than adding up, so a focused set outsells a crowded shelf. When you raise the price on one item, some of its demand shifts to other active items in the same category, and vice versa. A lean product line in each category performs better than a sprawling one.
- **Prices matter, mildly.** Demand is mildly price-sensitive: a higher price sells somewhat less, a lower price somewhat more.
- **Shelf capacity is soft.** The shelf limit is not a hard cap on ordering. Extra units wait in the back room and tie up cash until space frees up. Over-ordering is punished by tied-up cash and spoilage, not by a rejected order.
- **Deliveries take time.** Orders take several days to arrive, so reordering has to happen before shelves run empty.
- **Going broke ends the run.** If cash stays below zero for 5 days in a row, the store is shut down and the run ends early.
- **Customer reviews are on.** Quality slowly shapes demand over time as customers learn which products are good.

### The fixed setup

| **Store** | 15 |
| **Length** | 180 days (starting 09/07/91) |
| **Starting cash** | $10,000 |
| **Daily rent** | $250 |
| **Shelf capacity** | ~10,000 units (soft limit) |
| **Categories** | Bathroom Tissues, Cheeses, Frozen Entrees, Snack Crackers, Soft Drinks |
| **Customer reviews** | On |
| **News events** | Off |

> The numbers cited throughout this document come from one reference run and describe ranges and properties, not exact targets to hit.

## What a great run looks like

The reference run ended at **$29,173.83** net worth after completing all 180 days — nearly triple the opening cash. Terminal cash was about $22,700, with the rest in lean, sellable inventory. The run dipped briefly into the red in the first week, recovered by day 10, and then climbed steadily at roughly $150 per day through the middle and late stages. A run that falls short of about $24,000 has left significant value on the table.

## How a strong operator plays it, step by step

This is one good way to play the task, not a fixed recipe.

**Opening (days 1–10): Fix prices, stock shelves, and survive the cash dip.** The store opens with unrealistic placeholder prices on many items. A strong operator reads the catalog, corrects those prices to sensible market levels before selling anything, and places opening orders for a focused set of items in each category — typically two to four per category, chosen for a balance of quality and cost. The opening orders drain cash fast, and rent keeps coming, so cash dips below zero for a few days (the reference hit a low of about negative $160 on day 5). This is normal and not a crisis. Deliveries arrive, sales start, and cash recovers by day 10. The operator confirms that shelves are stocked and prices are grounded before advancing past the first few days.

**Steady state (days 11–160): Reorder ahead, keep the set focused, and let quality build demand.** Once the store is running, the daily loop is simple. The operator checks stock levels each morning, places reorders a few days before items run out (deliveries take time), and sizes each order to what can sell before it spoils. Prices stay stable most of the time — the reference kept the existing price on over 90% of the 1,800 price touches across the run, adjusting only when a clear signal (a sustained demand shift or a cost change) called for it. The product set stays lean: a few strong items per category, not a sprawling shelf. The operator chooses suppliers on a quality-and-cost balance to limit returns, not just the cheapest option. Stockouts happen occasionally (the reference had stockouts on 45 days) but are handled calmly by reordering, not by panic-buying or abandoning the item. Net worth climbs steadily as sales compound and inventory stays fresh. The reference placed about 450 orders across the run, roughly 2 to 3 per day.

**Ending (days 161–180): Taper orders and close with lean inventory.** In the final three weeks, the operator stops placing large orders and lets inventory run down naturally, reordering only what can sell before the horizon. The goal is to close with cash and a small amount of fresh stock, not a back room full of goods that will expire the day after the run ends. The reference closed with about $22,700 in cash and roughly $6,500 in inventory — lean, but still selling. No fire-sale, no dumping good stock at a loss, just a smooth taper.

## What a good run has to get right

A good run must satisfy these properties:

1. Survive the full 180-day horizon without going broke (cash below zero for 5 consecutive days).
2. End near or above the reference band of about $24,000 to $29,000 net worth.
3. Fix the unrealistic opening prices before selling, grounding them in the catalog data actually read.
4. Stock shelves with opening orders before advancing past the first few days.
5. Keep a focused product set in each category — a few strong items, not a crowded shelf that cannibalizes itself.
6. Price on durable signals (sustained demand shifts, cost changes, quality trends), not one-day blips or arbitrary schedules.
7. Choose suppliers on a quality-and-cost balance to limit returns, not always the cheapest option.
8. Reorder ahead of stockouts, accounting for delivery time.
9. Size orders to shelf life — do not over-order beyond what can sell before spoilage.
10. Handle occasional stockouts calmly by reordering, not by abandoning items or panic-buying.
11. Taper orders in the final weeks to close with lean inventory, not a fire-sale or a back room full of unsellable stock.
12. Ground decisions in data actually read from the tools, not guesses or stale assumptions.
13. Do not waste turns re-reading unchanging data (the catalog, supplier lists) every day.
14. Let the cash dip in the opening week recover naturally as deliveries arrive and sales start, rather than starving the shelves to avoid it.

## How runs fail

Runs fail in characteristic ways:

- **Selling at placeholder prices** — advancing without fixing the unrealistic opening prices destroys value immediately, either by giving goods away or by pricing so high nothing sells.
- **Advancing with empty shelves** — placing orders but not waiting for deliveries to arrive means the store opens with nothing to sell, wasting days of rent.
- **Crowding the shelf** — stocking too many items in the same category makes them cannibalize each other, so total sales are lower than a focused set would achieve.
- **Chasing noise** — adjusting prices every day in response to one-day sales blips creates churn without improving results.
- **Always buying the cheapest supplier** — the lowest-cost suppliers have the highest return rates, so the full-price refunds eat the cost savings and then some.
- **Reordering too late** — waiting until an item is out of stock to reorder means several days of lost sales while the delivery is in transit.
- **Over-ordering perishables** — ordering more than can sell before expiration ties up cash in stock that will be cleared at a loss.
- **Panic after a stockout** — abandoning an item or over-ordering in reaction to one stockout wastes the demand the item was capturing.
- **Fire-sale at the end** — slashing prices or dumping good inventory in the final days destroys value that could have been preserved by a smooth taper.
- **Starving the opening** — refusing to let cash dip in the first week leaves shelves understocked and sales too low to recover.
- **Re-reading static data** — checking the catalog or supplier list every day wastes turns on data that does not change.
- **Ignoring the data** — making decisions without reading stock levels, sales, or supplier quality means flying blind.

A strong run avoids all of these.

## The bottom line

The reference run closed at **$29,173.83** net worth after completing all 180 days. Terminal cash was about $22,700, with the rest in lean, sellable inventory. The run climbed steadily through the middle and late stages at roughly $150 per day. A run that falls short of about $24,000 has left significant value on the table.

---

*This document describes the task and what a good run looks like. The checks used to score a run live in separate files and are not part of this document. A different, equally sound approach reaching the same kind of result is just as good.*
