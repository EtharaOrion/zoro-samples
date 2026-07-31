# Task truth: f9b64d40-1277-546a-b1a6-567c3370c498

This document describes what the task is, how a strong operator runs it, and what a good result looks like. The scoring machinery that evaluates a run lives in separate files and is not part of this guide.

The walkthrough and numbers below come from one strong reference run. They show one good way to play the task and set a bar to beat, but they are not the only way and not a script to copy. A sharper operator can beat these numbers, and several different approaches can all be good.

## The store you're running

You are running store 15 for 180 days, starting September 7, 1991. You open with $30,000 in cash and pay $700 rent every day. The shelf can hold about 25,000 units, though this is a soft limit — extra stock waits in the back room and ties up cash until space opens. You stock twenty categories: Bathroom Tissues, Beer, Bottled Juices, Canned Soup, Canned Tuna, Cereals, Cheeses, Cigarettes, Cookies, Crackers, Dish Detergent, Fabric Softeners, Front-end Candies, Frozen Entrees, Frozen Juices, Oatmeal, Paper Towels, Snack Crackers, Soft Drinks, and Toothpastes.

**How this store works:**

- **Net worth is the score.** Net worth equals cash on hand plus the value of unsold stock plus any orders still in transit. Unsold stock is valued at what you paid for it, then written down steadily as its shelf life runs out, and counts as zero once it expires. In-transit orders count at their cost. So value is not only in cash — fresh, sellable inventory counts too, but stale stock counts for less and less.
- **Returns depend on supplier quality.** Customers return some of what they buy, and the store refunds them the full shelf price. The return rate is driven by the quality of the supplier the goods came from. The cheapest, lowest-quality suppliers are returned far more often (up to about 30% of units) than top-quality ones (as little as 2%). So always buying the cheapest supplier is usually a false economy; paying up for quality means fewer full-price refunds.
- **Everything is perishable.** Each item has a shelf life, typically a few weeks. Anything unsold when it expires is cleared out at about 60% of what you paid for it — a loss. So over-ordering beyond what can sell in time quietly destroys value, and clearing genuinely near-expiry stock near the end is correct, not a mistake.
- **Crowding a category cannibalizes it.** Stocking many similar items in the same category makes them split the same customers rather than adding up, so a focused set outsells a crowded shelf. When you raise the price on one item, some of its demand shifts to other active items in the same category, and vice versa. A lean product set in each category performs better than a sprawling one.
- **Prices matter, mildly.** Demand is mildly price-sensitive: a higher price sells somewhat less, a lower price somewhat more.
- **Shelf capacity is soft.** The shelf limit is not a hard cap on ordering. Extra units wait in the back room and tie up cash until space frees up. Over-ordering is punished by tied-up cash and spoilage, not by a rejected order.
- **Deliveries take time.** Orders take several days to arrive, so reordering has to happen before shelves run empty.
- **Going broke ends the run.** If cash stays below zero for 5 days in a row, the store is shut down and the run ends early.
- **Customer reviews are on.** Quality slowly shapes demand over time as customers learn which products are reliable.

### The fixed setup

| **Store** | 15 |
| **Length** | 180 days (starting 09/07/91) |
| **Starting cash** | $30,000 |
| **Daily rent** | $700 |
| **Shelf capacity** | 25,000 units (soft) |
| **Categories** | 20 (Bathroom Tissues, Beer, Bottled Juices, Canned Soup, Canned Tuna, Cereals, Cheeses, Cigarettes, Cookies, Crackers, Dish Detergent, Fabric Softeners, Front-end Candies, Frozen Entrees, Frozen Juices, Oatmeal, Paper Towels, Snack Crackers, Soft Drinks, Toothpastes) |
| **Customer reviews** | On |
| **News events** | Off |

> The numbers cited below come from one reference run. They are ranges and properties to understand, not exact targets to hit.

## What a great run looks like

A strong run finishes the full 180 days with a terminal net worth around **$102,300** — more than triple the opening cash. The reference run completed all 180 days and closed with about $85,900 in cash and the rest in lean, sellable inventory. Net worth dips sharply in the opening days as the operator stocks the shelves, recovers within the first week, then climbs steadily at roughly $480 per day through the middle and late phases. A run that falls short of about $90,000 has left significant value on the table.

## How a strong operator plays it, step by step

This is one good way to run the store, not a fixed recipe. A different sound approach reaching the same kind of result is just as good.

**Opening (days 1–7): Stock the shelves and fix the prices.** The store opens with empty shelves and unrealistic placeholder prices on every item. A strong operator reads the catalog to see what is available, chooses a focused set of items in each category (typically two to four per category, avoiding crowding), fixes the prices to sensible shelf levels before any sales happen, and places opening orders sized to fill the shelves without tying up too much cash. The operator picks suppliers balancing cost and quality — not always the cheapest, because low quality means high returns and lost margin. Orders take a few days to arrive, so the operator advances time carefully to let stock land and sales begin. Cash dips sharply during this phase (the reference run bottomed at about $270 on day 4) as orders are paid for, then recovers as sales start and deliveries complete. By the end of the first week, shelves are stocked, prices are grounded, and net worth is climbing.

