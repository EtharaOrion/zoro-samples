# Task truth: 48e706d5-72f5-5b53-860f-25618297a128

This document describes the task, what a strong run looks like, and the requirements a good run must satisfy. The scoring machinery lives elsewhere and is not part of this file.

The walkthrough and numbers below come from one strong reference run. They show a bar to beat and one good way to play, not the only way and not a script to copy. A sharper operator can beat these numbers, and several different approaches can all be good.

## The store you're running

You are running store 15 for 180 days starting September 7, 1991. You open with $50,000 in cash and pay $1,000 rent every day. The shelf can hold about 40,000 units, though this is a soft limit — extra stock waits in the back room and ties up cash until space frees up. You stock 20 categories: Bathroom Tissues, Beer, Bottled Juices, Canned Soup, Canned Tuna, Cereals, Cheeses, Cigarettes, Cookies, Crackers, Dish Detergent, Fabric Softeners, Front-end Candies, Frozen Entrees, Frozen Juices, Oatmeal, Paper Towels, Snack Crackers, Soft Drinks, and Toothpastes.

How this store works:

- **Net worth is the score.** Net worth equals cash on hand plus the value of unsold stock plus any orders still in transit. Unsold stock is valued at what you paid for it, then written down steadily as its shelf life runs out, and counts as zero once it expires. In-transit orders count at their cost. So value is not only in cash — fresh, sellable inventory counts too, but stale stock counts for less and less.
- **Returns depend on supplier quality.** Customers return some of what they buy, and the store refunds them the full shelf price. The return rate is driven by the quality of the supplier the goods came from. The cheapest, lowest-quality suppliers are returned far more often (up to about 30% of units) than top-quality ones (as little as 2%). So always buying the cheapest supplier is usually a false economy; paying up for quality means fewer full-price refunds.
- **Everything is perishable.** Each item has a shelf life, typically a few weeks. Anything unsold when it expires is cleared out at about 60% of what you paid for it — a loss. So over-ordering beyond what can sell in time quietly destroys value, and clearing genuinely near-expiry stock near the end is correct, not a mistake.
- **Crowding a category cannibalizes it.** Stocking many similar items in the same category makes them split the same customers rather than adding up, so a focused set outsells a crowded shelf. When you raise the price on one item, some of its demand shifts to other active items in the same category, and vice versa. This is not price sensitivity — it is the way similar products compete for the same shoppers.
- **Prices matter, mildly.** Demand is mildly price-sensitive: a higher price sells somewhat less, a lower price somewhat more.
- **Shelf capacity is soft.** The shelf limit is not a hard cap on ordering. Extra units wait in the back room and tie up cash until space frees up. Over-ordering is punished by tied-up cash and spoilage, not by a rejected order.
- **Deliveries take time.** Orders take several days to arrive, so reordering has to happen before shelves run empty.
- **Going broke ends the run.** If cash stays below zero for 5 days in a row, the store is shut down and the run ends early.
- **Customer reviews are on.** Quality slowly shapes demand over time as customers learn which products are good.

### The fixed setup

| Element | Value |
|---------|-------|
| Store | 15 |
| Length | 180 days (starting 09/07/91) |
| Starting cash | $50,000 |
| Daily rent | $1,000 |
| Shelf capacity | 40,000 units (soft) |
| Categories | 20 (Bathroom Tissues, Beer, Bottled Juices, Canned Soup, Canned Tuna, Cereals, Cheeses, Cigarettes, Cookies, Crackers, Dish Detergent, Fabric Softeners, Front-end Candies, Frozen Entrees, Frozen Juices, Oatmeal, Paper Towels, Snack Crackers, Soft Drinks, Toothpastes) |
| Customer reviews | On |
| News events | Off |

> The numbers cited throughout this document come from one reference run and describe ranges and properties, not exact targets to hit.

## What a great run looks like

The reference run finished all 180 days with a terminal net worth of **$83,175.84**, about 1.66 times the opening cash. Cash at the close was about $61,900, with the rest in lean, sellable inventory. Net worth dipped sharply in the first week as the operator stocked the shelves, recovered by day 30, then climbed steadily at roughly $290 per day through the rest of the run. A run that falls short of about $70,000 has left significant value on the table.

## How a strong operator plays it, step by step

