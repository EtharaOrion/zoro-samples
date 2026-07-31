# Task truth: f8ab5919-929c-53a1-a307-90cdfa1644a2

This document is a plain-language guide to the task, what a strong run looks like, and the properties a good run must satisfy. The scoring machinery lives in separate files and is not part of this document.

The walkthrough and numbers below come from one strong reference run. They show a bar to beat and one good way to play the store, not the only way and not a script to copy. A sharper operator can beat these numbers, and several different approaches can all be good.

## The store you're running

You're running store 15 for 180 days starting September 7, 1991. You open with $30,000 in cash and pay $700 rent every day. The shelf holds up to 25,000 units, though that's a soft limit — extra stock waits in the back room and ties up cash until space frees up. You stock twenty categories: Bathroom Tissues, Beer, Bottled Juices, Canned Soup, Canned Tuna, Cereals, Cheeses, Cigarettes, Cookies, Crackers, Dish Detergent, Fabric Softeners, Front-end Candies, Frozen Entrees, Frozen Juices, Oatmeal, Paper Towels, Snack Crackers, Soft Drinks, and Toothpastes.

**How this store works:**

- **Net worth is the score.** Net worth equals cash on hand plus the value of unsold stock you're holding plus any orders still in transit. Unsold stock is valued at what you paid for it, then written down steadily as its shelf life runs out, and counts as zero once it expires. In-transit orders count at their cost. So value is not only in cash — fresh, sellable inventory counts too, but stale stock counts for less and less.
- **Returns depend on supplier quality.** Customers return some of what they buy, and you refund them the full shelf price. The return rate is driven by the quality of the supplier the goods came from. The cheapest, lowest-quality suppliers are returned far more often (up to about 30% of units) than top-quality ones (as little as 2%). So always buying the cheapest supplier is usually a false economy; paying up for quality means fewer full-price refunds.
- **Everything is perishable.** Each item has a shelf life, typically a few weeks. Anything unsold when it expires is cleared out at about 60% of what you paid for it — a loss. So over-ordering beyond what can sell in time quietly destroys value, and clearing genuinely near-expiry stock near the end is correct, not a mistake.
- **Crowding a category cannibalizes it.** Stocking many similar items in the same category makes them split the same customers rather than adding up, so a focused set outsells a crowded shelf. When you raise the price on one item, some of its demand shifts to other active items in the same category, and vice versa. This is not price sensitivity — it's the way similar products compete for the same shoppers.
- **Prices matter, mildly.** Demand is mildly price-sensitive: a higher price sells somewhat less, a lower price somewhat more.
- **Shelf capacity is soft.** The 25,000-unit shelf limit is not a hard cap on ordering. Extra units wait in the back room and tie up cash until space frees up. Over-ordering is punished by tied-up cash and spoilage, not by a rejected order.
- **Deliveries take time.** Orders take several days to arrive, so reordering has to happen before shelves run empty.
- **Going broke ends the run.** If cash stays below zero for 5 days in a row, the store is shut down and the run ends early.
- **Customer reviews are on.** Quality slowly shapes demand over time as customers learn which products are good.
- **News events are on.** External events can shift demand during the run.

### The fixed setup

| **Store** | 15 |
| **Length** | 180 days (starting 09/07/91) |
| **Starting cash** | $30,000 |
| **Daily rent** | $700 |
| **Shelf capacity** | 25,000 units (soft limit) |
| **Categories** | 20 (Bathroom Tissues, Beer, Bottled Juices, Canned Soup, Canned Tuna, Cereals, Cheeses, Cigarettes, Cookies, Crackers, Dish Detergent, Fabric Softeners, Front-end Candies, Frozen Entrees, Frozen Juices, Oatmeal, Paper Towels, Snack Crackers, Soft Drinks, Toothpastes) |
| **Customer reviews** | On |
| **News events** | On |

> The numbers cited below come from one reference run. They are ranges and properties to understand, not exact targets to hit.

## What a great run looks like

The reference run closed at **$93,850** net worth after the full 180 days, more than tripling the opening $30,000. Cash at the close was about $86,500, with the rest in lean, sellable inventory. The run dipped briefly into the red in the first few days, recovered quickly, and then climbed steadily at roughly $550 per day through the middle and late stages. A run that falls short of about $75,000 has left significant value on the table.

## How a strong operator plays it, step by step

This is one good way to play the store, not a fixed recipe.

