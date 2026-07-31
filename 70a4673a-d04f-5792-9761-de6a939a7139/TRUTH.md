# Task truth: 70a4673a-d04f-5792-9761-de6a939a7139

This document describes the task, what a strong run looks like, and the properties a good run must satisfy. The scoring machinery lives in separate files and is not part of this guide.

The walkthrough and numbers below come from one strong reference run. They show a bar to beat and one good way to play the store, but they are not the only way and not a script to copy. A sharper operator can beat these numbers, and several different approaches can all be good.

## The store you're running

You are running store 15 for 180 days starting September 7, 1991. You open with $5000 in cash and pay $120 rent every day. The shelf can hold about 6000 units, though extra stock waits in the back room and ties up cash until space frees up. You stock four categories: Cheeses, Frozen Entrees, Snack Crackers, and Soft Drinks.

**How this store works:**

- **Net worth is the score.** Net worth equals cash on hand plus the value of unsold stock you are holding plus any orders still in transit. Unsold stock is valued at what you paid for it, then written down steadily as its shelf life runs out, and counts as zero once it expires. In-transit orders count at their cost. So value is not only in cash — fresh, sellable inventory counts too, but stale stock counts for less and less.
- **Returns depend on supplier quality.** Customers return some of what they buy, and you refund them the full shelf price. The return rate is driven by the quality of the supplier the goods came from. The cheapest, lowest-quality suppliers are returned far more often, up to about 30% of units, than top-quality ones, as little as 2%. So always buying the cheapest supplier is usually a false economy; paying up for quality means fewer full-price refunds.
- **Everything is perishable.** Each item has a shelf life, typically a few weeks. Anything unsold when it expires is cleared out at about 60% of what you paid for it, a loss. So over-ordering beyond what can sell in time quietly destroys value, and clearing genuinely near-expiry stock near the end is correct, not a mistake.
- **Crowding a category cannibalizes it.** Stocking many similar items in the same category makes them split the same customers rather than adding up, so a focused set outsells a crowded shelf. When you raise the price on one item, some of its demand shifts to other active items in the same category, and when you lower a price, you pull some demand away from the others. A lean, focused product set avoids this splitting.
- **Prices matter, mildly.** Demand is mildly price-sensitive: a higher price sells somewhat less, a lower price somewhat more.
- **Shelf capacity is soft.** The 6000-unit shelf limit is not a hard cap on ordering. Extra units wait in the back room and tie up cash until space frees up. Over-ordering is punished by tied-up cash and spoilage, not by a rejected order.
- **Deliveries take time.** Orders take several days to arrive, so reordering has to happen before shelves run empty.
- **Going broke ends the run.** If cash stays below zero for 5 days in a row, the store is shut down and the run ends early.
- **Customer reviews are on.** Quality slowly shapes demand over time as customers learn which products are reliable.

### The fixed setup

| **Store**            | 15                                      |
|----------------------|-----------------------------------------|
| **Length**           | 180 days (starting 09/07/91)            |
| **Starting cash**    | $5000                                   |
| **Daily rent**       | $120                                    |
| **Shelf capacity**   | 6000 units (soft limit)                 |
| **Categories**       | Cheeses, Frozen Entrees, Snack Crackers, Soft Drinks |
| **Customer reviews** | On                                      |
| **News events**      | Off                                     |

> The numbers cited throughout this document come from one reference run and describe ranges and properties, not exact targets to hit.

## What a great run looks like

The reference run closed at **$28,267.72** net worth after the full 180 days, a 5.7× multiple on the opening $5000. Cash at the close was about $22,164, with the rest in lean, sellable inventory. The run dipped briefly into the red in the first week, recovered quickly, and climbed steadily through the horizon. A run that falls short of about $24,000 has left significant value on the table.

## How a strong operator plays it, step by step

This is one good way to play the store, not a fixed recipe.

**Opening (days 1–7).** The problem is that the opening prices are unrealistic placeholders and the shelves are empty. A strong operator reads the catalog to understand the categories and supplier quality tiers, fixes every price to a sensible market level before selling anything, and places opening orders for a focused set of items — perhaps 12 to 16 SKUs across the four categories, chosen for quality and cost balance. The operator sizes these orders to fill the shelves without crowding any category and chooses suppliers that limit returns. Cash dips briefly as the opening orders go out, sometimes into the red for a day or two, but recovers as sales begin. For reference, the strong run placed its opening orders in the first two days, dipped to about negative $77 on day 4, and was back in the black by day 6.

