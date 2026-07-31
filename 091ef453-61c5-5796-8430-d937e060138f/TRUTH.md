# Task truth: 091ef453-61c5-5796-8430-d937e060138f

This document describes what Store 15 is, how a strong operator runs it over six months, what a good result looks like, and the ways runs go wrong. The scoring machinery that evaluates a run lives in separate files and is not part of this guide.

The walkthrough and numbers below come from one strong reference run. They show one good way to play the store and set a bar to beat, but they are not the only way and not a script to copy. A sharper operator can beat these numbers, and several different sound approaches can all reach a good result.

## The store you're running

Store 15 is a six-month run (180 days, starting September 7, 1991) with $30,000 opening cash, $700 daily rent, and a soft shelf capacity of 25,000 units. The store carries twenty categories: Bathroom Tissues, Beer, Bottled Juices, Canned Soup, Canned Tuna, Cereals, Cheeses, Cigarettes, Cookies, Crackers, Dish Detergent, Fabric Softeners, Front-end Candies, Frozen Entrees, Frozen Juices, Oatmeal, Paper Towels, Snack Crackers, Soft Drinks, and Toothpastes.

How this store works:

- **Net worth is the score.** Net worth equals cash on hand plus the value of unsold stock you are holding plus any orders still in transit. Unsold stock is valued at what you paid for it, then written down steadily as its shelf life runs out, and counts as zero once it expires. In-transit orders count at their cost. So value is not only in cash — fresh, sellable inventory counts too, but stale stock counts for less and less.
- **Returns depend on supplier quality.** Customers return some of what they buy, and the store refunds them the full shelf price. The return rate is driven by the quality of the supplier the goods came from. The cheapest, lowest-quality suppliers are returned far more often (up to about 30% of units) than top-quality ones (as little as 2%). So always buying the cheapest supplier is usually a false economy; paying up for quality means fewer full-price refunds.
- **Everything is perishable.** Each item has a shelf life, typically a few weeks. Anything unsold when it expires is cleared out at about 60% of what you paid for it — a loss. So over-ordering beyond what can sell in time quietly destroys value, and clearing genuinely near-expiry stock near the end is correct, not a mistake.
- **Crowding a category cannibalizes it.** Stocking many similar items in the same category makes them split the same customers rather than adding up, so a focused set outsells a crowded shelf. When you raise the price on one item, some of its demand shifts to other active items in the same category, and when you lower a price, you pull demand away from the others. A lean, focused product set in each category captures more total sales than a crowded one.
- **Prices matter, mildly.** Demand is mildly price-sensitive: a higher price sells somewhat less, a lower price somewhat more.
- **Shelf capacity is soft.** The 25,000-unit shelf limit is not a hard cap on ordering. Extra units wait in the back room and tie up cash until space frees up. Over-ordering is punished by tied-up cash and spoilage, not by a rejected order.
- **Deliveries take time.** Orders take several days to arrive, so reordering has to happen before shelves run empty.
- **Going broke ends the run.** If cash stays below zero for five days in a row, the store is shut down and the run ends early.
- **Customer reviews are on.** Quality slowly shapes demand over time as customers learn which items are reliable.

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
| News events | Off |

> The numbers cited throughout this document come from one reference run. They are ranges and properties to understand, not exact targets to hit.

## What a great run looks like

The reference run closed at **$73,624.52** net worth after completing all 180 days — about 2.5 times the opening cash. Terminal cash was $58,520, with the rest in lean, sellable inventory. The run dipped to a cash trough of about $71 on day 4 as the opening orders arrived, then recovered and climbed steadily at roughly $310 per day through the middle months. A run that falls short of about $60,000 has left significant value on the table.

## How a strong operator plays it, step by step

This is one good way to run the store, not a fixed recipe.

**Opening (days 1–7).** The problem is that the opening prices are unrealistic placeholders and the shelves are empty. A strong operator reads the full catalog to see what is available, fixes the prices to sensible market levels before any sales happen, and places the first wave of orders to stock the shelves. The operator chooses a focused set of items in each category — typically one to three strong sellers per category rather than a crowded shelf — and balances supplier cost against quality to limit returns. Orders are sized to arrive before the shelves are bare but not so large that stock spoils before it sells. For reference, the strong run placed about 90 orders in the opening week and kept 92% of the opening prices it set, showing that the prices were grounded and durable.

