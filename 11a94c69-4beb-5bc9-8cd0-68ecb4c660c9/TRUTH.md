# Task truth: 11a94c69-4beb-5bc9-8cd0-68ecb4c660c9

This document describes the task, what a strong run looks like, and the properties a good run must satisfy. The scoring machinery lives in separate files and is not part of this guide.

The walkthrough and numbers below come from one strong reference run. They show a bar to beat and one good way to play, not the only way and not a script to copy. A sharper operator can beat these numbers, and several different approaches can all be good.

## The store you're running

You are running store 15 for 180 days starting September 7, 1991. You open with $10,000 in cash and pay $250 rent every day. The shelf can hold about 10,000 units, though this is a soft limit — extra stock waits in the back room and ties up cash until space opens up. You stock five categories: Bathroom Tissues, Cheeses, Frozen Entrees, Snack Crackers, and Soft Drinks.

How this store works:

- **Net worth is the score.** Your net worth is cash on hand plus the value of unsold stock you are holding plus any orders still in transit. Unsold stock is valued at what you paid for it, then written down steadily as its shelf life runs out, and counts as zero once it expires. In-transit orders count at their cost. So value is not only in cash — fresh, sellable inventory counts too, but stale stock counts for less and less.
- **Returns depend on supplier quality.** Customers return some of what they buy, and you refund them the full shelf price. The return rate is driven by the quality of the supplier the goods came from. The cheapest, lowest-quality suppliers are returned far more often (up to about 30% of units) than top-quality ones (as little as 2%). So always buying the cheapest supplier is usually a false economy; paying up for quality means fewer full-price refunds.
- **Everything is perishable.** Each item has a shelf life, typically a few weeks. Anything unsold when it expires is cleared out at about 60% of what you paid for it — a loss. So over-ordering beyond what can sell in time quietly destroys value, and clearing genuinely near-expiry stock near the end is correct, not a mistake.
- **Crowding a category cannibalizes it.** Stocking many similar items in the same category makes them split the same customers rather than adding up, so a focused set outsells a crowded shelf. When you add another product to a category that already has several, the new one takes sales from the existing ones more than it brings in fresh demand.
- **Prices matter, mildly.** Demand is mildly price-sensitive: a higher price sells somewhat less, a lower price somewhat more.
- **Shelf capacity is soft.** The 10,000-unit shelf limit is not a hard cap on ordering. Extra units wait in the back room and tie up cash until space frees up. Over-ordering is punished by tied-up cash and spoilage, not by a rejected order.
- **Deliveries take time.** Orders take several days to arrive, so reordering has to happen before shelves run empty.
- **Going broke ends the run.** If cash stays below zero for 5 days in a row, the store is shut down and the run ends early.
- **Customer reviews are on.** Quality slowly shapes demand over time as customers learn which products are reliable.

### The fixed setup

| **Store**            | 15                                      |
|----------------------|-----------------------------------------|
| **Length**           | 180 days (starting 09/07/91)            |
| **Starting cash**    | $10,000                                 |
| **Daily rent**       | $250                                    |
| **Shelf capacity**   | 10,000 units (soft limit)               |
| **Categories**       | Bathroom Tissues, Cheeses, Frozen Entrees, Snack Crackers, Soft Drinks |
| **Customer reviews** | On                                      |
| **News events**      | Off                                     |

> The numbers cited below come from one reference run and are ranges or properties to understand, not exact targets to hit.

## What a great run looks like

The reference run closed at **$25,720** net worth after the full 180 days, about 2.6 times the opening cash. Cash at the close was about $19,000, with roughly $6,700 in fresh, sellable inventory still on hand. The run dipped briefly into the red in the first few days (bottoming around negative $100 on day 3), recovered quickly, and then climbed steadily at about $120 per day through the middle and late stages. A run that falls short of about $22,000 has left significant value on the table.

## How a strong operator plays it, step by step

This is one good way to run the store, not a fixed recipe. A strong operator solves three problems in sequence: getting the opening right, running the daily loop well, and closing cleanly.

**Opening (days 1–10).** The problem is that the opening catalog prices are unrealistic placeholders, and the shelves are empty. A strong operator reads the catalog on day one, fixes every price to a sensible market level before any sales happen, and places the first wave of orders to stock all five categories with a focused set of products — perhaps two to four items per category, chosen for a good balance of supplier quality and cost. The reference run placed about 20–30 orders in the first few days and confirmed about 50–60 prices, keeping most of them at their opening levels because they were already reasonable. Cash dips into the red briefly as the first orders arrive and rent keeps coming, but recovers within a week as sales start flowing. By day 10, shelves are stocked, prices are set, and the daily rhythm begins.

