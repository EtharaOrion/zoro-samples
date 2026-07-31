# Task truth: 614fe8a9-05ec-5fe4-9e42-e58032b9e045

This document describes what the task is, how the store works, what a strong run looks like, and the ways runs go wrong. The scoring machinery that evaluates a run lives in separate files and is not part of this guide.

The walkthrough and numbers below come from one strong reference run. They show one good way to play the store and set a bar to beat, but they are not the only way and not a script to copy. A sharper operator can beat these numbers, and several different approaches can all be good runs.

## The store you're running

You are running store 15 for 180 days, starting September 7, 1991. You open with $10,000 in cash and pay $250 rent every day. The shelf can hold about 10,000 units, though this is a soft limit — extra stock waits in the back room and ties up cash until space frees up. You stock five categories: Bathroom Tissues, Cheeses, Frozen Entrees, Snack Crackers, and Soft Drinks.

**How this store works:**

- **Net worth is the score.** Net worth equals cash on hand plus the value of unsold stock you are holding plus any orders still in transit. Unsold stock is valued at what you paid for it, then written down steadily as its shelf life runs out, and counts as zero once it expires. In-transit orders count at their cost. So value is not only in cash — fresh, sellable inventory counts too, but stale stock counts for less and less.
- **Returns depend on supplier quality.** Customers return some of what they buy, and you refund them the full shelf price. The return rate is driven by the quality of the supplier the goods came from. The cheapest, lowest-quality suppliers are returned far more often (up to about 30% of units) than top-quality ones (as little as 2%). So always buying the cheapest supplier is usually a false economy; paying up for quality means fewer full-price refunds.
- **Everything is perishable.** Each item has a shelf life, typically a few weeks. Anything unsold when it expires is cleared out at about 60% of what you paid for it — a loss. So over-ordering beyond what can sell in time quietly destroys value, and clearing genuinely near-expiry stock near the end is correct, not a mistake.
- **Crowding a category cannibalizes it.** Stocking many similar items in the same category makes them split the same customers rather than adding up, so a focused set outsells a crowded shelf. When you raise the price on one item, some of its demand shifts to other active items in the same category, and when you lower a price, you pull some demand away from the others. A lean, focused product set avoids this splitting.
- **Prices matter, mildly.** Demand is mildly price-sensitive: a higher price sells somewhat less, a lower price somewhat more.
- **Shelf capacity is soft.** The 10,000-unit shelf limit is not a hard cap on ordering. Extra units wait in the back room and tie up cash until space frees up. Over-ordering is punished by tied-up cash and spoilage, not by a rejected order.
- **Deliveries take time.** Orders take several days to arrive, so reordering has to happen before shelves run empty.
- **Going broke ends the run.** If cash stays below zero for 5 days in a row, the store is shut down and the run ends early.
- **Customer reviews are on.** Quality slowly shapes demand over time as customers learn which products are good.

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

> The numbers cited in this document come from one reference run. They are ranges and properties to understand, not exact targets to hit.

## What a great run looks like

The reference run closed at **$31,788.65** net worth after the full 180 days — more than triple the opening cash. Cash stood at about $26,600 and inventory at about $5,200, a lean but still-selling stock. The run dipped briefly into the red in the first few days, recovered by day 10, and then climbed steadily at roughly $150 per day through the middle and late stages. A run that falls short of about $28,000 has left significant value on the table.

## How a strong operator plays it, step by step

This is one good way to play the store, not a fixed recipe. A strong operator solves three problems in sequence: getting the opening right, running the daily loop well, and closing cleanly.

**Opening (days 1–10).** The problem is to fix the unrealistic opening prices, stock the shelves with a focused product set, and survive the cash dip. A strong operator reads the catalog, picks about 15–20 items spread across the five categories (3–4 per category to avoid crowding), chooses suppliers balancing cost and quality to limit returns, sets realistic shelf prices, and places opening orders sized to fill the shelves without tying up too much cash. The first orders arrive after a few days, so the operator advances time carefully to let stock land and sales start. Cash dips briefly below zero (the reference hit about negative $125 on day 3) but recovers as sales come in. By day 10, shelves are stocked, prices are grounded in real demand, and cash is positive and climbing.

