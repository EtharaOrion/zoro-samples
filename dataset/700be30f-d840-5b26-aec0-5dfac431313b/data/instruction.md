# Store Operations

You run a retail store for 180 days. Your goal is to maximize the store's net worth at the end of day 180. Net worth is the cash you have on hand, plus the value of your current inventory (valued at what you paid for it, declining as the goods age), plus the value of any stock you have ordered but not yet received. A fixed rent of $250 is charged every day regardless of sales, so the store must stay solvent throughout. You begin with $10000 in funds.

## How the store works

- The store sells products across five categories: Bathroom Tissues, Cheeses, Frozen Entrees, Snack Crackers, and Soft Drinks. Products in the same category compete for the same shoppers, so adding products to a category can draw sales away from the others in that category.
- A product's unit sales fall as its shelf price rises and rise as its price falls. Total shopper traffic is set by the market and is outside your control.
- Past sales history is available and is the main signal you have for future demand.
- Customer reviews affect demand over time. Each product's return rate depends on the quality of the supplier it was bought from — higher-quality goods are returned less often. A return refunds the customer the full sale price.
- Suppliers differ in price, in quality, and in delivery time. An order is paid for when it is placed and arrives after a delay of a few days.
- Inventory is perishable: stock has a short shelf life, and units that expire unsold are cleared at a loss, so ordering more than can be sold in time is wasteful.
- The warehouse holds up to 10000 units. Stock beyond that limit cannot go on the shelf until space frees up.

## What you do

Each day you can review the store's current data — inventory, funds, sales history, supplier prices and quality, and customer reviews — and then decide what to order from which supplier and what shelf prices to set. Decisions carry over from day to day, so plan across the whole 180 days rather than optimizing a single day.
