# Task truth: cbd603c3-5115-5a8c-9b19-06eee19acc02

This document is a plain-language guide to the task, what a strong run looks like, and the requirements a good run must satisfy. The scoring machinery lives elsewhere and is not part of this file.

The walkthrough and numbers below come from one strong reference run. They show a bar to beat and one good way to play the store, but they are not the only way and not a script to copy. A sharper operator can beat these numbers, and several different approaches can all be good.

## The store you're running

You are running store 15 for 180 days starting September 7, 1991. You open with $5,000 in cash and pay $120 in rent every day. The shelf can comfortably hold about 6,000 units, though extra stock can wait in the back room and tie up cash until space frees up. You sell four categories: Cheeses, Frozen Entrees, Snack Crackers, and Soft Drinks.

How this store works:

- **Net worth is the score.** Your net worth is cash on hand plus the value of unsold stock you are holding plus any orders still in transit. Unsold stock is valued at what you paid for it, then written down steadily as its shelf life runs out, and counts as zero once it expires. In-transit orders count at their cost. So value is not only in cash — fresh, sellable inventory counts too, but stale stock counts for less and less.
- **Returns depend on supplier quality.** Customers return some of what they buy, and you refund them the full shelf price. The return rate is driven by the quality of the supplier the goods came from. The cheapest, lowest-quality suppliers are returned far more often (up to about 30% of units) than top-quality ones (as little as 2%). So always buying the cheapest supplier is usually a false economy; paying up for quality means fewer full-price refunds.
- **Everything is perishable.** Each item has a shelf life, typically a few weeks. Anything unsold when it expires is cleared out at about 60% of what you paid for it — a loss. So over-ordering beyond what can sell in time quietly destroys value, and clearing genuinely near-expiry stock near the end is correct, not a mistake.
- **Crowding a category cannibalizes it.** Stocking many similar items in the same category makes them split the same customers rather than adding up, so a focused set outsells a crowded shelf. When you raise the price on one item, some of its demand shifts to other active items in the same category, and vice versa. A lean, focused product set avoids this splitting and lets each item reach its full potential.
- **Prices matter, mildly.** Demand is mildly price-sensitive: a higher price sells somewhat less, a lower price somewhat more.
- **Shelf capacity is soft.** The 6,000-unit shelf limit is not a hard cap on ordering. Extra units wait in the back room and tie up cash until space frees up. Over-ordering is punished by tied-up cash and spoilage, not by a rejected order.
- **Deliveries take time.** Orders take several days to arrive, so reordering has to happen before shelves run empty.
- **Going broke ends the run.** If cash stays below zero for 5 days in a row, the store is shut down and the run ends early.
- **Customer reviews are on.** Quality slowly shapes demand over time as customers learn which products are reliable.

### The fixed setup

| Element | Value |
|---------|-------|
| Store | 15 |
| Length | 180 days (starting 09/07/91) |
| Starting cash | $5,000 |
| Daily rent | $120 |
| Shelf capacity | 6,000 units (soft) |
| Categories | Cheeses, Frozen Entrees, Snack Crackers, Soft Drinks |
| Customer reviews | On |
| News events | Off |

> The numbers cited throughout this document come from one reference run. They are ranges and properties to understand, not exact targets to hit.

## What a great run looks like

The reference run closed at **$25,082.93** in net worth — five times the opening cash — after completing all 180 days. At the close, about $20,000 was in cash and the rest was lean, sellable inventory. The run dipped briefly into the red in the opening days, recovered quickly, and climbed steadily through the full horizon. A run that falls short of about $20,000 has left significant value on the table.

## How a strong operator plays it, step by step

This is one good way to run the store, not a fixed recipe.

**Opening (days 1–10).** The problem is to fix the unrealistic opening prices, stock the shelves with a focused product set, and survive the opening cash crunch. A strong operator reads the catalog to understand the categories and supplier landscape, picks a lean set of about 8–12 items spread across the four categories, chooses suppliers balancing cost and quality to limit returns, sets realistic shelf prices that can sustain demand, and places opening orders sized to fill the shelves without over-ordering. Cash dips into the red briefly — the reference hit a low of about negative $130 on day 4 — but recovers within a week as sales begin. The operator does not waste turns re-reading unchanging catalog data or fiddling with prices that are already sound.

