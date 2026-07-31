# Task truth: 730c53f1-be4c-5502-aa65-a5fd1b1918c0

This document describes the task, what a strong run looks like, and the properties a good run must satisfy. The scoring machinery that evaluates runs lives in separate files and is not part of this guide.

The walkthrough and numbers below come from one strong reference run. They show a bar to beat and one good way to play the store, but they are not the only way and not a script to copy. A sharper operator can beat these numbers, and several different approaches can all be good runs.

## The store you're running

You are running store 15 for 180 days starting September 7, 1991. You open with $30,000 in cash and pay $700 rent every day. The shelf can comfortably hold about 25,000 units, though you can order more — extra stock waits in the back room and ties up cash until space opens up. You stock twenty categories: Bathroom Tissues, Beer, Bottled Juices, Canned Soup, Canned Tuna, Cereals, Cheeses, Cigarettes, Cookies, Crackers, Dish Detergent, Fabric Softeners, Front-end Candies, Frozen Entrees, Frozen Juices, Oatmeal, Paper Towels, Snack Crackers, Soft Drinks, and Toothpastes.

How this store works:

- **Net worth is the score.** Your net worth is cash on hand plus the value of unsold stock you are holding plus any orders still in transit. Unsold stock is valued at what you paid for it, then written down steadily as its shelf life runs out, and counts as zero once it expires. In-transit orders count at their cost. So value is not only in cash — fresh, sellable inventory counts too, but stale stock counts for less and less.
- **Everything is perishable.** Each item has a shelf life, typically a few weeks. Anything unsold when it expires is cleared out at about sixty percent of what you paid for it — a loss. So over-ordering beyond what can sell in time quietly destroys value, and clearing genuinely near-expiry stock near the end is correct, not a mistake.
- **Returns depend on supplier quality.** Customers return some of what they buy, and you refund them the full shelf price. The return rate is driven by the quality of the supplier the goods came from. The cheapest, lowest-quality suppliers are returned far more often, up to about thirty percent of units, than top-quality ones, as little as two percent. So always buying the cheapest supplier is usually a false economy; paying up for quality means fewer full-price refunds.
- **Crowding a category cannibalizes it.** Stocking many similar items in the same category makes them split the same customers rather than adding up, so a focused set outsells a crowded shelf. When you raise the price on one item, some of its demand shifts to other active items in the same category, and when you lower a price, you pull some demand away from the others. A lean, well-chosen product set performs better than a sprawling one.
- **Prices matter, mildly.** Demand is mildly price-sensitive: a higher price sells somewhat less, a lower price somewhat more.
- **Shelf capacity is soft.** The shelf limit is not a hard cap on ordering. Extra units wait in the back room and tie up cash until space frees up. Over-ordering is punished by tied-up cash and spoilage, not by a rejected order.
- **Deliveries take time.** Orders take several days to arrive, so reordering has to happen before shelves run empty.
- **Reviews are on.** Customer reviews are enabled, so quality slowly shapes demand over time as customers learn which products are good.
- **Going broke ends the run.** If cash stays below zero for five days in a row, the store is shut down and the run ends early.

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

The reference run closed at **$80,834** net worth after the full 180 days, nearly 2.7 times the opening cash. About $66,871 was cash and the rest was fresh, sellable inventory still on the shelves. The run dipped sharply in the first few days as the operator stocked up, recovered quickly, and then climbed steadily through the full horizon. A run that falls short of about $70,000 has left significant value on the table.

## How a strong operator plays it, step by step

This is one good way to run the store, not a fixed recipe. A different sound approach reaching the same kind of result is just as good.

**Opening (days 1–5).** The problem is that the shelves are empty and the opening prices are unrealistic placeholders. A strong operator fixes the prices first — reading the market data and setting sensible shelf prices before any customer sees them — then stocks the shelves with a focused, quality-conscious product set. This means choosing one or two strong items per category, favoring suppliers with good quality-to-cost ratios to limit returns, and sizing the opening orders to fill the shelves without tying up too much cash in back-room overflow. The operator reads supplier quality and cost data, reads demand signals, places the opening orders, and advances a day or two to let deliveries arrive. Cash dips sharply during this phase — the reference run bottomed out around $340 on day 4 — but recovers quickly once sales begin. By day 5 or 6, the shelves are stocked, prices are sensible, and the store is open for business.