**Steady state (days 8–160).** The problem is to keep shelves stocked, prices stable, and cash flowing without tying up value in excess inventory or suffering waves of returns. A strong operator settles into a daily rhythm: check what sold and what is running low, reorder ahead of stockouts (deliveries take several days), and adjust prices only when durable signals — sustained demand shifts, quality trends from reviews, or competitive pressures — call for it. The operator does not chase one-day sales blips or re-read unchanging catalog data every turn. The strong run averaged about nine orders per day, kept prices stable (92% of price touches confirmed the existing level), and grew net worth at roughly $310 per day through the middle months. Stockouts happened on about 100 days across the run, showing that the operator ran lean and accepted occasional gaps rather than over-ordering and spoiling stock.

**Ending (days 161–180).** The problem is to convert inventory to cash without destroying value in a fire sale. A strong operator stops placing large new orders, lets existing stock sell down naturally, and clears genuinely near-expiry items at modest discounts if needed. The operator does not slash prices across the board or dump sellable inventory. The strong run closed with about $58,500 in cash and $15,100 in lean, sellable stock, showing that the operator wound down smoothly without a panic.

## What a good run has to get right

A good run satisfies these properties in its own way:

1. Survive the full 180-day horizon without going broke (cash below zero for five consecutive days).
2. End near or above the reference band of about $60,000 net worth, showing that the operator captured the store's potential.
3. Fix the unrealistic opening prices to sensible market levels before selling, so the run is not built on placeholder numbers.
4. Stock shelves with focused orders before advancing through the opening days, so the store has something to sell.
5. Keep a focused product set in each category rather than crowding the shelf, so items do not cannibalize each other and total sales stay strong.
6. Price on durable signals — sustained demand trends, quality feedback, competitive pressures — not on one-day sales blips, so prices are stable and grounded.
7. Choose suppliers on a balance of quality and cost to limit returns, not always the cheapest, because low-quality suppliers drive return rates up to 30% and refunding full shelf price destroys value.
8. Reorder ahead of stockouts, accounting for delivery time, so shelves do not sit empty for days, but accept occasional gaps rather than over-ordering and spoiling stock.
9. Size orders to shelf life, so stock sells before it expires and value is not quietly destroyed in spoilage and clearance losses.
10. Handle stockouts calmly as a sign of lean operation, not a crisis requiring panic orders, because over-ordering to avoid every gap ties up cash and leads to spoilage.
11. Wind down the endgame by letting stock sell naturally and clearing genuinely near-expiry items at modest discounts, not slashing prices across the board or dumping sellable inventory in a fire sale.
12. Ground decisions in data actually read — current stock levels, sales trends, supplier quality — not guesses or stale information.
13. Do not waste turns re-reading unchanging catalog data or checking the same static information every day, because the run has a finite number of actions and efficiency matters.
14. Maintain a cash cushion through the middle months so the store can reorder freely and is not constantly on the edge of bankruptcy.

## How runs fail

Runs fail in characteristic ways:

- **Keeping the opening placeholder prices** and selling at unrealistic levels, so the run is built on a false foundation and either leaves money on the table or prices itself out of the market.
- **Crowding categories** with many similar items that split the same customers, so total sales in the category fall and the operator wonders why a bigger assortment sells less.
- **Always buying the cheapest supplier** to save on cost, so return rates climb to 30% and refunding full shelf price quietly destroys more value than the cost savings delivered.
- **Chasing one-day sales blips** with constant price changes, so prices whipsaw and the operator never learns what a stable, grounded price level is.
- **Over-ordering to avoid stockouts**, so cash is tied up in excess inventory that spoils before it sells and the 60% clearance loss eats into net worth.
- **Reordering only when shelves are empty**, so deliveries arrive days late and the store sits with nothing to sell for long stretches.
- **Ignoring shelf life** and ordering as if stock lasts forever, so spoilage mounts and value is quietly destroyed.
- **Panicking at the first stockout** and placing huge orders, so the problem shifts from empty shelves to spoilage and tied-up cash.
- **Fire-selling the endgame** by slashing prices across the board in the final weeks, so sellable inventory is dumped at a loss and net worth collapses.
- **Re-reading unchanging catalog data every turn**, so the run wastes actions on static information and runs out of time for the decisions that matter.
- **Running cash to zero repeatedly** in the opening weeks, so the store teeters on the edge of bankruptcy and cannot reorder freely when opportunities arise.

A strong run avoids all of these.

## The bottom line

The reference run closed at $73,624.52 net worth after completing all 180 days, with $58,520 in cash and about $15,100 in lean, sellable inventory. A run that falls short of about $60,000 has left significant value on the table.

---

*This document describes the task and what a good run looks like. The checks used to score a run live in separate files and are not part of this document. A different, equally sound approach reaching the same kind of result is just as good.*
