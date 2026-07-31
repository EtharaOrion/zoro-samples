# Task truth: 48df3c8b-f46f-50e6-983e-d583fda86fa2

This document describes what the task is, how a strong operator runs it, what a good result looks like, and the ways a run goes wrong. The scoring machinery that grades a run lives in separate files and is not part of this guide.

The walkthrough and numbers below come from one strong reference run. They show one good way to play the store and set a bar to beat, but they are not the only way and not a script to copy. A sharper operator can beat these numbers, and several different sound approaches can all reach a good result.

## The store you're running

You are running store 15 for 180 days starting September 7, 1991. You open with $5000 in cash and pay $120 rent every day. The shelf can hold about 6000 units, though this is a soft limit — extra stock waits in the back room and ties up cash until space frees up. You sell four categories: Cheeses, Frozen Entrees, Snack Crackers, and Soft Drinks.

Here is how this store works:

- **Net worth is the score.** Your net worth is cash on hand plus the value of unsold stock you are holding plus any orders still in transit. Unsold stock is valued at what you paid for it, then written down steadily as its shelf life runs out, and counts as zero once it expires. In-transit orders count at their cost. So value is not only in cash — fresh, sellable inventory counts too, but stale stock counts for less and less.
- **Returns depend on supplier quality.** Customers return some of what they buy, and you refund them the full shelf price. The return rate is driven by the quality of the supplier the goods came from. The cheapest, lowest-quality suppliers are returned far more often (up to about 30% of units) than top-quality ones (as little as 2%). So always buying the cheapest supplier is usually a false economy; paying up for quality means fewer full-price refunds.
- **Everything is perishable.** Each item has a shelf life, typically a few weeks. Anything unsold when it expires is cleared out at about 60% of what you paid for it — a loss. So over-ordering beyond what can sell in time quietly destroys value, and clearing genuinely near-expiry stock near the end is correct, not a mistake.
- **Crowding a category cannibalizes it.** Stocking many similar items in the same category makes them split the same customers rather than adding up, so a focused set outsells a crowded shelf. When you raise the price on one item, some of its demand shifts to other active items in the same category, and when you lower a price, you pull some demand away from the others. A lean, focused product set avoids this splitting.
- **Prices matter, mildly.** Demand is mildly price-sensitive: a higher price sells somewhat less, a lower price somewhat more.
- **Shelf capacity is soft.** The 6000-unit shelf limit is not a hard cap on ordering. Extra units wait in the back room and tie up cash until space frees up. Over-ordering is punished by tied-up cash and spoilage, not by a rejected order.
- **Deliveries take time.** Orders take several days to arrive, so reordering has to happen before shelves run empty.
- **Going broke ends the run.** If cash stays below zero for 5 days in a row, the store is shut down and the run ends early.
- **Customer reviews are on.** Quality slowly shapes demand over time as customers learn which products are good.

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

The reference run closed at **$31557** net worth after the full 180 days, more than six times the opening cash. About $26700 was cash and the rest was lean, sellable inventory. The run dipped briefly into the red in the first few days while the opening orders arrived, then recovered and climbed steadily through the horizon. A run that falls short of about $25000 has left significant value on the table.

## How a strong operator plays it, step by step

This is one good way to run the store, not a fixed recipe.

**Opening (days 1–5).** The problem is to fix the unrealistic opening prices, stock the shelves with a focused product set, and survive the cash dip while the first orders arrive. A strong operator reads the catalog to see what is available, picks a lean set of items across the four categories (avoiding a crowded shelf in any one category), chooses suppliers balancing cost and quality to limit returns, sets realistic prices based on cost and the market, and places opening orders sized to fill the shelves without tying up too much cash in any one item. The run dips into the red briefly (the reference hit about negative $50 on day 3) as rent eats cash before goods arrive and sell, then recovers as sales begin. The operator does not panic at the dip — it is expected and short-lived.

