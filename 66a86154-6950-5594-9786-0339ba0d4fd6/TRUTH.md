# Task truth: 66a86154-6950-5594-9786-0339ba0d4fd6

This document is a plain-language guide to the task, what a strong run looks like, and the properties a good run must satisfy. The scoring machinery lives in separate files and is not part of this document.

The walkthrough and numbers below come from one strong reference run. They show a bar to beat and one good way to play, not the only way and not a script to copy. A sharper operator can beat these numbers, and several different approaches can all be good.

## The store you're running

You are running store 15 for 180 days starting September 7, 1991. You open with $30,000 in cash and pay $700 rent every day. The shelf can comfortably hold about 25,000 units, though you can order more — extra stock waits in the back room and ties up cash until space frees up. You carry twenty categories: Bathroom Tissues, Beer, Bottled Juices, Canned Soup, Canned Tuna, Cereals, Cheeses, Cigarettes, Cookies, Crackers, Dish Detergent, Fabric Softeners, Front-end Candies, Frozen Entrees, Frozen Juices, Oatmeal, Paper Towels, Snack Crackers, Soft Drinks, and Toothpastes.

**How this store works:**

- **Net worth is the score.** Net worth equals cash on hand plus the value of unsold stock you are holding plus any orders still in transit. Unsold stock is valued at what you paid for it, then written down steadily as its shelf life runs out, and counts as zero once it expires. In-transit orders count at their cost. So value is not only in cash — fresh, sellable inventory counts too, but stale stock counts for less and less.
- **Returns depend on supplier quality.** Customers return some of what they buy, and you refund them the full shelf price. The return rate is driven by the quality of the supplier the goods came from. The cheapest, lowest-quality suppliers are returned far more often (up to about 30% of units) than top-quality ones (as little as 2%). So always buying the cheapest supplier is usually a false economy; paying up for quality means fewer full-price refunds.
- **Everything is perishable.** Each item has a shelf life, typically a few weeks. Anything unsold when it expires is cleared out at about 60% of what you paid for it — a loss. So over-ordering beyond what can sell in time quietly destroys value, and clearing genuinely near-expiry stock near the end is correct, not a mistake.
- **Crowding a category cannibalizes it.** Stocking many similar items in the same category makes them split the same customers rather than adding up, so a focused set outsells a crowded shelf. When you raise the price on one item, some of its demand shifts to other active items in the same category, and vice versa. A lean, well-chosen product set performs better than a sprawling one.
- **Prices matter, mildly.** Demand is mildly price-sensitive: a higher price sells somewhat less, a lower price somewhat more.
- **Shelf capacity is soft.** The 25,000-unit capacity is not a hard cap on ordering. Extra units wait in the back room and tie up cash until space frees up. Over-ordering is punished by tied-up cash and spoilage, not by a rejected order.
- **Deliveries take time.** Orders take several days to arrive, so reordering has to happen before shelves run empty.
- **Going broke ends the run.** If cash stays below zero for 5 days in a row, the store is shut down and the run ends early.
- **Customer reviews are on.** Quality slowly shapes demand over time as customers learn which products are reliable.
- **News events are on.** External events can shift demand for certain categories during the run.

### The fixed setup

| **Element**          | **Value**                                                                                                                                                                                                                                                      |
|----------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Store                | 15                                                                                                                                                                                                                                                             |
| Length               | 180 days (starting 09/07/91)                                                                                                                                                                                                                                   |
| Starting cash        | $30,000                                                                                                                                                                                                                                                        |
| Daily rent           | $700                                                                                                                                                                                                                                                           |
| Shelf capacity       | ~25,000 units (soft)                                                                                                                                                                                                                                           |
| Categories           | Bathroom Tissues, Beer, Bottled Juices, Canned Soup, Canned Tuna, Cereals, Cheeses, Cigarettes, Cookies, Crackers, Dish Detergent, Fabric Softeners, Front-end Candies, Frozen Entrees, Frozen Juices, Oatmeal, Paper Towels, Snack Crackers, Soft Drinks, Toothpastes |
| Customer reviews     | On                                                                                                                                                                                                                                                             |
| News events          | On                                                                                                                                                                                                                                                             |

> The numbers cited throughout this document come from one reference run and describe ranges and properties, not exact targets to hit.

## What a great run looks like

The reference run closed at **$106,738.56** in net worth — about 3.6 times the opening cash — after completing all 180 days. At the close, roughly $92,400 was in cash and the rest in lean, sellable inventory. The run dipped briefly into the red in the opening days, recovered quickly, and then climbed steadily at about $725 per day through the middle and late stages. A run that falls short of about $95,000 in terminal net worth has left significant value on the table.

## How a strong operator plays it, step by step

This is one good way to play the task, not a fixed recipe.

