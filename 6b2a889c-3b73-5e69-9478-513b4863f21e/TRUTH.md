# Task truth: 6b2a889c-3b73-5e69-9478-513b4863f21e

This document describes the task, what a strong run looks like, and the properties a good run must satisfy. The scoring machinery that evaluates runs lives in separate files and is not part of this document.

The walkthrough and numbers below come from one strong reference run. They show one good way to play the task and set a bar to beat, but they are not the only way and not a script to copy. A sharper operator can beat these numbers, and several different approaches can all be good runs.

## The store you're running

You are running store 15 for 180 days starting September 7, 1991. You open with $30,000 in cash and pay $700 rent every day. The shelf has a soft capacity of 25,000 units — you can order beyond it, but extra stock waits in the back room and ties up cash until space frees up. You stock twenty categories: Bathroom Tissues, Beer, Bottled Juices, Canned Soup, Canned Tuna, Cereals, Cheeses, Cigarettes, Cookies, Crackers, Dish Detergent, Fabric Softeners, Front-end Candies, Frozen Entrees, Frozen Juices, Oatmeal, Paper Towels, Snack Crackers, Soft Drinks, and Toothpastes.

How this store works:

- **Net worth is the score.** Net worth = cash + the value of unsold stock + orders in transit. Unsold stock is valued at what you paid for it, then written down steadily as its shelf life runs out, and counts as zero once it expires. In-transit orders count at their cost. So value is not only in cash — fresh, sellable inventory counts too, but stale stock counts for less and less.
- **Everything is perishable.** Each item has a shelf life of a few weeks. Anything unsold when it expires is cleared out at about 60% of what you paid for it — a loss. Over-ordering beyond what can sell in time quietly destroys value.
- **Returns depend on supplier quality.** Customers return some of what they buy, and you refund them the full shelf price. The return rate is driven by the quality of the supplier the goods came from. The cheapest, lowest-quality suppliers are returned far more often (up to about 30% of units) than top-quality ones (as little as 2%). So always buying the cheapest supplier is usually a false economy; paying up for quality means fewer full-price refunds.
- **Crowding a category cannibalizes it.** Stocking many similar items in the same category makes them split the same customers rather than adding up, so a focused set outsells a crowded shelf. When you stock multiple items in one category, they compete for the same pool of demand.
- **Prices matter, mildly.** Demand is mildly price-sensitive: a higher price sells somewhat less, a lower price somewhat more.
- **Deliveries take time.** Orders take several days to arrive, so reordering has to happen before shelves run empty.
- **Going broke ends the run.** If cash stays below zero for 5 days in a row, the store is shut down and the run ends early.
- **Customer reviews are on.** Quality slowly shapes demand over time as customers learn which products are reliable.
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

> The numbers cited throughout this document come from one reference run. They are ranges and properties to understand, not exact targets to hit.

## What a great run looks like

The reference run closed at **$133,419.54** net worth after completing all 180 days — more than quadruple the opening cash. Terminal cash was $121,970 with the rest in lean, sellable inventory. The run dipped briefly into the red in the opening days, recovered by day 10, and then climbed steadily at about $740 per day through the middle and late phases. A run that falls short of $100,000 has left significant value on the table.

## How a strong operator plays it, step by step

This is one good way to play the task, not a fixed recipe.

**Opening (days 1–10): Fix prices, stock shelves, and survive the cash trough.** The store opens with unrealistic placeholder prices on many items. A strong operator reads the catalog, identifies items priced far above or below the market, and corrects them before selling begins. Then they place opening orders across all twenty categories, choosing one or two strong items per category to keep the shelf focused and avoid cannibalization. They balance supplier cost against quality — paying a bit more for mid-to-high-quality suppliers cuts return rates and protects margin. Orders are sized to fit the soft shelf capacity and the items' shelf lives, so nothing spoils before it can sell. Cash dips into the red for a few days as opening orders arrive and rent accrues, but sales begin and the store recovers by day 10. For reference, the strong run dipped to about negative $300 on day 4 and was back in the black by day 10.

