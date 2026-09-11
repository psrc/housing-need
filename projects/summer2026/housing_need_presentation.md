---
marp: true
title: Housing Need Methodology
---

# Estimating Housing Need

How we translate population into housing need, county by county

---

## The Core Idea

If people at every age formed households at **year-2000 rates** — before rising
costs and scarcity suppressed household formation — how many households (and
housing units) would today's population require?

- Compare that estimate to today's actual housing stock → **current shortage**
- Apply the same rates to a population forecast → **long-run housing need**

> 📊 *[Chart placeholder: simple diagram showing Population → Households → Housing Units]*

---

## Three Steps to Convert Population → Housing Units

1. **Group quarters** — set aside people who don't occupy their own housing
   unit (dorms, prisons, nursing homes, etc.)
2. **Headship rates** — estimate how many of the remaining people head their
   own household, by age
3. **Vacancy rates** — convert households into total housing units needed

All three rates are calculated once from Decennial Census data, then applied
to both current-year and forecast-year populations.

---

## Data Sources

| Data | Source |
|---|---|
| Group-quarters & household formation | Decennial Census (2000, 2010, or 2020, depending on rate) |
| Vacancy data | 2020 Census housing occupancy data |
| Current population by age | WA OFM population estimates (latest year) |
| Current housing unit counts | WA OFM housing unit estimates |
| Forecast population by age | Regional REMI forecast (chosen future year) |

All data is broken into nine age groups (10-year bands, plus 0-14 and 85+).

---

## Step 1: Group-Quarters Rates

For each county and age group: what share of the population lives in group
quarters rather than in a household?

- Calculated from **2020 Census** data
- Applied to current & forecast populations to isolate the **household population**

> 📊 *[Chart placeholder: group-quarters rate by age group, one line per county]*

---

## Step 2: Headship Rates

For each county and age group: what share of the household population is the
**householder** (as opposed to living in someone else's household)?

- Rises steeply through young adulthood
- Varies by county depending on demographics
- **Children (0–14)**: assumed to form zero households

> 📊 *[Chart placeholder: headship rate curve by age, 2000 vs. current]*

---

## Why Use Year-2000 Rates?

- Rising housing costs are believed to have **suppressed** household formation
  since 2000 (roommates, adult children staying home longer, etc.)
- Year 2000 is treated as a **"housing not constrained" benchmark**
- Gap between year-2000-rate estimate and actual current housing stock =
  **pent-up / suppressed housing need**

---

## Step 3: Vacancy Rates

For each county: what share of housing units are vacant at any given time?

- Needed for a healthy, functioning housing market (turnover, moving, seasonal
  homes, etc.)
- Calculated from **2020 Census** housing data
- Calculated at the **county level only** (not by age)

> 📊 *[Chart placeholder: vacancy rate by county]*

---

## Step 4: Applying the Rates

For a given year's population, by county and age group:

1. Set aside group-quarters population → household population
2. Apply headship rate → number of households
3. Adjust for vacancy rate → total housing units needed

Repeated for **current-year** population and **forecast-year** population;
results summed across age groups for a county/regional total.

> 📋 *[Table placeholder: housing units needed by county, current vs. forecast]*

---

## Step 5: Shortage & Long-Run Need

- **Current housing shortage** = current-year estimated need − actual current
  housing stock
- **Long-run housing need** = forecast-year estimated need
- **Growth/need to forecast year** = forecast-year need − current housing stock
  *(combines current shortage + growth)*
  - Divide by number of years → **average annual housing need**

> 📊 *[Chart placeholder: current shortage vs. long-run need by county]*

---

## Putting It All Together

- These estimates are combined with a separate **homelessness-based need**
  estimate to produce the final regional summary
- Homelessness component is estimated **regionally only** (not by county)

> 📋 *[Table placeholder: final regional summary — housing need + homelessness need]*

---

## Key Takeaways

- Uses year-2000 household-formation rates as an "unconstrained" benchmark
- Three rates (group-quarters, headship, vacancy) drive the whole model
- Produces both a **current shortage** and a **long-run need** figure, by
  county and regionally
