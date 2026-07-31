# Task truth: 3feb7d26-cc07-54aa-9fba-1ef518298ecd

This document describes the task, what a strong run looks like, and the properties a good run must satisfy. The scoring machinery lives elsewhere and is not part of this file.

The walkthrough and numbers below come from one strong reference run. They show one good way to play the task and set a bar to beat, but they are not the only way and not a script to copy. A sharper operator can beat these numbers, and several different approaches can all be good.

## The store you're running

You are running store 15 for 180 days, starting September 7, 1991. You open with $30,000 in cash and pay $700 rent every day. The shelf can hold about 25,000 units, though this is a soft limit — extra stock waits in the back room and ties up cash until space frees up. You stock twenty categories: Bathroom Tissues, Beer, Bottled Juices, Canned Soup, Canned Tuna, Cereals, Cheeses, Cigarettes, Cookies, Crackers, Dish Detergent, Fabric Softeners, Front-end Candies, Frozen Entrees, Frozen Juices, Oatmeal, Paper Towels, Snack Crackers, Soft Drinks, and Toothpastes.

**How this store works:**

- **Net worth is the score.** Net worth equals cash on hand plus the value of unsold stock you are holding plus any orders still in transit. Unsold stock is valued at what you paid for it, then written down steadily as its shelf life runs out, and counts as zero once it expires. In-transit orders count at their cost. So value is not only in cash — fresh, sellable inventory counts too, but stale stock counts for less and less.
- **Returns depend on supplier quality.** Customers return some of what they buy, and the store refunds them the full shelf price. The return rate is driven by the quality of the supplier the goods came from. The cheapest, lowest-quality suppliers are returned far more often (up to about 30% of units) than top-quality ones (as little as 2%). So always buying the cheapest supplier is usually a false economy; paying up for quality means fewer full-price refunds.
- **Everything is perishable.** Each item has a shelf life, typically a few weeks. Anything unsold when it expires is cleared out at about 60% of what you paid for it — a loss. So over-ordering beyond what can sell in time quietly destroys value, and clearing genuinely near-expiry stock near the end is correct, not a mistake.
- **Crowding a category cannibalizes it.** Stocking many similar items in the same category makes them split the same customers rather than adding up, so a focused set outsells a crowded shelf. When you raise the price on one item, some of its demand shifts to other active items in the same category, and when you lower a price, you pull some demand away from the others. A lean, focused product set in each category performs better than a sprawling one.
- **Prices matter, mildly.** Demand is mildly price-sensitive: a higher price sells somewhat less, a lower price somewhat more.
- **Shelf capacity is soft.** The 25,000-unit limit is not a hard cap on ordering. Extra units wait in the back room and tie up cash until space frees up. Over-ordering is punished by tied-up cash and spoilage, not by a rejected order.
- **Deliveries take time.** Orders take several days to arrive, so reordering has to happen before shelves run empty.
- **Going broke ends the run.** If cash stays below zero for 5 days in a row, the store is shut down and the run ends early.
- **Customer reviews are on.** Quality slowly shapes demand over time as customers learn which products are reliable.

### The fixed setup

| **Store**            | 15                                      |
|----------------------|-----------------------------------------|
| **Length**           | 180 days (starting 09/07/91)            |
| **Starting cash**    | $30,000                                 |
| **Daily rent**       | $700                                    |
| **Shelf capacity**   | 25,000 units (soft limit)               |
| **Categories**       | 20 (listed above)                       |
| **Customer reviews** | On                                      |
| **News events**      | Off                                     |

> The numbers cited below come from one reference run. They are ranges and properties to understand, not exact targets to hit.

## What a great run looks like

The reference run closed at **$109,143** net worth after the full 180 days — a 3.6× multiple on the opening $30,000. Cash at the close was $95,113, with the rest in lean, sellable inventory. The run dipped to a cash trough of $359 on day 4 as opening orders arrived, then recovered and climbed steadily at about $520 per day through the middle stretch. A run that falls short of about $95,000 has left significant value on the table.

## How a strong operator plays it, step by step

This is one good way to play the task, not a fixed recipe.

**Opening (days 1–10).** The store opens with placeholder prices on every item, often wildly off-market. A strong operator reads the market data on day 1, fixes every unrealistic price to something sensible before any customer sees it, then stocks the shelves with opening orders across all twenty categories. The opening orders are sized to fill the shelf without crowding any one category, and the operator chooses suppliers carefully — balancing cost against quality to keep return rates manageable. Orders take several days to arrive, so the operator places them early and advances through the first few days while deliveries come in. Cash dips sharply as orders are paid for, but this is expected and temporary. For reference, the strong run placed about 180 orders in the opening phase and saw cash bottom out at $359 on day 4 before recovering.

