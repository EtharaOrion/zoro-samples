# Task truth: 4091bea3-bab5-53fc-b81d-5bd6286cf1bf

This document describes what the task is, how a strong operator runs it, what a good result looks like, and the ways runs go wrong. The scoring machinery that evaluates a run lives in separate files and is not part of this guide.

The walkthrough and numbers below come from one strong reference run. They show one good way to play the task and set a bar to beat, but they are not the only way and not a script to copy. A sharper operator can beat these numbers, and several different sound approaches can all reach a good result.

## The store you're running

You are running store 15 for 180 days, starting September 7, 1991. You open with $5000 in cash and pay $120 rent every day. The shelf can hold about 6000 units, though this is a soft limit — extra stock waits in the back room and ties up cash until space frees up. You stock four categories: Cheeses, Frozen Entrees, Snack Crackers, and Soft Drinks.

**How this store works:**

- **Net worth is the score.** Net worth equals cash on hand plus the value of unsold stock you are holding plus any orders still in transit. Unsold stock is valued at what you paid for it, then written down steadily as its shelf life runs out, and counts as zero once it expires. In-transit orders count at their cost. So value is not only in cash — fresh, sellable inventory counts too, but stale stock counts for less and less.
- **Returns depend on supplier quality.** Customers return some of what they buy, and you refund them the full shelf price. The return rate is driven by the quality of the supplier the goods came from. The cheapest, lowest-quality suppliers see return rates up to about 30% of units, while top-quality ones see as little as 2%. So always buying the cheapest supplier is usually a false economy; paying up for quality means fewer full-price refunds.
- **Everything is perishable.** Each item has a shelf life, typically a few weeks. Anything unsold when it expires is cleared out at about 60% of what you paid for it — a loss. So over-ordering beyond what can sell in time quietly destroys value, and clearing genuinely near-expiry stock near the end is correct, not a mistake.
- **Crowding a category cannibalizes it.** Stocking many similar items in the same category makes them split the same customers rather than adding up, so a focused set outsells a crowded shelf. When you add another SKU to a category that already has several active items, each one sells less than it would alone. A tight product line outperforms a sprawling one.
- **Prices matter, mildly.** Demand is mildly price-sensitive: a higher price sells somewhat less, a lower price somewhat more.
- **Shelf capacity is soft.** The 6000-unit shelf limit is not a hard cap on ordering. Extra units wait in the back room and tie up cash until space frees up. Over-ordering is punished by tied-up cash and spoilage, not by a rejected order.
- **Deliveries take time.** Orders take several days to arrive, so reordering has to happen before shelves run empty.
- **Going broke ends the run.** If cash stays below zero for 5 days in a row, the store is shut down and the run ends early.
- **Customer reviews are on.** Quality slowly shapes demand over time as customers learn which products are reliable.

### The fixed setup

| Element | Value |
|---------|-------|
| Store | 15 |
| Length | 180 days (starting 09/07/91) |
| Starting cash | $5000 |
| Daily rent | $120 |
| Shelf capacity | 6000 units (soft) |
| Categories | Cheeses, Frozen Entrees, Snack Crackers, Soft Drinks |
| Customer reviews | On |
| News events | Off |

> The numbers cited throughout this document come from one reference run. They are ranges and properties to understand, not exact targets to hit.

## What a great run looks like

The reference run closed at **$23,538.76** net worth after completing all 180 days — nearly five times the opening cash. At the close, about $18,700 was cash and the rest was lean, sellable inventory. The run dipped briefly into the red in the first few days, recovered by day 10, and then climbed steadily at about $117 per day through the middle and late stages. A run that falls short of about $20,000 has left significant value on the table.

## How a strong operator plays it, step by step

This is one good way to play the task, not a fixed recipe.

**Opening (days 1–10): Fix prices, stock shelves, and survive the cash dip.** The store opens with placeholder prices that are often wildly wrong — some far too high, others far too low. A strong operator reads the catalog on day one, corrects every price to something reasonable for its category and supplier quality, and then places opening orders for a focused set of items across all four categories. The opening orders are sized to fill the shelves without crowding any category, and they favor mid-to-high-quality suppliers to keep return rates manageable. Cash goes negative for a few days while the opening stock arrives and rent keeps coming out, but sales start immediately and the run recovers to positive cash by about day 10. For reference, the strong run placed its opening orders on day 1, dipped to about negative $50 on day 3, and was back in the black by day 10.