**Opening (days 1–5).** The store starts with placeholder prices that are often wildly unrealistic — some items priced at pennies, others at hundreds of dollars. The first job is to fix those prices before selling anything, using the cost and competitor data to set sensible shelf prices. Then stock the shelves with a focused product set, choosing suppliers on a balance of quality and cost to limit returns. The reference run placed about 6 orders per day on average across the full 180 days, so the opening burst is heavier to get shelves filled. Cash dips briefly into the red (the reference hit about −$84 on day 4) as opening orders arrive and rent accrues, but recovers within a few days as sales begin.

**Steady state (days 6–160).** The daily loop is to check what sold, what's running low, and what's expiring soon, then reorder ahead of stockouts and adjust prices on durable signals, not one-day blips. A strong operator keeps a focused product set — not every SKU in every category, because crowding a category makes the items split the same customers. The reference run kept about 90% of price touches unchanged, meaning most prices were set once and left alone unless something real changed. Stockouts happen (the reference had stockouts on about 80 days), and the right response is to reorder calmly, not to panic or abandon the item. Orders are sized to shelf life so stock sells before it expires. Net worth climbs steadily as cash and fresh inventory accumulate; the reference grew at about $550 per day through this phase.

**Ending (days 161–180).** As the horizon approaches, the operator stops ordering items that won't sell in time and lets inventory run down naturally. The reference closed with about $86,500 in cash and the rest in lean, sellable stock — not a fire-sale clearance, just a controlled wind-down. The run completes the full 180 days without going broke.

## What a good run has to get right

A good run satisfies these properties:

1. Survives the full 180-day horizon without going broke (cash below zero for 5 consecutive days).
2. Ends near or above the reference band of roughly $75,000 to $95,000 net worth.
3. Fixes the unrealistic opening prices before selling, using cost and competitor data to set sensible shelf prices.
4. Stocks shelves before advancing through the opening days, so the store has something to sell.
5. Keeps a focused product set, not every SKU in every category, because crowding a category makes items split the same customers rather than adding up.
6. Prices on durable signals, not one-day blips — most prices are set once and left alone unless something real changes (the reference kept about 90% of price touches unchanged).
7. Chooses suppliers on a balance of quality and cost to limit returns, not always the cheapest option, because low-quality suppliers are returned far more often and you refund the full shelf price.
8. Reorders ahead of stockouts, since deliveries take several days to arrive.
9. Sizes orders to shelf life so stock sells before it expires, avoiding the quiet destruction of value from spoilage.
10. Handles stockouts calmly by reordering, not by abandoning the item or panicking.
11. Winds down inventory naturally near the end, not with a fire-sale clearance, so the close is lean but still selling.
12. Grounds decisions in data actually read from the tools, not guesses or stale information.
13. Does not waste turns re-reading unchanging data like the full product catalog or competitor prices that were just checked.

## How runs fail

Runs fail in characteristic ways:

- **Selling at placeholder prices.** The operator advances without fixing the unrealistic opening prices, selling items at pennies or hundreds of dollars and destroying value immediately.
- **Advancing with empty shelves.** The operator skips the opening stocking phase and advances through days with nothing to sell, losing the early revenue that funds the rest of the run.
- **Crowding categories.** The operator stocks every SKU in every category, making them split the same customers and underperform a focused set.
- **Chasing noise.** The operator changes prices daily on one-day sales blips, thrashing instead of letting durable prices do their work.
- **Always buying the cheapest supplier.** The operator ignores quality and buys the lowest-cost option every time, then refunds full shelf price on the high return rate and loses money on every sale.
- **Reordering too late.** The operator waits until shelves are empty to reorder, then loses days of sales while deliveries are in transit.
- **Over-ordering perishables.** The operator orders more than can sell before expiry, tying up cash in stock that spoils and is cleared at a loss.
- **Abandoning stockouts.** The operator treats a stockout as a permanent failure and stops reordering the item, leaving a hole in the product set.
- **Fire-sale ending.** The operator slashes prices to zero in the final days to clear inventory, destroying value instead of winding down naturally.
- **Going broke.** The operator runs cash below zero for 5 consecutive days and the store is shut down early, ending the run with whatever net worth was left.

A strong run avoids all of these.

## The bottom line

The reference run closed at $93,850 net worth after the full 180 days, with about $86,500 in cash and the rest in lean, sellable inventory. It dipped briefly into the red in the opening days, recovered quickly, and climbed steadily at roughly $550 per day through the middle and late stages. A run that falls short of about $75,000 has left significant value on the table.

---

*This file describes the task and what a good run looks like. The checks used to score a run live in separate files and are not part of this document. A different, equally sound approach reaching the same kind of result is just as good.*