**Steady state (days 11–160).** Once shelves are stocked, the operator settles into a daily rhythm: check what sold overnight, check what is running low, reorder ahead of stockouts, and adjust prices only when the data shows a durable reason to move. A strong operator keeps the product set focused — about 80 to 100 active SKUs across the twenty categories, not hundreds — so each item gets enough demand to sell through before it spoils. Reorders are sized to shelf life and expected sales, and the operator continues to favor mid-to-high-quality suppliers to limit returns. Prices are touched often to confirm they are still right, but most touches leave the price unchanged because the market has not moved. Stockouts happen from time to time (the reference run saw stockouts on 108 days), and the operator handles them calmly by reordering and moving on — a few missed sales do not break the run. For reference, the strong run placed about 1600 orders across the full 180 days (roughly 9 per day), kept 93% of price touches unchanged, and grew net worth at about $520 per day through the middle stretch.

**Ending (days 161–180).** As the horizon approaches, the operator stops placing large orders that will not sell in time and lets inventory run down naturally. Anything genuinely near expiry is cleared at a modest discount, but there is no panicked fire-sale of fresh stock. The operator keeps the store open and selling through the final day, and closes with cash in hand and a lean, sellable inventory. For reference, the strong run closed with $95,113 in cash and the rest in inventory, for a total net worth of $109,143.

## What a good run has to get right

A good run must satisfy these properties:

1. Survive the full 180-day horizon without going broke (cash below zero for 5 consecutive days).
2. End near or above the reference band of about $95,000 net worth.
3. Fix the unrealistic opening prices before selling begins, so customers see sensible market prices from day 1.
4. Stock shelves across all twenty categories before advancing through the opening days, so the store is ready to sell.
5. Keep a focused product set — a lean selection in each category that avoids crowding and cannibalization, not a sprawling shelf of hundreds of SKUs.
6. Price on durable signals, not one-day blips — most price reviews confirm the existing price is still right, and changes happen only when the data shows a real reason to move.
7. Choose suppliers on quality-and-cost to limit returns — the cheapest supplier is often a false economy when return rates climb to 30%, so paying up for quality saves money on refunds.
8. Reorder ahead of stockouts, since deliveries take several days — waiting until shelves are empty means lost sales while the next order arrives.
9. Size orders to shelf life — over-ordering beyond what can sell before expiry quietly destroys value through spoilage and write-downs.
10. Handle stockouts calmly — a few missed sales do not break the run, and panicked over-ordering or price cuts often do more harm than good.
11. No endgame fire-sale — let inventory run down naturally in the final weeks, and clear only genuinely near-expiry stock, not fresh goods that still have value.
12. Ground decisions in data actually read — prices, sales, stock levels, and supplier quality all come from the tools, and a strong operator uses them.
13. Do not waste turns re-reading unchanging data — the opening market prices and supplier lists do not change day to day, so reading them once is enough.

## How runs fail

Runs fail in characteristic ways:

- **Ignoring the opening prices.** Leaving the placeholder prices in place means customers see absurd prices on day 1, and sales collapse or returns explode. The run never recovers.
- **Crowding the shelf.** Stocking too many similar items in the same category makes them split the same customers, so total sales are lower than a focused set would achieve. The operator works harder for less.
- **Chasing the cheapest supplier every time.** The lowest-cost supplier often has the highest return rate, and refunding 30% of sales at full shelf price destroys more value than the cost savings create.
- **Over-ordering beyond shelf life.** Ordering more than can sell before expiry means spoilage, write-downs, and tied-up cash. The operator thinks they are building inventory, but they are quietly burning value.
- **Reacting to one-day noise.** Changing prices or order sizes based on a single day's blip creates churn and mistakes. Durable signals take a few days to confirm.
- **Waiting until stockouts to reorder.** Deliveries take several days, so reordering only when shelves are empty means lost sales while the next order arrives.
- **Panicking at stockouts.** A few missed sales do not break the run, but over-ordering or slashing prices in response often does.
- **Fire-sale at the end.** Dumping fresh inventory at steep discounts in the final weeks destroys value that could have been held as sellable stock or sold at normal prices.
- **Going broke early.** Spending too much too fast, or failing to recover from the opening cash dip, means cash stays negative for 5 days and the run is shut down.
- **Ignoring the data.** Guessing at prices, suppliers, or order sizes instead of reading the tools means decisions are blind, and blind decisions are usually wrong.

A strong run avoids all of these.

## The bottom line

The reference run closed at **$109,143** net worth after 180 days, with $95,113 in cash and the rest in lean, sellable inventory. It grew steadily at about $520 per day through the middle stretch, handled stockouts calmly, and closed with value intact. A run that falls short of about $95,000 has left significant value on the table.

---

*This file describes the task and what a good run looks like. The checks used to score a run live in separate files and are not part of this document. A different, equally sound approach reaching the same kind of result is just as good.*
