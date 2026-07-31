# Task truth: ed026cee-4d8e-5ebc-a13c-1d8d7ba8f0ee

This document is a plain-language guide to the task, what a strong run looks like, and the properties a good run must satisfy. The scoring machinery that evaluates runs lives in separate files and is not part of this document.

The walkthrough and numbers below come from one strong reference run. They show one good way to play the store and set a bar to beat, but they are not the only way and not a script to copy. A sharper operator can beat these numbers, and several different approaches can all be good runs.

## The store you're running

You are running store 15 for 180 days starting September 7, 1991. You open with $30,000 in cash and pay $700 rent every day. The shelf can comfortably hold about 25,000 units, though extra stock waits in the back room if you order more. You stock twenty categories: Bathroom Tissues, Beer, Bottled Juices, Canned Soup, Canned Tuna, Cereals, Cheeses, Cigarettes, Cookies, Crackers, Dish Detergent, Fabric Softeners, Front-end Candies, Frozen Entrees, Frozen Juices, Oatmeal, Paper Towels, Snack Crackers, Soft Drinks, and Toothpastes.

**How this store works:**

- **Your score is net worth.** Net worth equals cash on hand plus the value of unsold stock you are holding plus any orders still in transit. Unsold stock is valued at what you paid for it, then written down steadily as its shelf life runs out, and counts as zero once it expires. In-transit orders count at their cost. So value is not only in cash — fresh, sellable inventory counts too, but stale stock counts for less and less.
- **Everything is perishable.** Each item has a shelf life, typically a few weeks. Anything unsold when it expires is cleared out at about 60% of what you paid for it, which is a loss. Over-ordering beyond what can sell in time quietly destroys value, and clearing genuinely near-expiry stock near the end is correct, not a mistake.
- **Returns depend on supplier quality.** Customers return some of what they buy, and you refund them the full shelf price. The return rate is driven by the quality of the supplier the goods came from. The cheapest, lowest-quality suppliers are returned far more often, up to about 30% of units, than top-quality ones, as little as 2%. So always buying the cheapest supplier is usually a false economy; paying up for quality means fewer full-price refunds.
- **Crowding a category cannibalizes it.** Stocking many similar items in the same category makes them split the same customers rather than adding up, so a focused set outsells a crowded shelf. A handful of well-chosen items in each category will outperform a sprawling assortment.
- **Prices matter, mildly.** Demand is mildly price-sensitive. A higher price sells somewhat less, a lower price somewhat more. Adjust prices based on durable patterns, not day-to-day noise.
- **Shelf capacity is soft.** The 25,000-unit shelf limit is not a hard cap on ordering. Extra units wait in the back room and tie up cash until space frees up. Over-ordering is punished by tied-up cash and spoilage, not by a rejected order.
- **Deliveries take time.** Orders take several days to arrive, so reordering has to happen before shelves run empty.
- **Going broke ends the run.** If cash stays below zero for five days in a row, the store is shut down and the run ends early.
- **Customer reviews are on.** Quality slowly shapes demand over time as customers learn which products are good.
- **News events are on.** External events can shift demand for certain categories during the run.

### The fixed setup

| Element | Value |
|---------|-------|
| Store | 15 |
| Length | 180 days (starting 09/07/91) |
| Starting cash | $30,000 |
| Daily rent | $700 |
| Shelf capacity | 25,000 units (soft) |
| Categories | 20 (Bathroom Tissues, Beer, Bottled Juices, Canned Soup, Canned Tuna, Cereals, Cheeses, Cigarettes, Cookies, Crackers, Dish Detergent, Fabric Softeners, Front-end Candies, Frozen Entrees, Frozen Juices, Oatmeal, Paper Towels, Snack Crackers, Soft Drinks, Toothpastes) |
| Customer reviews | On |
| News events | On |

> The numbers cited below come from one reference run. They are ranges and properties to understand, not exact targets to hit.

## What a great run looks like

The reference run finished all 180 days with a terminal net worth of **$122,598**, more than four times the opening cash. Cash at the close was about $110,000, with the rest in lean, sellable inventory. The run dipped briefly into the red in the first few days, recovered quickly, and then climbed steadily at roughly $700 per day through the middle and late stages. A run that falls short of about $100,000 has left significant value on the table.

## How a strong operator plays it, step by step

This is one good way to run the store, not a fixed recipe.

