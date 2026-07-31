# Task truth: d6927ef5-5755-5bf8-bef6-6a65211a4fcc

This document describes what Store 15 is, how a strong operator runs it over six months, what a good result looks like, and the ways runs go wrong. It is a plain-language guide to the task and the requirements a run must satisfy. The scoring machinery that grades runs lives in separate files and is not part of this document.

The walkthrough and numbers below come from one strong reference run that completed the full horizon and reached a solid result. That run is a bar to beat and one good way to play the store, not the only way and not a script to copy. A sharper operator can beat the numbers, and several different sound approaches can all reach good results.

## The store you're running

You are running Store 15 for 180 days, starting September 7, 1991. You open with $30,000 in cash and pay $700 rent every day. The shelf can hold about 25,000 units, though that is a soft limit — extra stock waits in the back room and ties up cash until space frees up. The store carries twenty categories: Bathroom Tissues, Beer, Bottled Juices, Canned Soup, Canned Tuna, Cereals, Cheeses, Cigarettes, Cookies, Crackers, Dish Detergent, Fabric Softeners, Front-end Candies, Frozen Entrees, Frozen Juices, Oatmeal, Paper Towels, Snack Crackers, Soft Drinks, and Toothpastes.

How this store works:

- **Net worth is the score.** Net worth equals cash on hand plus the value of unsold stock you are holding plus any orders still in transit. Unsold stock is valued at what you paid for it, then written down steadily as its shelf life runs out, and counts as zero once it expires. In-transit orders count at their cost. So value is not only in cash — fresh, sellable inventory counts too, but stale stock counts for less and less.
- **Everything is perishable.** Each item has a shelf life, typically a few weeks. Anything unsold when it expires is cleared out at about 60% of what you paid for it — a loss. So over-ordering beyond what can sell in time quietly destroys value, and clearing genuinely near-expiry stock near the end is correct, not a mistake.
- **Returns depend on supplier quality.** Customers return some of what they buy, and the store refunds them the full shelf price. The return rate is driven by the quality of the supplier the goods came from — the cheapest, lowest-quality suppliers are returned far more often, up to about 30% of units, than top-quality ones, as little as 2%. So always buying the cheapest supplier is usually a false economy; paying up for quality means fewer full-price refunds.
- **Crowding a category cannibalizes it.** Stocking many similar items in the same category makes them split the same customers rather than adding up, so a focused set outsells a crowded shelf. A handful of well-chosen items in each category will outperform a sprawling assortment.
- **Prices matter, mildly.** Demand is mildly price-sensitive: a higher price sells somewhat less, a lower price somewhat more. Raising the price on one item also redirects some demand to other active items in the same category, and vice versa.
- **Shelf capacity is soft.** The 25,000-unit limit is not a hard cap on ordering — extra units wait in the back room and tie up cash until space frees up. Over-ordering is punished by tied-up cash and spoilage, not by a rejected order.
- **Deliveries take time.** Orders take several days to arrive, so reordering has to happen before shelves run empty.
- **Going broke ends the run.** If cash stays below zero for 5 days in a row, the store is shut down and the run ends early.
- **Customer reviews are on.** Quality slowly shapes demand over time as customers notice which items hold up and which disappoint.

### The fixed setup

| Element | Value |
|---------|-------|
| Store | 15 |
| Length | 180 days (starting 09/07/91) |
| Starting cash | $30,000 |
| Daily rent | $700 |
| Shelf capacity | 25,000 units (soft limit) |
| Categories | 20 (Bathroom Tissues, Beer, Bottled Juices, Canned Soup, Canned Tuna, Cereals, Cheeses, Cigarettes, Cookies, Crackers, Dish Detergent, Fabric Softeners, Front-end Candies, Frozen Entrees, Frozen Juices, Oatmeal, Paper Towels, Snack Crackers, Soft Drinks, Toothpastes) |
| Customer reviews | On |
| News events | Off |

> The numbers cited throughout this document come from one reference run and describe ranges and properties a good run should satisfy, not exact targets to hit.

## What a great run looks like

The reference run closed at **$55,056** net worth after 180 days, an 84% gain over the opening $30,000. It completed the full horizon without going broke. At the close, the store held about $39,200 in cash and roughly $15,800 in fresh, sellable inventory still moving off the shelves. Net worth dipped sharply in the opening days as the operator stocked the shelves, recovered within the first two weeks, then climbed steadily through the rest of the run. A run that falls short of about $48,000 has left significant value on the table.

## How a strong operator plays it, step by step

This is one good way to run the store, not a fixed recipe. A different sound approach reaching the same kind of result is just as good.