**Steady state (days 11–160).** The problem is to keep shelves stocked, prices stable, and net worth climbing without wasting effort. A strong operator checks stock levels daily, reorders items running low (typically placing 2–3 orders per day, for reference), and adjusts prices only when demand signals are durable — not on one-day blips. The reference run kept 92% of price touches unchanged, meaning prices were set well and left alone. Stockouts happen occasionally (the reference had stockouts on about 45 days across the run) but are handled calmly by reordering promptly, not by panic moves. The operator sizes orders to shelf life so stock sells before it expires, and watches supplier quality to keep return rates low. Net worth climbs steadily; the reference grew at about $150 per day through this phase. The operator does not waste turns re-reading unchanging catalog data or checking stock that was just checked.

**Ending (days 161–180).** The problem is to close with lean inventory and high cash, not to dump stock in a fire sale. A strong operator tapers orders in the final three weeks so fresh stock sells down naturally, clears genuinely near-expiry items at cost or slightly below (this is correct, not a mistake), and keeps prices stable. The reference closed with about $5,200 in inventory — lean but still selling — and $26,600 in cash. A panicked endgame fire sale destroys value; a calm taper preserves it.

## What a good run has to get right

A good run must satisfy these properties, in its own way:

1. Survive the full 180 days without going broke (cash below zero for 5 consecutive days).
2. End near or above the reference band of about $28,000 to $32,000 net worth.
3. Fix the unrealistic opening prices before selling, grounding them in the catalog and early demand signals.
4. Stock the shelves with a focused product set (roughly 15–20 items spread across the five categories) before advancing time in bulk.
5. Keep the product set focused throughout — a crowded category cannibalizes itself, so a lean set outsells a bloated one.
6. Adjust prices on durable demand signals, not one-day noise — most price reviews should confirm the existing price is still right.
7. Choose suppliers balancing cost and quality to limit returns — the cheapest supplier is often a false economy when returns hit 30%.
8. Reorder ahead of stockouts so deliveries arrive before shelves run empty, but handle occasional stockouts calmly without panic moves.
9. Size orders to shelf life so stock sells before it expires — over-ordering beyond what can sell in time quietly destroys value through spoilage.
10. Taper orders in the final three weeks so inventory sells down naturally, and clear genuinely near-expiry stock near the end without a fire sale.
11. Ground decisions in data actually read from the tools — guessing supplier quality or demand without checking the numbers leads to poor choices.
12. Do not waste turns re-reading unchanging catalog data or checking stock levels that were just checked — efficient operators move deliberately.

## How runs fail

Runs fail in characteristic ways, and each destroys a different part of the value:

- **Going broke early.** Ordering too much too fast in the opening, or picking suppliers so cheap their return rates drain cash, can push cash negative for 5 straight days and end the run early. This destroys everything.
- **Leaving shelves empty.** Failing to stock the shelves before advancing time, or letting stockouts persist for days, means no sales and no growth. This destroys the revenue stream.
- **Crowding the categories.** Stocking 10 or 15 items in one category makes them split the same customers and all sell poorly. This destroys the sales potential of the whole category.
- **Chasing noise.** Adjusting prices daily on one-day blips, or changing the product set constantly, wastes effort and destabilizes demand. This destroys efficiency and growth.
- **Ignoring supplier quality.** Always buying the cheapest supplier to save a few cents per unit leads to 30% return rates and full-price refunds that drain cash faster than the savings. This destroys profitability.
- **Over-ordering.** Ordering more than can sell before expiry ties up cash in stock that spoils and gets cleared at 60% of cost. This quietly destroys value every week.
- **Panicking at stockouts.** Treating an occasional stockout as a crisis and making wild changes wastes effort and destabilizes the run. This destroys calm, steady growth.
- **Fire-sale ending.** Slashing prices across the board in the final week to dump inventory destroys more value than it recovers. This turns a strong run into a mediocre one.
- **Guessing instead of reading.** Ordering without checking stock levels, or pricing without reading demand data, leads to poor decisions that compound. This destroys the information advantage the tools provide.
- **Wasting effort.** Re-reading the catalog every day, or checking stock that was just checked, burns turns that could be spent on real decisions. This destroys efficiency.

A strong run avoids all of these.

## The bottom line

The reference run closed at $31,788.65 net worth after 180 days, with about $26,600 in cash and $5,200 in lean, still-selling inventory. It dipped briefly into the red in the opening, recovered by day 10, and climbed steadily at roughly $150 per day through the middle and late stages. A run that falls short of about $28,000 has left significant value on the table.

---

*This document describes the task and what a good run looks like. The checks used to score a run live in separate files and are not part of this document. A different, equally sound approach reaching the same kind of result is just as good.*
