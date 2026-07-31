# Task truth: d0f8ad74-049d-5646-baf6-430dc680c4bb

This document describes what the task is, how the store works, what a strong run looks like, and the ways runs go wrong. It is a plain-language guide, not a scoring file. The scoring machinery lives elsewhere.

The walkthrough and numbers below come from one strong reference run that reached about $119,000 in net worth over 180 days. That run is a bar to beat and one good way to play the store, but it is not the only way and not a script to copy. A sharper operator can beat those numbers, and several different sound approaches can all be good.

## The store you're running

You are running store 15 for 180 days starting September 7, 1991. You open with $50,000 in cash and pay $1,000 rent every day. The shelf can hold about 40,000 units, though this is a soft limit — extra stock waits in the back room and ties up cash until space frees up. You stock 20 categories: Bathroom Tissues, Beer, Bottled Juices, Canned Soup, Canned Tuna, Cereals, Cheeses, Cigarettes, Cookies, Crackers, Dish Detergent, Fabric Softeners, Front-end Candies, Frozen Entrees, Frozen Juices, Oatmeal, Paper Towels, Snack Crackers, Soft Drinks, and Toothpastes.

How this store works:

- **Net worth is the score.** Net worth equals cash on hand plus the value of unsold stock plus any orders still in transit. Unsold stock is valued at what you paid for it, then written down steadily as its shelf life runs out, and counts as zero once it expires. In-transit orders count at their cost. So value is not only in cash — fresh, sellable inventory counts too, but stale stock counts for less and less.
- **Everything is perishable.** Each item has a shelf life, typically a few weeks. Anything unsold when it expires is cleared out at about 60% of what you paid for it, which is a loss. Over-ordering beyond what can sell in time quietly destroys value.
- **Returns depend on supplier quality.** Customers return some of what they buy, and you refund them the full shelf price. The return rate is driven by the quality of the supplier the goods came from. The cheapest, lowest-quality suppliers are returned far more often, up to about 30% of units, than top-quality ones, as little as 2%. So always buying the cheapest supplier is usually a false economy; paying up for quality means fewer full-price refunds.
- **Crowding a category cannibalizes it.** Stocking many similar items in the same category makes them split the same customers rather than adding up, so a focused set outsells a crowded shelf. When you raise the price on one item, some of its demand shifts to other active items in the same category, and vice versa.
- **Prices matter, mildly.** Demand is mildly price-sensitive. A higher price sells somewhat less, a lower price somewhat more.
- **Deliveries take time.** Orders take several days to arrive, so reordering has to happen before shelves run empty.
- **Going broke ends the run.** If cash stays below zero for five days in a row, the store is shut down and the run ends early.
- **Customer reviews are on.** Quality slowly shapes demand over time as customers notice and respond to what they experience.
- **News events are on.** External events can shift demand for certain categories during the run.

### The fixed setup

| **Store**            | 15                                      |
|----------------------|-----------------------------------------|
| **Length**           | 180 days (starting 09/07/91)            |
| **Starting cash**    | $50,000                                 |
| **Daily rent**       | $1,000                                  |
| **Shelf capacity**   | 40,000 units (soft limit)               |
| **Categories**       | 20 categories (listed above)            |
| **Customer reviews** | On                                      |
| **News events**      | On                                      |

> The numbers cited throughout this document come from one reference run and describe ranges and properties, not exact targets to hit.

## What a great run looks like

The reference run ended at **$118,829.52** in net worth, about 2.4 times the opening cash, after completing all 180 days. At the close, the store held about $109,800 in cash and roughly $9,000 in fresh, sellable inventory still on the shelf. The net worth curve followed a dip-recover-climb shape: cash dropped sharply in the first week as the operator stocked the shelves, recovered as sales began, then climbed steadily through the middle and late periods. A run that falls short of about $100,000 has left significant value on the table.

## How a strong operator plays it, step by step

This is one good way to run the store, not a fixed recipe.

**Opening (days 1–10).** The operator faces empty shelves, unrealistic opening prices, and the need to get the store running before cash runs out. A strong operator reads the catalog to understand what is available, fixes the opening prices to realistic levels before selling anything, chooses a focused set of items across all 20 categories, and places opening orders sized to fill the shelves without over-ordering. The operator balances supplier cost against quality, avoiding the cheapest suppliers in categories where returns would be costly. Orders arrive over several days, so the operator staggers them and monitors cash carefully. The reference run saw cash drop to about $1,100 on day 6 as opening orders arrived, then recover as sales began. The operator does not advance the day until shelves are stocked and prices are set.