**Steady state (days 11–160): Reorder ahead, keep prices stable, and let the business compound.** Once shelves are stocked and prices are set, the daily loop is simple: check for stockouts, reorder items that are running low before they run out, and leave prices alone unless a durable signal (a sustained demand shift, a news event, or a quality trend from reviews) justifies a change. Reordering happens several days before shelves empty, because deliveries take time. Orders are sized to what will sell within the item's shelf life, so fresh stock keeps turning and nothing piles up to spoil. The operator does not waste turns re-reading unchanging catalog data or fiddling with prices that are already working. Stockouts happen occasionally — the reference run had stockouts on about 80 days — but a strong operator handles them calmly by reordering and moving on, not by panic-buying or abandoning the item. For reference, the strong run placed about 1,260 orders across the full 180 days (roughly 7 per day), kept prices stable on about 92% of touches, and grew net worth at about $740 per day through this phase.

**Ending (days 161–180): Run out the clock without a fire sale.** As the horizon approaches, the operator stops placing large orders that will not sell in time, but does not dump inventory at a loss. They let existing stock sell down naturally, reorder only fast movers in small quantities, and close with lean but still-selling shelves. The reference run ended with about $11,000 in inventory — enough to keep serving customers to the last day, but not so much that value was left rotting on the shelf.

## What a good run has to get right

A good run satisfies these properties:

1. Survives the full 180-day horizon without going broke (cash below zero for 5 consecutive days).
2. Ends near or above the reference band of $100,000 to $135,000 net worth.
3. Fixes the unrealistic opening prices before selling begins, so the store does not bleed margin on mispriced goods.
4. Stocks shelves across all twenty categories in the opening days before advancing time, so the store is ready to serve customers.
5. Keeps a focused product set in each category — one or two strong items per category — rather than crowding the shelf with many similar items that cannibalize each other.
6. Prices on durable signals like sustained demand shifts, news events, or quality trends from reviews, not on one-day blips or noise.
7. Chooses suppliers on a balance of quality and cost to limit return rates, rather than always buying the cheapest and eating the refunds.
8. Reorders ahead of stockouts, because deliveries take several days and waiting until shelves are empty means lost sales.
9. Sizes orders to what will sell within the item's shelf life, so fresh stock keeps turning and nothing spoils in the back room.
10. Handles occasional stockouts calmly by reordering and moving on, not by abandoning the item or panic-buying.
11. Runs out the clock in the final weeks without a fire sale — lets stock sell down naturally rather than dumping inventory at a loss.
12. Grounds decisions in data actually read from the tools, not in guesses or stale information.
13. Does not waste turns re-reading unchanging catalog data or fiddling with prices that are already working.

## How runs fail

Runs fail in characteristic ways:

- **Selling at the unrealistic opening prices** bleeds margin and destroys net worth in the first days.
- **Advancing time before stocking shelves** means the store opens empty and loses the opening sales window.
- **Crowding categories with many similar items** cannibalizes demand and leaves the shelf full of slow movers.
- **Chasing one-day price blips** or re-reading unchanging data wastes turns and leaves no time for the real work of reordering.
- **Always buying the cheapest supplier** invites high return rates that eat the cost savings and then some.
- **Waiting until stockouts happen to reorder** means lost sales while deliveries are in transit.
- **Over-ordering beyond what can sell in time** ties up cash in spoiling stock and quietly destroys value.
- **Abandoning items after a stockout** shrinks the product set and leaves categories underserved.
- **Running a fire sale in the final weeks** dumps inventory at a loss and destroys the net worth the run built.
- **Guessing instead of reading data** leads to decisions that do not match the store's actual state.

A strong run avoids all of these.

## The bottom line

The reference run closed at $133,419.54 net worth after completing all 180 days, with $121,970 in cash and about $11,000 in lean, sellable inventory. A run that falls short of $100,000 has left significant value on the table.

---

*This file describes the task and what a good run looks like. The checks used to score a run live in separate files and are not part of this document. A different, equally sound approach reaching the same kind of result is just as good.*