**Opening (days 1–10).** The store starts with unrealistic placeholder prices on many items. A strong operator fixes these prices before selling anything, bringing them into line with what the market will bear and what covers costs. Then the operator stocks the shelves with a focused product set, choosing a handful of strong items in each category rather than crowding the shelf with every option. Supplier choice balances cost and quality — the cheapest suppliers often have return rates so high they destroy profit, so paying a bit more for quality is usually the right trade. Orders are sized to what can sell within shelf life, not to fill every inch of capacity. The reference run placed about 70 orders in the first ten days and dipped to about negative $300 in cash on day 4 before recovering as sales began.

**Steady state (days 11–160).** Each day, the operator reads sales and stock levels, reorders items that are running low, and adjusts prices based on durable signals like sustained over- or under-performance, not one-day blips. Reordering happens before shelves run empty, since deliveries take several days. The operator keeps the product set focused, resisting the temptation to add more and more SKUs to a category, since crowding cannibalizes sales. Stockouts happen occasionally and are handled calmly by reordering; they are not emergencies. The reference run placed about seven orders per day during this phase, kept prices stable most of the time (about 92% of price touches confirmed the existing price), and grew net worth at roughly $700 per day.

**Ending (days 161–180).** As the horizon approaches, the operator stops ordering items that cannot sell out before the close and lets inventory run down naturally. There is no fire-sale or panic discounting — items still on the shelf at the end are valued at cost (written down for age), and clearing them early at a loss is worse than holding them. The reference run ended with about $12,000 in inventory, most of it still sellable, and $110,000 in cash.

## What a good run has to get right

A good run must satisfy these properties:

1. Survive the full 180-day horizon without going broke (five consecutive days of negative cash).
2. End with net worth near or above the reference band of roughly $100,000 to $125,000.
3. Fix the unrealistic opening prices before selling, bringing them into line with market reality and cost coverage.
4. Stock shelves with a focused product set before advancing through the early days, rather than leaving them empty or ordering haphazardly.
5. Keep the product set focused in each category, avoiding the trap of crowding the shelf with many similar items that cannibalize each other.
6. Price on durable signals like sustained patterns over several days, not on one-day blips or noise.
7. Choose suppliers based on the quality-and-cost trade-off to limit returns, not always the cheapest option.
8. Reorder ahead of stockouts, since deliveries take several days, and handle occasional stockouts calmly by reordering rather than treating them as crises.
9. Size orders to what can sell within shelf life, not to fill capacity, since over-ordering ties up cash and leads to spoilage losses.
10. Let inventory run down naturally near the end rather than fire-selling or panic-discounting, since items still on the shelf at the close are valued at cost (written down for age) and clearing them early at a loss is worse than holding them.
11. Ground pricing and ordering decisions in sales and stock data actually read from the store, not guesses or stale assumptions.
12. Avoid wasting turns re-reading data that has not changed, like supplier catalogs or item details that are stable across the run.

## How runs fail

Runs fail in characteristic ways:

- **Selling at the unrealistic opening prices** before fixing them destroys profit on early sales and sets a bad baseline for the rest of the run.
- **Crowding categories** with many similar items cannibalizes sales and leaves net worth far below what a focused set would earn.
- **Always buying the cheapest supplier** to save pennies on cost leads to return rates so high they wipe out the savings and then some.
- **Chasing one-day price blips** with constant adjustments creates noise and misses the durable patterns that matter.
- **Waiting until shelves are empty to reorder** causes stockouts that lose sales, since deliveries take several days.
- **Over-ordering to fill capacity** ties up cash in stock that cannot sell before it expires, quietly destroying value through spoilage.
- **Fire-selling inventory near the end** to "convert it to cash" actually destroys value, since unsold stock is valued at cost (written down for age) and clearing it early at a loss is worse than holding it.
- **Ignoring the quality-cost trade-off** and treating all suppliers as interchangeable leaves the store vulnerable to high return rates.
- **Going broke in the first week** by ordering too much too fast before sales revenue arrives ends the run early.
- **Leaving shelves empty for days** while cash sits idle wastes the opportunity to earn and grow.

A strong run avoids all of these.

## The bottom line

The reference run finished all 180 days with a terminal net worth of **$122,598**, cash of about $110,000, and lean, sellable inventory of about $12,000. A run that falls short of roughly $100,000 has left significant value on the table.

---

*This file describes the task and what a good run looks like. The checks used to score a run live in separate files and are not part of this document. A different, equally sound approach reaching the same kind of result is just as good.*