**Steady state (days 8–160): Run the daily loop and grow net worth.** Each day, the operator checks what sold, what is running low, and what needs reordering. The operator places orders ahead of stockouts (the reference run averaged about nine orders per day and saw stockouts on roughly 100 days, handled calmly by reordering promptly). Prices are touched frequently to confirm they remain sound, but most touches keep the existing price (the reference run confirmed the price on about 94% of touches) because demand and cost are stable and one-day sales blips are noise, not signals. The operator sizes orders to shelf life — enough to meet demand before expiry, not so much that stock spoils. The operator keeps the product set lean and focused, avoiding the temptation to add many similar items that would cannibalize each other. Net worth climbs steadily, driven by daily sales margin minus rent and the occasional spoilage or return loss. The reference run grew net worth at roughly $480 per day through this phase.

**Ending (days 161–180): Close out cleanly without a fire sale.** As the horizon approaches, the operator stops placing long-lead orders that would arrive after the close and lets inventory run down naturally through sales. The operator does not slash prices or dump stock at a loss — genuinely near-expiry items are cleared at the usual markdown, but most inventory sells at full margin right up to the end. The reference run closed with about $85,900 in cash and the rest in lean, sellable stock, having completed all 180 days without going broke.

## What a good run has to get right

A good run satisfies these properties, in its own way:

1. Survives the full 180-day horizon without going broke (cash below zero for 5 consecutive days).
2. Ends with net worth near or above the reference band of roughly $90,000 to $105,000.
3. Fixes the unrealistic opening prices to sensible shelf levels before selling begins, grounding them in catalog cost and reasonable margin.
4. Stocks the shelves with opening orders before advancing time, so sales can start promptly.
5. Keeps a focused product set in each category, avoiding the cannibalization that comes from crowding the shelf with many similar items.
6. Prices on durable signals like cost and steady demand, not on one-day sales blips or noise.
7. Chooses suppliers balancing cost and quality to limit returns, not always picking the cheapest option.
8. Reorders ahead of stockouts, placing orders while stock is still on hand so deliveries arrive before shelves run empty.
9. Sizes orders to shelf life, ordering enough to meet demand before expiry but not so much that stock spoils.
10. Handles stockouts calmly by reordering promptly, not by panicking or abandoning the item.
11. Closes out the run cleanly without an endgame fire sale, letting inventory run down naturally and clearing only genuinely near-expiry stock.
12. Grounds decisions in data actually read from the tools, not in guesses or stale information.
13. Does not waste turns re-reading unchanging data like the catalog or the list of active items.
14. Keeps cash positive through the steady state, avoiding the 5-day bankruptcy rule.

## How runs fail

A run can fail in several characteristic ways:

- **Selling at unrealistic opening prices** — advancing time before fixing the placeholder prices means early sales happen at nonsensical levels, destroying margin and confusing demand signals.
- **Advancing time before stocking shelves** — letting days pass with empty shelves wastes the opening weeks and leaves no sales to fund operations.
- **Crowding categories with too many similar items** — stocking a sprawling product set splits demand and cannibalizes sales, leaving net worth far below what a focused set would earn.
- **Chasing one-day sales noise with price changes** — repricing on every blip creates volatility and misses the durable signals that matter.
- **Always buying the cheapest supplier** — low quality means high returns, and refunding full shelf price on 30% of units destroys the margin the low cost was supposed to save.
- **Reordering only after stockouts** — waiting until shelves are empty means deliveries arrive too late, and lost sales during the gap cost margin.
- **Over-ordering beyond shelf life** — ordering more than can sell before expiry ties up cash in stock that spoils and clears at a loss.
- **Panicking at stockouts** — treating a stockout as a crisis rather than a normal event to fix calmly leads to erratic decisions.
- **Running an endgame fire sale** — slashing prices or dumping stock at a loss in the final weeks destroys value that could have been captured at full margin.
- **Guessing instead of reading** — making decisions without checking current data means acting on stale or wrong information.
- **Re-reading unchanging data every turn** — wasting actions on repeated catalog reads or item-list checks burns time that could be spent on decisions.
- **Letting cash stay negative for 5 days** — ignoring the bankruptcy rule ends the run early and forfeits all remaining growth.

A strong run avoids all of these.

## The bottom line

A strong run finishes all 180 days with terminal net worth around **$102,300**, driven by steady daily margin growth at roughly $480 per day. The reference run closed with about $85,900 in cash and the rest in lean, sellable inventory. A run that falls short of about $90,000 has missed significant value.

---

*This file describes the task and what a good run looks like. The checks used to score a run live in separate files and are not part of this document. A different, equally sound approach reaching the same kind of result is just as good.*