**Steady state (days 11–160).** The operator settles into a daily rhythm: check what sold and what is running low, reorder ahead of stockouts, adjust prices when demand signals are durable, and respond to news events when they shift category demand. A strong operator keeps the product set focused, avoids crowding categories with too many similar items, and reorders in quantities that match shelf life and sales velocity. The operator reads sales and stock data to ground decisions, but does not waste turns re-reading unchanging information. The reference run placed about 1,200 orders across the full 180 days, roughly 6 to 7 per day, and confirmed most existing prices rather than changing them constantly. Stockouts happened on about 68 days, which is normal — a strong operator handles them calmly by reordering and does not panic. Net worth climbed at a steady pace, roughly $700 per day through the middle stretch, as the operator balanced inventory investment against cash flow.

**Ending (days 161–180).** The operator prepares for the close by letting inventory run down naturally, not placing large late orders that will not sell in time, and not fire-selling good stock at a loss. The reference run ended with about $9,000 in fresh inventory still on the shelf, which is lean but still selling. A strong operator does not clear the shelves early or stop reordering too soon, because unsold fresh stock still counts toward net worth and a premature wind-down leaves money on the table.

## What a good run has to get right

A good run must satisfy these properties, in its own way:

1. Survive the full 180-day horizon without going broke — cash must not stay below zero for five consecutive days.
2. End near or above the reference band of about $100,000 to $120,000 in net worth.
3. Fix the unrealistic opening prices before selling anything, so the store does not lose money on the first sales.
4. Stock the shelves before advancing through the opening days, so the store has something to sell when customers arrive.
5. Keep a focused product set — avoid crowding categories with too many similar items that cannibalize each other.
6. Price on durable demand signals, not one-day blips — most price touches should confirm the existing price is still right.
7. Choose suppliers on a balance of quality and cost to limit returns — the cheapest supplier is often a false economy.
8. Reorder ahead of stockouts, because deliveries take several days and an empty shelf loses sales.
9. Size orders to shelf life — over-ordering beyond what can sell in time quietly destroys value through spoilage and write-downs.
10. Handle stockouts calmly — they happen in a normal run, and the right response is to reorder, not to panic or over-correct.
11. No endgame fire-sale — clearing good stock early or stopping reorders too soon leaves value on the table.
12. Ground decisions in data actually read — check what sold, what is low, and what demand looks like before acting.
13. Do not waste turns re-reading unchanging data — read what you need, then act.
14. End with lean but still-selling inventory — fresh stock on the shelf at the close still counts toward net worth.

## How runs fail

Runs fail in characteristic ways:

- **Going broke early.** The operator orders too much too fast in the opening, cash drops below zero and stays there for five days, and the run ends early. This destroys all future value.
- **Ignoring opening prices.** The operator advances the day without fixing the unrealistic opening prices, sells at a loss, and bleeds cash before the store even starts.
- **Crowding categories.** The operator stocks too many similar items in the same category, they cannibalize each other, and total sales are lower than a focused set would have achieved.
- **Chasing the cheapest supplier.** The operator always buys the lowest-cost supplier, return rates spike, and the store refunds full shelf price on 20% or 30% of sales, which quietly destroys margin.
- **Over-ordering.** The operator places large orders without checking shelf life or sales velocity, stock spoils before it sells, and value is written down or cleared at a loss.
- **Reacting to noise.** The operator changes prices constantly in response to one-day fluctuations, confuses customers, and destabilizes demand.
- **Letting stockouts linger.** The operator does not reorder ahead of stockouts, shelves go empty, and sales are lost for days while deliveries are in transit.
- **Endgame fire-sale.** The operator panics near the end and clears good stock at a loss, or stops reordering too soon and ends with empty shelves, leaving value on the table.
- **Not reading data.** The operator guesses at what to order or price without checking what actually sold or what stock levels are, and decisions drift away from reality.
- **Wasting turns on unchanged data.** The operator re-reads the same catalog or prices over and over, burns turns without acting, and falls behind.

A strong run avoids all of these.

## The bottom line

The reference run ended at about $118,800 in net worth after completing all 180 days, with roughly $109,800 in cash and $9,000 in lean but still-selling inventory. A run that falls short of about $100,000 has left significant value on the table.

---

*This document describes the task and what a good run looks like. The checks used to score a run live in separate files and are not part of this document. A different, equally sound approach reaching the same kind of result is just as good.*