**Steady state (days 6–160).** The problem is to keep shelves stocked, prices stable, and the product set lean while the store grinds out daily profit. A strong operator settles into a daily rhythm: check for stockouts and reorder ahead of them, watch for items nearing expiry and clear them if needed, and adjust prices only when durable signals — sustained demand shifts or cost changes — call for it. The operator does not re-read unchanging supplier or product data every day, does not chase one-day sales blips, and does not crowd categories with too many similar items. The reference run placed about 1,580 orders across the full horizon, roughly nine per day, and kept prices stable — over ninety-two percent of price touches confirmed the existing price rather than changing it. Stockouts happened on about 104 days, which is normal and not a crisis; the operator handled them calmly by reordering and moving on. Net worth climbed steadily at about $360 per day through this phase, compounding the opening investment into a growing cushion.

**Ending (days 161–180).** The problem is to close out cleanly without destroying value. A strong operator keeps the store running normally through the final weeks — no fire-sale, no dumping good inventory, no stopping orders early and letting shelves go bare. Items genuinely nearing expiry are cleared at a modest discount, but fresh stock keeps selling at full price right up to the end. The reference run closed with about $14,000 in fresh, sellable inventory still on the shelves, which counted toward the terminal net worth. A panicked endgame sell-off would have destroyed that value.

## What a good run has to get right

A good run must satisfy these properties:

1. Survive the full 180-day horizon without going broke — cash must not stay below zero for five consecutive days.
2. End near or above the reference band of about $70,000 net worth, showing the operator compounded the opening cash effectively.
3. Fix the unrealistic opening prices before selling anything — read the market and set sensible shelf prices on day 1, not after customers have already seen placeholder numbers.
4. Stock the shelves before advancing past the opening days — place opening orders and let them arrive so the store is ready to sell.
5. Keep a focused product set — one or two strong items per category, not a sprawling shelf that cannibalizes itself.
6. Price on durable signals, not one-day blips — adjust prices when sustained demand shifts or cost changes call for it, not in reaction to normal daily noise.
7. Choose suppliers on quality-and-cost to limit returns — favor suppliers with good quality-to-cost ratios over the rock-bottom cheapest, because fewer returns mean fewer full-price refunds.
8. Reorder ahead of stockouts — deliveries take several days, so reorder before shelves run empty, not after.
9. Size orders to shelf life — order quantities that can sell before expiry, not so much that spoilage quietly destroys value.
10. Handle stockouts calmly — a stockout is a signal to reorder, not a crisis; the reference run had stockouts on over half the days and still performed well.
11. No endgame fire-sale — keep the store running normally through the final weeks; clear genuinely near-expiry stock, but do not dump fresh inventory or stop ordering early.
12. Ground decisions in data actually read — check supplier quality, read demand signals, and use that information to choose products and set prices.
13. Do not waste turns re-reading unchanging data — supplier catalogs and product attributes do not change day to day; read them once and move on.
14. Keep cash positive through the steady state — the opening dip is normal, but after that, cash should stay comfortably above zero except for brief reorder cycles.

## How runs fail

Runs fail in characteristic ways:

- **Selling at placeholder prices.** The operator advances without fixing the opening prices, so customers see unrealistic numbers and either do not buy or buy at prices that destroy value.
- **Crowding categories.** The operator stocks too many similar items in the same category, so they split the same customers and each sells less than a focused set would.
- **Chasing the cheapest supplier.** The operator always buys the lowest-cost supplier without checking quality, so return rates spike and full-price refunds eat into profit.
- **Over-ordering beyond shelf life.** The operator places large orders that cannot sell before expiry, so spoilage quietly destroys value and the terminal net worth is far below what the sales would suggest.
- **Reacting to daily noise.** The operator changes prices in response to one-day sales blips rather than durable signals, so prices whipsaw and customers see instability.
- **Letting stockouts linger.** The operator does not reorder ahead of stockouts, so shelves go empty for days and sales opportunities are lost.
- **Endgame panic.** The operator dumps fresh inventory or stops ordering in the final weeks, so the store closes with bare shelves and the terminal net worth is just cash, missing the value of sellable stock.
- **Re-reading static data.** The operator wastes turns re-reading supplier catalogs or product attributes every day, burning time that could be spent on decisions that matter.
- **Going broke early.** The operator runs out of cash and stays negative for five consecutive days, so the store is shut down and the run ends early.

A strong run avoids all of these.

## The bottom line

The reference run closed at **$80,834** net worth after 180 days, with about $66,871 in cash and the rest in fresh, sellable inventory. It dipped to around $340 on day 4 during the opening stock-up, recovered quickly, and climbed steadily at about $360 per day through the steady state. A run that falls short of about $70,000 has left significant value on the table.

---

*This document describes the task and what a good run looks like. The checks used to score a run live in separate files and are not part of this guide. A different, equally sound approach reaching the same kind of result is just as good.*