**Opening (days 1–7).** The problem is an empty store with unrealistic placeholder prices and no stock. A strong operator reads the full catalog to understand what is available, fixes the placeholder prices to realistic levels before any sales happen, chooses a focused set of items across all twenty categories — avoiding a crowded shelf in any one — and places opening orders sized to fill the shelves without tying up all the cash. The operator balances supplier cost against quality, paying up where returns would otherwise eat into margin. Orders arrive over the next few days, shelves fill, and sales begin. For reference, the strong run placed about 90 orders in the opening week and saw cash dip to around $7 by day 4 before recovering as sales came in.

**Steady state (days 8–160).** The problem is keeping shelves stocked, prices sound, and inventory fresh while rent drains $700 every day. A strong operator settles into a daily rhythm: check what sold and what is running low, reorder ahead of stockouts in quantities matched to shelf life and remaining demand, adjust prices when durable signals — several days of data or a clear quality trend — justify it but leave stable prices alone when nothing has changed, and keep the product set lean so categories do not cannibalize themselves. The operator does not waste turns re-reading static catalog data or fiddling with prices that are working. Stockouts happen occasionally — the reference run saw them on about half the days — and the operator handles them calmly by restocking promptly, not by over-ordering in panic. For reference, the strong run placed about 8 to 9 orders per day during this phase, kept about 92% of price touches at the existing level, and grew net worth by roughly $200 per day on average.

**Ending (days 161–180).** The problem is closing out cleanly without destroying value. A strong operator continues normal operations — restocking items that still have time to sell, holding prices steady, running the store as usual — and does not fire-sale the inventory or stop ordering just because the end is near. Fresh stock ordered in the final weeks still sells and still counts toward net worth. The operator clears genuinely near-expiry stock at a modest discount if it will not move in time, but does not dump sellable inventory. The reference run closed with about $15,800 in fresh inventory still on the shelves, not an empty store.

## What a good run has to get right

A good run must satisfy these properties, in its own way:

1. Survive the full 180-day horizon without going broke — cash must not stay below zero for 5 consecutive days.
2. End near or above the reference band, around $48,000 to $55,000 net worth, showing the operator extracted value from the opportunity.
3. Fix the unrealistic opening placeholder prices to sensible levels before selling begins, so early sales do not happen at nonsense prices.
4. Stock the shelves with a focused product set before advancing through the opening days, so the store has something to sell when customers arrive.
5. Keep the product set lean within each category — a handful of well-chosen items outperforms a crowded shelf that cannibalizes itself.
6. Price on durable signals, not one-day blips — adjust when several days of data or a clear quality trend justifies it, but leave stable prices alone when nothing has changed.
7. Choose suppliers balancing cost against quality to limit returns — the cheapest supplier is often a false economy when returns hit 30%, while paying up for quality can mean returns as low as 2%.
8. Reorder ahead of stockouts, sizing orders to shelf life and remaining demand so stock arrives before shelves run empty but does not spoil before it sells.
9. Handle occasional stockouts calmly by restocking promptly, not by over-ordering in panic and tying up cash in excess inventory.
10. Run the store normally through the final weeks — no endgame fire-sale, no stopping orders just because the end is near; fresh stock ordered late still sells and still counts.
11. Ground pricing and ordering decisions in data actually read from the tools, not guesses or stale information.
12. Do not waste turns re-reading unchanging catalog data or fiddling with prices that are already working — efficient operators spend their time on decisions that matter.

## How runs fail

Runs fail in characteristic ways:

- **Ignoring supplier quality** — always buying the cheapest supplier to save a few cents per unit, then losing dollars per unit to returns when 30% of sales come back for full refunds.
- **Crowding categories** — stocking ten similar items in one category so they split the same customers and all sell poorly, instead of a focused few that would each sell well.
- **Chasing noise** — adjusting prices every day based on one-day sales blips, creating chaos instead of letting stable prices work.
- **Over-ordering** — placing huge orders that tie up all the cash and spoil before they sell, quietly destroying value as inventory ages past its shelf life.
- **Reacting to stockouts with panic** — seeing one item run out and ordering ten times too much, locking up cash and creating new spoilage problems.
- **Fire-selling the endgame** — slashing prices or stopping orders in the final weeks, leaving the store empty or dumping sellable inventory at a loss when it could have sold normally.
- **Running on stale data** — making pricing or ordering decisions without reading current sales and stock levels, so choices drift out of touch with reality.
- **Wasting time on static reads** — re-reading the full catalog every day or checking prices that have not changed, burning turns that could have gone to real decisions.
- **Going broke early** — running cash negative for 5 days in a row and getting shut down, ending the run with most of the horizon unplayed.

A strong run avoids all of these.

## The bottom line

The reference run closed at **$55,056** net worth after 180 days, holding about $39,200 in cash and roughly $15,800 in fresh, sellable inventory still moving off the shelves. A run that falls short of about $48,000 has left significant value on the table.

---

*This document describes the task and what a good run looks like. The checks used to score a run live in separate files and are not part of this document. A different, equally sound approach reaching the same kind of result is just as good.*
