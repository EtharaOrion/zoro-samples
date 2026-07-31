# Task truth: 891a0d2a-028a-5c17-ab92-8ba39f9bebb3

This document is a plain-language guide to the task, what a strong run looks like, and the properties a good run must satisfy. The scoring machinery lives elsewhere and is not part of this file.

The walkthrough and numbers below come from one strong reference run. They show a bar to beat and one good way to play the store, but they are not the only way and not a script to copy. A sharper operator can beat these numbers, and several different approaches can all be good.

## The store you're running

You are running store 15 for 180 days starting September 7, 1991. You open with $30,000 in cash and pay $700 rent every day. The shelf can comfortably hold about 25,000 units, though you can order more — extra stock waits in the back room and ties up cash until space frees up. You carry twenty categories: Bathroom Tissues, Beer, Bottled Juices, Canned Soup, Canned Tuna, Cereals, Cheeses, Cigarettes, Cookies, Crackers, Dish Detergent, Fabric Softeners, Front-end Candies, Frozen Entrees, Frozen Juices, Oatmeal, Paper Towels, Snack Crackers, Soft Drinks, and Toothpastes.

**How this store works:**

- **Net worth is the score.** Net worth equals cash on hand plus the value of unsold stock you are holding plus any orders still in transit. Unsold stock is valued at what you paid for it, then written down steadily as its shelf life runs out, and counts as zero once it expires. In-transit orders count at their cost. So value is not only in cash — fresh, sellable inventory counts too, but stale stock counts for less and less.
- **Returns depend on supplier quality.** Customers return some of what they buy, and you refund them the full shelf price. The return rate is driven by the quality of the supplier the goods came from. The cheapest, lowest-quality suppliers are returned far more often, up to about 30% of units, while top-quality ones see as little as 2%. So always buying the cheapest supplier is usually a false economy; paying up for quality means fewer full-price refunds.
- **Everything is perishable.** Each item has a shelf life, typically a few weeks. Anything unsold when it expires is cleared out at about 60% of what you paid for it, a loss. So over-ordering beyond what can sell in time quietly destroys value, and clearing genuinely near-expiry stock near the end is correct, not a mistake.
- **Crowding a category cannibalizes it.** Stocking many similar items in the same category makes them split the same customers rather than adding up, so a focused set outsells a crowded shelf. When you raise the price on one item, some of its demand shifts to other active items in the same category, and when you lower a price, you pull some demand away from the others. A lean, well-chosen product set performs better than a sprawling one.
- **Prices matter, mildly.** Demand is mildly price-sensitive. A higher price sells somewhat less; a lower price sells somewhat more.
- **Shelf capacity is soft.** The 25,000-unit capacity is not a hard cap on ordering. Extra units wait in the back room and tie up cash until space frees up. Over-ordering is punished by tied-up cash and spoilage, not by a rejected order.
- **Deliveries take time.** Orders take several days to arrive, so reordering has to happen before shelves run empty.
- **Going broke ends the run.** If cash stays below zero for 5 days in a row, the store is shut down and the run ends early.
- **Customer reviews are on.** Quality slowly shapes demand over time as customers learn which products are reliable.
- **News events are on.** External events can shift demand for certain categories during the run.

### The fixed setup

| **Store** | 15 |
| **Length** | 180 days (starting 09/07/91) |
| **Starting cash** | $30,000 |
| **Daily rent** | $700 |
| **Shelf capacity** | 25,000 units (soft) |
| **Categories** | 20 (Bathroom Tissues, Beer, Bottled Juices, Canned Soup, Canned Tuna, Cereals, Cheeses, Cigarettes, Cookies, Crackers, Dish Detergent, Fabric Softeners, Front-end Candies, Frozen Entrees, Frozen Juices, Oatmeal, Paper Towels, Snack Crackers, Soft Drinks, Toothpastes) |
| **Customer reviews** | On |
| **News events** | On |

> The numbers cited below come from one reference run. They are ranges and properties to understand, not exact targets to hit.

## What a great run looks like

The reference run closed at **$106,756** in net worth after the full 180 days, more than 3.5 times the opening cash. About $101,000 was cash and the rest was lean, sellable inventory. The run dipped briefly into the red in the opening days, recovered quickly, and then climbed steadily at roughly $650 per day through the middle and late stages. A run that falls short of about $90,000 has left significant value on the table.

## How a strong operator plays it, step by step

This is one good way to play the store, not a fixed recipe.

**Opening (days 1–10).** The problem is that the store starts with no stock and unrealistic default prices. A strong operator first fixes the prices to sensible market levels before selling anything, then stocks the shelves with a focused, quality-conscious product set. The reference run placed about 1,200 orders across the full 180 days, roughly 6 to 7 per day, and kept nearly 90% of price touches at the existing price, meaning most pricing work was confirming good levels rather than constant tinkering. The operator chooses suppliers carefully, balancing cost against quality to limit the flood of full-price refunds that cheap suppliers bring. Cash dips into the red briefly as the opening orders go out — the reference hit a low of about negative $335 on day 4 — but recovers as sales begin and the shelves fill. By day 10 the store is stocked, priced, and selling.