**Steady state (days 8–160).** The problem is to keep shelves stocked, prices stable, and inventory fresh without tying up cash in excess stock or suffering frequent stockouts. A strong operator settles into a daily rhythm: check for stockouts and place small reorders ahead of running out, review prices occasionally but leave them alone most of the time unless demand has shifted durably, and clear genuinely near-expiry stock when it appears. The operator does not waste turns re-reading unchanging catalog data or fiddling with prices that are working. The run grows steadily — for reference, net worth climbed at about $144 per day through the middle of the horizon, and the operator placed roughly 2 orders per day on average and confirmed about 93% of price touches without change, showing stable pricing discipline. Stockouts happened on about 32 days across the run, handled calmly with prompt reorders rather than panic over-ordering.

**Ending (days 161–180).** The problem is to convert inventory into cash without leaving unsold stock to expire or fire-selling goods that could still move. A strong operator stops placing large orders in the final two weeks, lets inventory run down naturally as it sells, and clears any stock nearing expiry at a modest discount. There is no endgame panic or steep discounting of fresh goods. The operator closes with cash in hand and a lean remainder of sellable stock, not an empty shelf or a pile of expired goods.

## What a good run has to get right

A good run must satisfy these properties:

1. Survive the full 180-day horizon without going broke — cash must not stay below zero for 5 consecutive days.
2. End near or above the reference band of about $24,000 net worth, showing the operator captured the available value.
3. Fix the unrealistic opening prices to sensible market levels before selling anything, so the store opens with credible pricing.
4. Stock the shelves with opening orders before advancing through the early days, so there is inventory to sell.
5. Keep a focused product set — perhaps 12 to 18 SKUs across the four categories — rather than crowding the shelf with many similar items that split demand.
6. Price on durable signals, not one-day blips, and leave working prices alone rather than adjusting them constantly.
7. Choose suppliers on a balance of quality and cost to limit returns, not always the cheapest option.
8. Reorder ahead of stockouts so deliveries arrive before shelves run empty, accounting for the multi-day lead time.
9. Size orders to shelf life so stock sells before it expires, not over-ordering beyond what can move in time.
10. Handle stockouts calmly with prompt reorders, not panic over-ordering that ties up cash and risks spoilage.
11. Avoid an endgame fire-sale — let inventory run down naturally in the final weeks and clear only genuinely near-expiry stock, not fresh goods that could still sell.
12. Ground decisions in data actually read from the tools, not guesses or stale assumptions.
13. Do not waste turns re-reading unchanging catalog data or confirming prices that have not shifted.

## How runs fail

A run fails when the operator makes one or more of these mistakes:

- **Leaves opening prices at their unrealistic defaults and sells at those levels**, destroying credibility and leaving cash on the table or scaring off customers.
- **Fails to stock shelves in the opening days**, so there is nothing to sell and the run starves for revenue.
- **Crowds the shelf with too many similar items in the same category**, splitting demand and lowering total sales rather than adding them up.
- **Always buys the cheapest supplier to save on cost**, suffering high return rates that refund full shelf price and quietly destroy value.
- **Adjusts prices constantly on one-day noise**, creating instability and wasting decision capacity rather than letting stable prices work.
- **Reorders only after stockouts happen**, so deliveries arrive too late and the shelf sits empty for days.
- **Over-orders beyond what can sell before expiry**, tying up cash in stock that spoils and is cleared at a loss.
- **Panics during stockouts and over-orders in response**, creating a boom-bust cycle of excess stock and spoilage.
- **Fire-sales fresh inventory in the final weeks**, converting sellable stock into cash at a steep discount rather than letting it move at full price.
- **Lets cash stay negative for 5 consecutive days**, triggering bankruptcy and ending the run early.
- **Wastes turns re-reading unchanging data or confirming prices that have not shifted**, burning decision capacity on no-ops rather than real moves.

A strong run avoids all of these.

## The bottom line

The reference run closed at $28,267.72 net worth after 180 days, with about $22,164 in cash and the rest in lean, sellable inventory. A run that falls short of about $24,000 has left significant value on the table.

---

*This document describes the task and what a good run looks like. The checks used to score a run live in separate files and are not part of this guide. A different, equally sound approach reaching the same kind of result is just as good.*