**Steady state (days 6–160).** The problem is to keep shelves stocked, prices stable, and net worth climbing without waste. A strong operator checks inventory and sales each day, reorders items that are running low (ahead of stockouts, since deliveries take days), and adjusts prices only when durable signals justify it — not on one-day blips. The reference run placed about 375 orders across the horizon (roughly two per day) and kept most prices stable (over 90% of price touches confirmed the existing price). Stockouts happen occasionally (the reference had stockouts on about 35 days) but are handled calmly by reordering promptly, not by over-ordering everything in fear. Orders are sized to shelf life so stock sells before it spoils, and the product set stays focused so categories do not cannibalize themselves. Net worth climbs steadily; the reference grew at about $170 per day through this phase.

**Ending (days 161–180).** The problem is to close out cleanly without a fire-sale or a pile of unsold stock. A strong operator stops placing large orders as the horizon approaches, lets inventory run down naturally, and clears genuinely near-expiry stock at a reasonable discount if needed. The reference closed with about $4800 in inventory, all of it fresh and sellable — not zero, not a mountain. There is no endgame panic or steep discounting of good stock.

## What a good run has to get right

A good run must satisfy these properties:

1. Survive the full 180-day horizon without going broke (cash below zero for 5 consecutive days).
2. End with net worth near or above the reference band of about $25000, showing the store was run profitably.
3. Fix the unrealistic opening prices before selling, so the store opens with a sensible price list.
4. Stock the shelves with a focused product set before advancing through the days, so there is something to sell from the start.
5. Keep the product set lean and focused within each category, avoiding a crowded shelf that splits demand and cannibalizes sales.
6. Adjust prices on durable signals, not one-day noise, so pricing is stable and grounded in real trends.
7. Choose suppliers balancing cost and quality to limit returns, not always picking the cheapest and eating 30% return rates.
8. Reorder ahead of stockouts, since deliveries take days, so shelves do not sit empty for long stretches.
9. Size orders to shelf life so stock sells before it spoils, not over-ordering and watching value evaporate as goods expire.
10. Handle occasional stockouts calmly by reordering promptly, not by over-ordering everything in fear and tying up cash.
11. Close out the run cleanly without a fire-sale, ending with lean, sellable inventory rather than a pile of unsold or expired stock.
12. Ground decisions in data actually read from the tools, not guesses or stale information.
13. Avoid wasting turns re-reading unchanging data like the catalog or the full price list when a targeted check would do.

## How runs fail

Here are the characteristic ways a run goes wrong:

- **Panicking at the opening cash dip and freezing.** The operator sees cash go negative in the first few days, thinks the run is doomed, and stops ordering or makes wild changes. This wastes the recovery phase and leaves shelves empty. A strong run expects the dip and rides it out.
- **Crowding the shelf with too many similar items.** The operator stocks a dozen items in one category, thinking more is better. They split the same customers and cannibalize each other, so total sales are lower than a focused set would achieve.
- **Always buying the cheapest supplier.** The operator chases the lowest cost and ignores quality. Return rates hit 30%, refunds eat the margin, and net worth stagnates.
- **Over-ordering in fear of stockouts.** The operator orders huge quantities of everything to avoid ever running out. Cash is tied up in excess stock, much of it spoils before it sells, and net worth grows slowly or not at all.
- **Chasing one-day price blips.** The operator adjusts prices every day based on tiny demand shifts. Prices thrash, customers see instability, and the operator wastes time on noise instead of managing inventory.
- **Ignoring shelf life.** The operator orders without checking how long goods last. Stock expires on the shelf, is cleared at a loss, and value evaporates.
- **Fire-sale at the end.** The operator panics as the horizon approaches and slashes prices on all stock, even fresh goods. This destroys value that could have been preserved as inventory.
- **Running on stale data.** The operator makes decisions without reading current inventory or sales, guessing or using day-old information. Orders are mistimed, stockouts drag on, and the run drifts.
- **Re-reading the catalog every day.** The operator wastes turns checking unchanging data instead of managing the live store. Time runs out before the work is done.

A strong run avoids all of these.

## The bottom line

The reference run closed at $31557 net worth after 180 days, with about $26700 in cash and $4800 in lean, sellable inventory. A run that falls short of about $25000 has missed significant value.

---

*This document describes the task and what a good run looks like. The checks used to score a run live in separate files and are not part of this guide. A different, equally sound approach reaching the same kind of result is just as good.*