**Steady state (days 11–160).** The problem is to keep shelves stocked without over-ordering, maintain sensible prices, and grow net worth steadily. A strong operator reads sales and stock levels each day, reorders items that are running low well before they stock out, and sizes each order to what can sell before it expires. The reference run saw stockouts on about 96 days across the full horizon, meaning the operator kept shelves mostly full but did not waste cash on excess safety stock. Prices are adjusted when durable signals — a sustained shift in demand, a news event, a quality trend — call for it, not in reaction to one-day blips. The operator does not re-read unchanging data every turn; once a price or supplier is set and working, the operator moves on. The reference run grew net worth at roughly $650 per day through this phase, compounding cash and inventory value together.

**Ending (days 161–180).** The problem is to finish strong without a wasteful fire-sale. A strong operator continues normal operations, reordering and pricing as usual, and lets genuinely near-expiry stock clear at the standard markdown near the end. The reference closed with about $5,700 in inventory, all of it fresh and sellable, and $101,000 in cash. There is no endgame panic, no slashing prices to zero, no dumping good stock at a loss.

## What a good run has to get right

A good run must satisfy these properties, in its own way:

1. Survive the full horizon without going broke — cash may dip below zero briefly in the opening, but must not stay negative for 5 consecutive days.
2. End near or above the reference band of roughly $90,000 to $110,000 in net worth, showing the operator grew value steadily and did not leave major opportunities on the table.
3. Fix the unrealistic opening prices to sensible market levels before selling, so the store does not bleed value through mispriced goods.
4. Stock the shelves before advancing through the run — a store with empty shelves for days on end cannot sell.
5. Keep a focused product set in each category, not a sprawling shelf that cannibalizes itself.
6. Price on durable signals, not one-day blips — a price that changes every day for no reason confuses customers and wastes effort.
7. Choose suppliers on quality and cost together to limit returns — the cheapest supplier is rarely the best deal when 30% of units come back for a full refund.
8. Reorder ahead of stockouts, since deliveries take several days — waiting until shelves are empty means lost sales.
9. Size orders to shelf life, not to some fixed rule — over-ordering beyond what can sell in time quietly destroys value through spoilage.
10. Handle stockouts calmly when they happen — a few stockouts across 180 days is normal and better than tying up cash in excess safety stock.
11. No endgame fire-sale — slashing prices or dumping good stock at a loss in the final days destroys value for no reason.
12. Ground decisions in data actually read — the operator must check sales, stock, and prices to know what to do, not guess.
13. Do not waste turns re-reading unchanging data — once a price or supplier is set and working, move on to the next decision.
14. Close with lean, sellable inventory and strong cash — the reference closed with about $5,700 in fresh stock and $101,000 in cash, showing the operator did not over-order or under-sell.

## How runs fail

Runs fail in characteristic ways:

- **Ignoring supplier quality and always buying the cheapest.** This floods the store with returns at full shelf price, destroying cash and net worth. A strong run pays up for quality and limits refunds.
- **Over-ordering beyond shelf life.** This ties up cash in stock that spoils before it sells, quietly destroying value. A strong run sizes orders to what can sell in time.
- **Crowding categories with too many similar items.** This cannibalizes demand and lowers total sales. A strong run keeps a focused, high-performing set.
- **Leaving prices at unrealistic opening defaults.** This bleeds value through mispriced goods. A strong run fixes prices before selling.
- **Reacting to one-day blips instead of durable signals.** This wastes effort and confuses customers. A strong run prices on sustained trends.
- **Waiting until shelves are empty to reorder.** This loses sales during the delivery lag. A strong run reorders ahead of stockouts.
- **Running an endgame fire-sale.** This dumps good stock at a loss for no reason. A strong run finishes normally and closes with lean, sellable inventory.
- **Re-reading unchanging data every turn.** This wastes time and effort. A strong run reads what has changed and moves on.
- **Letting cash stay negative for 5 consecutive days.** This shuts the store down early. A strong run manages the opening dip and recovers quickly.

A strong run avoids all of these.

## The bottom line

The reference run closed at **$106,756** in net worth after 180 days, with about $101,000 in cash and $5,700 in lean, sellable inventory. It grew value steadily at roughly $650 per day through the middle and late stages, kept shelves mostly stocked, and finished strong. A run that falls short of about $90,000 has missed significant opportunities.

---

*This file describes the task and what a good run looks like. The checks used to score a run live in separate files and are not part of this document. A different, equally sound approach reaching the same kind of result is just as good.*
