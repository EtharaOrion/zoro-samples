# Task truth: f62e57e0-657a-5f2e-a8ef-4fbfc13f7797

This document is a plain-language guide to the task, what a strong run looks like, and the properties a good run must satisfy. The scoring machinery lives in separate files and is not part of this document.

The walkthrough and numbers below come from one strong reference run. They show a bar to beat and one good way to play the store, but they are not the only way and not a script to copy. A sharper operator can beat these numbers, and several different approaches can all be good.

## The store you're running

You are running store 15 for 180 days, starting September 7, 1991. You open with $10,000 in cash and pay $250 in rent every day. The shelf can hold about 10,000 units, though this is a soft limit — extra stock waits in the back room and ties up cash until space frees up. You stock five categories: Bathroom Tissues, Cheeses, Frozen Entrees, Snack Crackers, and Soft Drinks.

**How this store works:**

- **Net worth is the score.** Net worth equals cash on hand plus the value of unsold stock you are holding plus any orders still in transit. Unsold stock is valued at what you paid for it, then written down steadily as its shelf life runs out, and counts as zero once it expires. In-transit orders count at their cost. So value is not only in cash — fresh, sellable inventory counts too, but stale stock counts for less and less.
- **Returns depend on supplier quality.** Customers return some of what they buy, and the store refunds them the full shelf price. The return rate is driven by the quality of the supplier the goods came from. The cheapest, lowest-quality suppliers are returned far more often (up to about 30% of units) than top-quality ones (as little as 2%). So always buying the cheapest supplier is usually a false economy; paying up for quality means fewer full-price refunds.
- **Everything is perishable.** Each item has a shelf life, typically a few weeks. Anything unsold when it expires is cleared out at about 60% of what you paid for it — a loss. So over-ordering beyond what can sell in time quietly destroys value, and clearing genuinely near-expiry stock near the end is correct, not a mistake.
- **Crowding a category cannibalizes it.** Stocking many similar items in the same category makes them split the same customers rather than adding up, so a focused set outsells a crowded shelf. When you add another product to a category that already has several active items, the new one takes sales from the existing ones more than it brings in fresh demand.
- **Prices matter, mildly.** Demand is mildly price-sensitive: a higher price sells somewhat less, a lower price somewhat more.
- **Shelf capacity is soft.** The shelf limit is not a hard cap on ordering. Extra units wait in the back room and tie up cash until space frees up. Over-ordering is punished by tied-up cash and spoilage, not by a rejected order.
- **Deliveries take time.** Orders take several days to arrive, so reordering has to happen before shelves run empty.
- **Going broke ends the run.** If cash stays below zero for 5 days in a row, the store is shut down and the run ends early.
- **Customer reviews are on.** Quality slowly shapes demand over time as customers learn which products are reliable.

### The fixed setup

| Store | Length | Starting cash | Daily rent | Shelf capacity | Categories | Customer reviews | News events |
|-------|--------|---------------|------------|----------------|------------|------------------|-------------|
| 15 | 180 days (from 09/07/91) | $10,000 | $250 | ~10,000 units (soft) | Bathroom Tissues, Cheeses, Frozen Entrees, Snack Crackers, Soft Drinks | On | Off |

> The numbers cited throughout this document come from one reference run and describe ranges and properties, not exact targets to hit.

## What a great run looks like

The reference run closed at **$25,138** in net worth, about 2.5 times the opening cash, after completing all 180 days. Terminal holdings were roughly $17,800 in cash and $7,300 in fresh, sellable inventory. The run dipped briefly into the red in the opening week, recovered by day 10, and then climbed steadily at about $110 per day through the middle and late stages. A run that falls short of about $20,000 has left significant value on the table.

## How a strong operator plays it, step by step

This is one good way to run the store, not a fixed recipe.

**Opening (days 1–10): Fix the setup and stock the shelves.** The store opens with placeholder prices that are often wildly unrealistic. A strong operator reads the market data on day one, sets sensible prices for each product (grounded in what customers will pay and what competitors charge), and places opening orders to fill the shelves with a focused product set. The opening orders are sized to arrive quickly and get the store selling without tying up all the cash in one giant shipment. For reference, the strong run placed about 30 orders in the first week, bringing in roughly 3,000 units, and saw cash dip to about negative $200 on day 5 before sales began to cover rent and restock costs. By day 10, cash was positive and climbing.