**Steady state (days 11–160).** The problem is to keep shelves stocked, prices stable, and inventory fresh while the net worth climbs. A strong operator checks inventory and sales each day, reorders items running low a few days before they would stock out, sizes orders to what can sell within shelf life, and leaves prices alone unless a durable signal (a sustained sales change, a quality shift from reviews, or a persistent stockout) calls for adjustment. The reference run placed about 2 orders per day on average, kept prices stable about 90% of the time, and grew net worth by roughly $140 per day through the middle stretch. Stockouts happen occasionally — the reference had stockouts on about 33 days — but a strong operator handles them calmly by reordering promptly and not fire-selling or abandoning the item. The operator does not chase one-day sales blips with price changes, does not crowd the shelves with redundant items that cannibalize each other, and does not over-order perishables that will spoil before selling.

**Ending (days 161–180).** The problem is to close out cleanly without destroying value. A strong operator keeps the store running normally, does not fire-sale the inventory, and clears only genuinely near-expiry stock in the final days. The reference closed with about $5,000 in lean, sellable inventory — not zero, not bloated. The operator does not stop ordering early and let shelves go empty, and does not dump good stock at a loss.

## What a good run has to get right

A good run must satisfy these properties:

1. Survive the full 180-day horizon without going broke (cash below zero for 5 consecutive days).
2. End near or above the reference band of about $20,000 in net worth.
3. Fix the unrealistic opening prices before selling begins, setting shelf prices that can sustain demand.
4. Stock the shelves with a focused product set before advancing through the opening days.
5. Keep a focused product set throughout — about 8–12 active items spread across the four categories — to avoid cannibalizing demand within each category.
6. Price on durable signals, not one-day blips; a sound price can stay put for weeks if sales are steady.
7. Choose suppliers balancing cost and quality to limit returns; the cheapest supplier is rarely the best value when returns run high.
8. Reorder ahead of stockouts, accounting for the several-day delivery lag.
9. Size orders to shelf life so stock sells before it spoils; over-ordering perishables quietly destroys value.
10. Handle stockouts calmly by reordering promptly, not by fire-selling or abandoning the item.
11. Close out cleanly with lean, sellable inventory; no endgame fire-sale of good stock.
12. Ground decisions in data actually read from the tools; do not invent facts or ignore what the store reports.
13. Do not waste turns re-reading unchanging catalog data or confirming prices that are already sound.
14. Do not crowd the shelves with many similar items in the same category; a lean set outsells a crowded one.

## How runs fail

Runs fail in characteristic ways:

- **Ignoring supplier quality and always buying the cheapest.** This floods the store with high-return goods, and refunding customers the full shelf price on 20–30% of sales quietly bleeds cash. A strong run pays up for quality.
- **Crowding the categories with too many similar items.** Stocking a dozen soft drinks or crackers makes them split the same customers, and total sales fall short of what a focused set would achieve. A strong run keeps the product set lean.
- **Chasing one-day sales blips with price changes.** Tweaking prices every day on noisy signals wastes turns and destabilizes demand. A strong run leaves sound prices alone.
- **Over-ordering perishables beyond what can sell in time.** The excess spoils or is cleared at a loss, destroying value silently. A strong run sizes orders to shelf life.
- **Reordering too late and letting stockouts linger.** Missing sales for days on end leaves money on the table. A strong run reorders ahead of the delivery lag.
- **Fire-selling good inventory in the endgame.** Dumping sellable stock at a loss to "clean up" destroys value. A strong run closes with lean, sellable inventory.
- **Wasting turns re-reading unchanging data.** Reading the catalog or confirming stable prices every day burns turns that could be spent on real decisions. A strong run reads data once and acts on it.
- **Letting cash stay negative for 5 days in a row.** This ends the run early and forfeits the full horizon. A strong run survives the opening dip and recovers quickly.

A strong run avoids all of these.

## The bottom line

The reference run closed at **$25,082.93** in net worth after completing all 180 days, with about $20,000 in cash and the rest in lean, sellable inventory. A run that falls short of about $20,000 has left significant value on the table.

---

*This file describes the task and what a good run looks like. The checks used to score a run live in separate files and are not part of this document. A different, equally sound approach reaching the same kind of result is just as good.*
