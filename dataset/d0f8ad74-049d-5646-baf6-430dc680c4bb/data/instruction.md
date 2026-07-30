# Store Operations

You run a retail store (store 15) for a fixed period of 180 days, starting with $50000 in funds. Your goal is to maximize the store's net worth at the end of day 180. Net worth is the cash you hold, plus the value of inventory on hand (valued at what you paid for it, declining as the goods age), plus the value of stock you have ordered but not yet received. A fixed rent of $1000 is charged every day regardless of sales, so the store must stay solvent throughout.

## How the store works

- The store carries products across 20 categories: Bathroom Tissues, Beer, Bottled Juices, Canned Soup, Canned Tuna, Cereals, Cheeses, Cigarettes, Cookies, Crackers, Dish Detergent, Fabric Softeners, Front end candies, Frozen Entrees, Frozen Juices, Oatmeal, Paper Towels, Snack Crackers, Soft Drinks, and Toothpastes.
- Products in the same category compete for the same shoppers, so adding or promoting products within a category can draw sales away from the other products in that category.
- A product's unit sales fall as its shelf price rises and rise as its price falls. The total number of shoppers coming through is set by the market and is outside your control.
- Past sales history is available to you and is the main signal for anticipating future demand.
- Customer reviews affect demand over time. Each product's return rate depends on the quality of the supplier it was bought from — higher-quality goods are returned less often. A return refunds the customer the full sale price.
- Suppliers differ in price, in quality, and in delivery time. An order is paid for when it is placed and arrives after a delay of a few days.
- Inventory is perishable: stock has a short shelf life, and units that expire unsold are cleared at a loss, so ordering more than can be sold in time is wasteful.
- The warehouse holds a limited number of units (40000 units). Stock beyond that limit cannot go on the shelf until space frees up.
- Daily news can shift demand for individual products or whole categories. You can read the day's news and factor it into your decisions.

## What you do

Each day you can review the store's current data — inventory on hand, available funds, sales history, supplier prices and quality, and customer reviews — and then decide what to order from which supplier and what shelf prices to set. Decisions carry over from day to day, so plan across the full 180 days rather than optimizing any single day in isolation.