This is one good way to play the task, not a fixed recipe.

**Opening (days 1–10).** The operator faces an empty store and unrealistic opening prices. The first job is to fix the prices before selling anything — the opening numbers are often far from what the market will bear, and selling at bad prices wastes the opening inventory. Next, the operator stocks the shelves with a focused product set, choosing one or two strong items per category rather than crowding the shelf with many similar products. Supplier choice matters from the start: the operator balances cost against quality, knowing that the cheapest suppliers will generate heavy returns that eat into profit. Orders are sized to what can sell within the items' shelf lives, not to fill the capacity. The reference run placed about 9 orders per day in this phase, and cash bottomed out around day 7 at roughly $3,500 before recovering as sales began.

**Steady state (days 11–160).** The daily loop is simple: check what sold and what is running low, reorder ahead of stockouts, and adjust prices when durable signals (like a sustained demand shift or a quality trend) justify it. The operator does not chase one-day blips or re-read unchanging data every turn. Reordering happens before shelves run empty, because deliveries take several days. The reference run kept prices stable most of the time — about 93% of price touches confirmed the existing price rather than changing it — and experienced stockouts on roughly 107 days, handling them calmly by reordering and moving on. Net worth climbed steadily at about $290 per day through this phase, compounding the opening investment.

**Ending (days 161–180).** The operator does not fire-sale the inventory in the final weeks. Clearing genuinely near-expiry stock is correct, but dumping sellable goods at a loss to convert them to cash destroys value, because unsold stock still counts toward net worth at its cost (less any age write-down). The reference run closed with about $61,900 in cash and the rest in lean inventory, for a total of $83,175.84.

## What a good run has to get right

A good run must satisfy these properties:

1. Survive the full 180-day horizon without going broke (cash below zero for 5 consecutive days).
2. End near or above the reference band of roughly $70,000 to $85,000 in net worth.
3. Fix the unrealistic opening prices before selling, so the first sales happen at sensible market prices.
4. Stock the shelves before advancing through the opening days, so the store is ready to sell.
5. Keep a focused product set in each category, not a crowded shelf of many similar items that cannibalize each other.
6. Adjust prices on durable signals like sustained demand shifts or quality trends, not on one-day blips.
7. Choose suppliers on a balance of quality and cost to limit returns, not always the cheapest option.
8. Reorder ahead of stockouts, because deliveries take several days.
9. Size orders to what can sell within the items' shelf lives, not to fill the capacity.
10. Handle stockouts calmly by reordering and moving on, not by over-correcting or panicking.
11. Avoid an endgame fire-sale that dumps sellable inventory at a loss to convert it to cash.
12. Ground pricing and ordering decisions in data actually read from the store, not guesses.
13. Avoid wasting turns re-reading unchanging data or checking the same facts repeatedly.
14. Maintain a cash cushion through the run, never letting cash stay negative for 5 days in a row.

## How runs fail

Runs fail in characteristic ways:

- **Selling at the unrealistic opening prices** wastes the opening inventory and leaves money on the table from the start.
- **Crowding the shelf with many similar items in the same category** makes them split the same customers, so total sales are lower than a focused set would achieve.
- **Always buying the cheapest supplier** generates heavy returns (up to 30% of units) that refund the full shelf price and destroy profit.
- **Chasing one-day demand blips with price changes** creates noise and instability without capturing real trends.
- **Waiting until shelves are empty to reorder** causes stockouts that lose sales, because deliveries take several days.
- **Over-ordering beyond what can sell within shelf life** ties up cash and leads to spoilage losses when unsold stock expires.
- **Fire-selling the inventory in the final weeks** converts sellable stock to cash at a loss, destroying value because unsold stock still counts toward net worth.
- **Letting cash stay negative for 5 days in a row** ends the run early and forfeits the rest of the horizon.
- **Re-reading unchanging data every turn** wastes time without adding information.

A strong run avoids all of these.

## The bottom line

The reference run finished all 180 days with a terminal net worth of **$83,175.84**, about 1.66 times the opening cash. Cash at the close was about $61,900, with the rest in lean, sellable inventory. A run that falls short of about $70,000 has left significant value on the table.

---

*This file describes the task and what a good run looks like. The checks used to score a run live in separate files and are not part of this document. A different, equally sound approach reaching the same kind of result is just as good.*