**Steady state (days 11–160).** The problem is keeping shelves full, prices stable, and cash growing without over-ordering or crowding the categories. A strong operator checks stock levels and sales velocity every day, reorders a few items that are running low (the reference run averaged about two orders per day), and leaves prices alone unless a durable signal — a sustained sales trend or a quality shift from reviews — calls for a change. The reference run confirmed the existing price on about 93% of the touches it made, adjusting only when the data clearly justified it. The operator keeps the product set focused, avoids adding redundant items that would cannibalize each other, and chooses suppliers that balance cost and quality to keep return rates manageable. Orders are sized to what can sell before expiry, and deliveries are timed so stock arrives before a stockout happens. The reference run had stockouts on about 40 days across the full 180, handling them calmly by reordering and moving on. Net worth climbs steadily, and cash stays comfortably positive after the opening recovery.

**Ending (days 161–180).** The problem is closing with value intact, not trapped in unsellable stock. A strong operator keeps ordering and selling normally through the final weeks, lets inventory run down naturally as the horizon approaches, and does not fire-sale fresh stock just because the end is near. The reference run closed with about $6,700 in inventory still on hand — lean, but still selling — and about $19,000 in cash. Clearing genuinely near-expiry stock in the last few days is correct; dumping everything at a loss is not.

## What a good run has to get right

A good run must satisfy these properties, in its own way:

1. Survive the full 180 days without going broke — cash must not stay below zero for 5 consecutive days.
2. End near or above the reference band of about $22,000 to $26,000 in net worth.
3. Fix the unrealistic opening catalog prices to sensible market levels before any significant sales happen.
4. Stock shelves with a focused product set across all five categories before advancing past the opening phase.
5. Keep the product set focused — avoid crowding categories with many similar items that cannibalize each other.
6. Price on durable signals, not one-day blips — most price touches should confirm the existing price unless a sustained trend or quality shift justifies a change.
7. Choose suppliers on a balance of quality and cost to limit return rates — always buying the cheapest supplier usually backfires.
8. Reorder ahead of stockouts so deliveries arrive before shelves run empty, given that orders take several days.
9. Size orders to what can sell before expiry — over-ordering beyond shelf life quietly destroys value through spoilage.
10. Handle stockouts calmly when they happen — reorder and move on, rather than panic or abandon the product.
11. Avoid an endgame fire-sale — keep ordering and selling normally through the final weeks, and close with lean but still-sellable inventory.
12. Ground decisions in data actually read from the tools — prices, stock levels, sales velocity, supplier quality, and review trends.
13. Do not waste turns re-reading unchanging data — the catalog does not change day to day, and most prices stay stable once set.
14. Keep cash positive after the opening dip — the brief red in the first few days is normal, but staying broke punishes growth.

## How runs fail

Runs fail in characteristic ways, and each destroys a different part of the outcome:

- **Selling at the unrealistic opening prices** — customers will not buy, or you give away value, and the opening phase stalls.
- **Leaving shelves empty for days** — no sales means no cash flow, and rent keeps draining value.
- **Crowding categories with too many similar items** — they cannibalize each other and total sales fall rather than rise.
- **Chasing every one-day sales blip with a price change** — prices thrash, customers lose trust, and you waste turns on noise.
- **Always buying the cheapest supplier** — return rates spike, you refund full shelf price on 30% of sales, and cash bleeds out.
- **Reordering only after a stockout** — deliveries take days, so the shelf stays empty and you lose a week of sales.
- **Over-ordering beyond what can sell before expiry** — stock spoils, you clear it at 60% of cost, and value quietly vanishes.
- **Panicking at a stockout and abandoning the product** — you lose a steady seller and shrink the revenue base.
- **Fire-selling fresh stock in the final weeks** — you turn sellable inventory into cash at a loss and leave money on the table.
- **Making decisions without reading the data** — you guess at stock levels, miss supplier quality signals, and order blindly.
- **Re-reading the catalog every day** — you waste turns on data that does not change and slow the daily loop.
- **Staying broke after the opening** — cash below zero for 5 days ends the run early, and you never reach the growth phase.

A strong run avoids all of these.

## The bottom line

The reference run closed at **$25,720** net worth after 180 days, with about $19,000 in cash and roughly $6,700 in lean, still-selling inventory. It dipped briefly into the red in the opening days, recovered quickly, and climbed steadily through the middle and late stages. A run that falls short of about $22,000 has left significant value on the table.

---

*This file describes the task and what a good run looks like. The checks used to score a run live in separate files and are not part of this document. A different, equally sound approach reaching the same kind of result is just as good.*