**Opening (days 1–10).** The store starts with a default product set and prices that are often unrealistic. A strong operator reads the opening catalog, identifies the obviously mispriced items (prices far above or below cost, or far from competitors), and corrects them before customers arrive. Then the operator stocks the shelves with a focused product set — one or two strong items per category, chosen for reasonable quality-to-cost balance and steady demand. The operator places initial orders sized to fill the shelves without crowding them, knowing deliveries take a few days. Cash dips briefly into the red as the first orders go out (the reference hit about –$300 on day 4), but sales begin immediately and the account recovers within a week. By day 10, shelves are stocked, prices are grounded, and cash is climbing.

**Steady state (days 11–160).** Each day, the operator checks what sold, what is running low, and what is nearing expiry. The operator reorders items that are selling well and running low, sizing each order to what can sell before it expires — not filling the shelf to the brim, but keeping popular items in stock. The operator watches for stockouts (they happen — the reference had stockouts on about 100 days) and responds calmly by reordering promptly, not by panic-buying or abandoning the item. Prices stay stable most of the time; the operator adjusts them only when demand or cost shifts durably, not in response to one-day blips. The reference kept the existing price on about 91% of all price touches, changing it only when the data justified a move. The operator places about seven orders per day on average, keeping the product set lean and the shelves turning over. Net worth climbs steadily — the reference grew at about $725 per day through this phase — as cash accumulates and inventory stays fresh and sellable.

**Ending (days 161–180).** As the horizon approaches, the operator stops ordering items that cannot sell in time and lets inventory run down naturally. The operator does not fire-sale everything or clear the shelves early; instead, the operator continues selling at normal prices and clears only genuinely near-expiry stock near the very end. The run closes with most value in cash and a small amount of lean, sellable inventory still on hand. The reference closed with about $92,400 in cash and the rest in stock, having completed all 180 days without going broke.

## What a good run has to get right

A good run satisfies these properties:

1. Survives the full 180-day horizon without going broke (cash below zero for 5 consecutive days).
2. Ends near or above the reference band of about $95,000 in net worth.
3. Fixes the unrealistic opening prices before selling begins, grounding them in cost, competitor prices, and demand signals.
4. Stocks the shelves with a focused product set before advancing past the opening days, so sales can begin immediately.
5. Keeps the product set lean — one or two strong items per category — rather than crowding the shelf with many similar items that cannibalize each other.
6. Adjusts prices on durable signals (sustained demand shifts, cost changes, competitor moves), not on one-day sales blips or noise.
7. Chooses suppliers on a quality-and-cost balance to limit returns, not always the cheapest option.
8. Reorders ahead of stockouts, knowing deliveries take several days, and responds to stockouts calmly by reordering promptly.
9. Sizes orders to shelf life, ordering what can sell before it expires rather than filling the shelf to capacity.
10. Handles stockouts as a normal part of operations, not a crisis requiring drastic action or abandonment of the item.
11. Avoids an endgame fire-sale; lets inventory run down naturally in the final weeks and clears only genuinely near-expiry stock near the close.
12. Grounds decisions in data actually read from the tools, not guesses or stale information.
13. Does not waste turns re-reading unchanging data; reads the catalog and competitor prices when they matter, not every day.
14. Closes with most value in cash and a small amount of lean, sellable inventory, not tied up in stale or unsellable stock.

## How runs fail

A run can fail in several characteristic ways:

- **Ignoring the opening prices.** Leaving the default prices in place without checking them against cost or competitors means selling at a loss or scaring customers away, destroying value from day one.
- **Over-ordering in the opening.** Filling the shelf to capacity with every available item ties up all the cash, triggers a long bankruptcy countdown, and leaves no room to respond to what actually sells.
- **Crowding the categories.** Stocking many similar items in the same category makes them split the same customers, so total sales are lower than a focused set would achieve.
- **Chasing one-day noise.** Adjusting prices or orders in response to single-day sales blips rather than durable trends wastes effort and destabilizes the operation.
- **Always buying the cheapest supplier.** The lowest-cost suppliers have the highest return rates, so the full-price refunds eat up the savings and then some.
- **Reordering too late.** Waiting until an item is out of stock to reorder means several days of lost sales while the delivery is in transit.
- **Ordering to capacity, not to shelf life.** Filling the shelf with more than can sell before expiry means the excess spoils and is cleared at a loss.
- **Panicking at stockouts.** Treating a stockout as a crisis and abandoning the item or over-ordering in response disrupts the steady operation and wastes cash.
- **Fire-selling the endgame.** Clearing all inventory in the final weeks at steep discounts destroys value that could have been realized through normal sales or held as sellable stock.
- **Ignoring the data.** Making decisions without reading the sales, stock levels, or competitor prices means flying blind and missing obvious opportunities or problems.
- **Re-reading unchanging data every day.** Wasting turns on catalog or competitor checks that have not changed since yesterday slows the operation and adds no value.

A strong run avoids all of these.

## The bottom line

The reference run closed at $106,738.56 in net worth after completing all 180 days, with about $92,400 in cash and the rest in lean, sellable inventory. A run that falls short of about $95,000 has left significant value on the table.

---

*This document describes the task and what a good run looks like. The checks used to score a run live in separate files and are not part of this document. A different, equally sound approach reaching the same kind of result is just as good.*