**Steady state (days 10–160): Reorder ahead, keep the set focused, and let quality build demand.** Once the shelves are stocked and cash is positive, the daily loop is simple: check what is running low, reorder those items a few days before they run out, and leave prices alone unless a durable signal (a sustained trend in sales or a quality shift from reviews) calls for a change. A strong operator keeps the product set focused — typically two to four active SKUs per category — so each item gets enough volume to sell through before it expires. Orders are sized to the item's shelf life and recent sales rate, and they favor suppliers whose quality justifies their cost. The operator does not waste turns re-reading the catalog or sales history every single day; once prices are set and the rhythm is established, most days need only a stockout check and one or two reorders. For reference, the strong run averaged about two orders per day, kept prices stable over 90% of the time, and saw stockouts on only 35 of the 180 days.

**Ending (days 160–180): Let inventory run down naturally, no fire-sale.** In the final few weeks, a strong operator stops placing large orders and lets the shelves thin out naturally as items sell through. There is no need to clear stock at a loss — the goal is to close with lean, sellable inventory, not zero inventory. Items that are genuinely near expiry and unlikely to sell in time can be cleared, but a broad price cut or a rush to liquidate everything destroys value. For reference, the strong run closed with about $4,800 in fresh inventory still on hand, which counted toward the final net worth.

## What a good run has to get right

A strong run satisfies these properties:

1. Survives the full 180 days without going broke — cash never stays negative for 5 consecutive days.
2. Ends near or above the reference band of about $20,000 net worth, ideally closer to $23,500 or higher.
3. Fixes the unrealistic opening prices before selling begins — every item gets a reasonable price on day one or two, grounded in its category and supplier quality.
4. Stocks all four categories before advancing past the opening phase — the shelves are not left empty in any category.
5. Keeps a focused product set — typically two to four active SKUs per category, not a sprawling shelf that cannibalizes itself.
6. Prices on durable signals, not one-day blips — a price change responds to a sustained trend in sales or a quality shift, not a single day's noise.
7. Chooses suppliers on quality and cost together to limit returns — the cheapest supplier is not always the best deal when return rates are high.
8. Reorders ahead of stockouts — orders go out a few days before an item runs empty, not after the shelf is already bare.
9. Sizes orders to shelf life — an item that expires in three weeks does not get a five-week supply.
10. Handles stockouts calmly — a temporary stockout is not a crisis; the operator reorders and moves on.
11. No endgame fire-sale — the final weeks let inventory run down naturally; there is no broad price cut or rush to liquidate.
12. Grounds decisions in data actually read — prices and orders reflect the catalog, sales, and stock levels the operator has checked, not guesses.
13. Does not waste turns re-reading unchanging data — once the catalog is known and prices are set, most days need only a stockout check and reorders, not a full data refresh.
14. Ends with lean, sellable inventory — the close has some fresh stock on hand, not zero and not a pile of near-expiry goods.

## How runs fail

A run can fail in several characteristic ways:

- **Ignoring the opening prices.** Leaving the placeholder prices in place and selling at wildly wrong levels — some items priced so high they never sell, others so low they give away margin — quietly destroys thousands of dollars of value before the operator even notices.
- **Stocking only one or two categories.** Leaving whole categories empty for weeks or the entire run means the store never taps a quarter or half of its potential demand.
- **Crowding the shelf.** Stocking ten or fifteen SKUs in a single category makes them all cannibalize each other, so total sales are lower than a focused set of three or four would deliver.
- **Always buying the cheapest supplier.** Chasing the lowest cost without checking quality leads to return rates near 30%, which means refunding nearly a third of revenue at full shelf price — a quiet bleed that wrecks the bottom line.
- **Reordering after stockouts.** Waiting until an item is already sold out before placing the next order means losing several days of sales while the new stock is in transit.
- **Over-ordering perishables.** Placing a huge order for an item with a three-week shelf life, then watching half of it expire unsold and get cleared at 60% of cost, is a direct loss.
- **Changing prices every day on noise.** Tweaking prices up and down in response to single-day sales blips, rather than waiting for a durable signal, wastes turns and destabilizes demand.
- **Running a fire-sale at the end.** Slashing prices across the board in the final weeks to "clear inventory" turns sellable stock into a loss and leaves cash on the table.
- **Going broke in the opening phase.** Placing opening orders so large that cash stays negative for 5 straight days ends the run early, often before day 10.
- **Ignoring shelf life entirely.** Treating all stock as if it lasts forever, then discovering at day 150 that half the inventory has expired and been cleared at a loss, is a late-stage collapse.

A strong run avoids all of these.

## The bottom line

The reference run closed at $23,538.76 net worth after completing all 180 days, with about $18,700 in cash and the rest in lean, sellable inventory. It climbed steadily through the middle and late stages at about $117 per day. A run that falls short of about $20,000 has left significant value on the table.

---

*This document describes the task and what a good run looks like. The checks used to score a run live in separate files and are not part of this document. A different, equally sound approach reaching the same kind of result is just as good.*