**Steady state (days 11–160): Run the daily loop and grow the business.** Each day, a strong operator checks what sold yesterday, what is running low, and what needs reordering. Orders are placed a few days ahead of stockouts, sized to the product's shelf life and the category's capacity, and sourced from suppliers chosen for a sensible quality-and-cost trade-off. The operator keeps the product set lean — about 15 to 20 active items across the five categories — so each product gets enough demand to turn over before it spoils, and categories do not cannibalize themselves with too many similar choices. Prices are touched only when durable signals (a sustained demand shift, a competitor's move, a quality trend) call for it; day-to-day sales noise is ignored. For reference, the strong run placed about 400 orders across the full 180 days (roughly 2 per day), kept prices stable more than 90% of the time when reviewing them, and experienced stockouts on about 40 days — handled calmly by reordering and moving on, not by panic over-ordering. Net worth grew at a steady pace, adding roughly $110 per day through this phase.

**Ending (days 161–180): Close out cleanly without a fire sale.** As the horizon approaches, a strong operator stops placing orders that will not turn over in time and lets inventory run down naturally. There is no endgame panic or deep discounting of still-fresh stock. The goal is to finish with lean but still-selling inventory and cash in hand, not to clear the shelves at a loss. For reference, the strong run closed with about $7,300 in fresh inventory still valued at cost, alongside $17,800 in cash.

## What a good run has to get right

A good run must satisfy these properties:

1. Survive the full 180-day horizon without going broke (cash below zero for 5 consecutive days).
2. End with net worth near or above the reference range of about $20,000 to $25,000.
3. Fix the unrealistic opening prices before selling begins, grounding them in market data actually read.
4. Stock the shelves with opening orders before advancing through the opening week.
5. Keep a focused product set (roughly 15 to 20 active items across five categories) so each product gets enough demand to turn over and categories do not cannibalize themselves.
6. Touch prices only on durable signals (sustained demand shifts, competitor moves, quality trends), not on day-to-day sales noise.
7. Choose suppliers on a sensible quality-and-cost trade-off to limit returns, not always the cheapest option.
8. Reorder ahead of stockouts, sizing orders to shelf life and category capacity, not waiting until shelves are empty.
9. Size orders so stock turns over before it spoils, not over-ordering beyond what can sell in time.
10. Handle stockouts calmly by reordering and moving on, not by panic over-ordering or abandoning the product.
11. Close out the endgame cleanly without a fire sale, finishing with lean but still-selling inventory and cash in hand.
12. Ground every decision in data actually read from the store, not guesses or stale assumptions.
13. Avoid wasting turns re-reading unchanging data when the time could be spent acting on what is already known.

## How runs fail

A run can fail in several characteristic ways:

- **Ignoring the opening prices.** Selling at wildly unrealistic placeholder prices (a $50 box of crackers, a $0.10 gallon of milk) destroys sales or gives away inventory, and the run never recovers.
- **Over-ordering in the opening.** Placing one giant order that ties up all the cash and fills the back room with slow-moving stock leaves no funds to reorder fast sellers, and the store starves for weeks.
- **Crowding categories.** Stocking 10 or 15 similar items in one category makes them split the same customers, so total sales are lower than a focused set of 3 or 4 strong products would achieve.
- **Chasing noise.** Changing prices every day in reaction to normal sales variance wastes time, confuses customers, and does not improve results.
- **Always buying the cheapest supplier.** The lowest-cost suppliers have the highest return rates, so the store refunds 20% or 30% of sales at full shelf price and loses money on every unit.
- **Waiting for stockouts.** Reordering only after shelves are empty means days of lost sales while the new shipment is in transit.
- **Over-ordering beyond shelf life.** Ordering a month's worth of a product with a three-week shelf life means the last units spoil unsold and are cleared at a 40% loss.
- **Panic over-ordering after a stockout.** Doubling or tripling order sizes after one stockout ties up cash in slow-moving inventory and often leads to spoilage.
- **Endgame fire sale.** Slashing prices in the final week to clear still-fresh inventory destroys value that could have been held as stock or sold at normal margins.
- **Guessing instead of reading.** Making decisions without checking what sold, what competitors charge, or what quality trends are emerging leads to mispriced products, wrong suppliers, and missed opportunities.
- **Re-reading unchanging data.** Spending turn after turn checking the same static market facts instead of acting on what is already known wastes time and slows growth.

A strong run avoids all of these.

## The bottom line

The reference run closed at **$25,138** in net worth after completing all 180 days, with about $17,800 in cash and $7,300 in lean, still-selling inventory. A run that falls short of about $20,000 has left significant value on the table.

---

*This document describes the task and what a good run looks like. The checks used to score a run live in separate files and are not part of this document. A different, equally sound approach reaching the same kind of result is just as good.*
