# Housing Need Methodology

This document describes how current and future housing need is estimated for each county.
It does not cover the homelessness-based need estimate, which is documented separately.

## Overview

The core idea is to take the population, broken down by age, and ask: if people at every
age formed households at the rate they did in the year 2000 - before rising housing costs
and scarcity suppressed household formation - how many households, and therefore how many
housing units, would that population require?

Comparing that estimate to the actual current housing stock gives the current housing
shortage. Applying the same rates to a population forecast gives an estimate of long-run
housing need.

Turning a population into a number of housing units needed takes three steps:

1. Set aside the portion of the population living in **group quarters** (dorms, prisons,
   nursing homes, etc.), since those people don't independently occupy a housing unit.
2. Estimate, for the remaining population, how many people head their own household, using
   **rates of household formation** by age.
3. Convert that number of households into a total number of housing units, using
   **vacancy rates**, since a healthy housing market always has some units sitting empty.

All three rates are calculated once from Decennial Census data (each from its own reference
year) and then applied to both a current-year population and a forecast-year population.

## Data sources

- **Group-quarters population and household-formation data**: Decennial Census
  questionnaire data (from the 2000, 2010, or 2020 Census, depending on which year is
  configured for each rate).
- **Vacancy data**: 2020 Census housing occupancy data.
- **Current population by age**: Washington Office of Financial Management (OFM)
  population estimates, for the most recent year available.
- **Current housing unit counts**: OFM housing unit estimates.
- **Forecast population by age**: The regional REMI economic and demographic forecast, for
  a chosen future year.

All of these are broken down into the same nine age groups, in ten-year bands (for example,
25-34, 35-44, and so on), plus a combined 0-14 group for children and an 85-and-up group for
the oldest residents.

## Step 1: Group-quarters rates

For each county and age group, we calculate what share of the total population lives in
group quarters rather than in a household, using 2020 Census data. This share is called the
**group-quarters rate**. It's later applied to the current and forecast populations to set
aside the group-quarters population and leave the "household population" - the population
that could plausibly live in, and therefore need, its own housing unit.

## Step 2: Rates of household formation ("headship rates")

For each county and age group, we calculate what share of the household population (people
not living in group quarters) are the person a household is recorded under - referred to as
the "householder." This share is often called a **headship rate**, since it reflects how
often people of a given age head, or are the primary person responsible for, a household,
as opposed to living in someone else's household (for example, an adult child living with
their parents, or roommates living together, only one of whom is recorded as the
householder).

This rate is calculated separately for each age group and county, using Census
questionnaire data that reports, by age, both the total population living in households and
the number of those people who are the householder.

The result is, for each age group, the share of people living in households who head their
own household, rather than live in someone else's. This share rises steeply through young
adulthood as people move out on their own, and varies somewhat by county depending on local
demographics.

**Reference year choice**: rates of household formation are calculated using data from the
year **2000** by default. In more recent years, rising housing costs and scarcity are
believed to have suppressed household formation - people who would otherwise be able to
afford to live on their own instead double up with roommates or family, or stay in a
parent's household longer than they otherwise would. Using the year 2000 as the reference
point treats those rates as a "housing not constrained" benchmark: applying them to a
current population estimates how many households would form if today's population had the
same freedom to form their own households as people did in 2000. The gap between that
estimate and the number of households the current housing stock can actually hold is
interpreted as pent-up, or suppressed, housing need.

**Children (ages 0-14)**: no rate of household formation is calculated for this age group,
since children are not considered to head their own households. They are treated as
forming zero households.

## Step 3: Vacancy rates

For each county, we calculate what share of housing units are vacant at any given time,
using 2020 Census housing data. This reflects the share of units that need to sit empty for
a functioning housing market (to allow for moving, turnover, seasonal homes, and so on), and
is used to convert a number of households into the total number of housing units required to
house them.

## Step 4: Applying the rates to a population

For a given year's population, broken down by county and age group:

1. **Set aside the group-quarters population**, using the group-quarters rate for that
   county and age group, leaving the household population.
2. **Estimate the number of households**, by applying the rate of household formation for
   that county and age group to the household population.
3. **Convert households into total housing units needed**, by accounting for the county's
   vacancy rate (vacancy rates are calculated at the county level only, not broken out by
   age).

This is done twice: once using the current-year population estimate, and once using the
forecast population for a chosen future year. In both cases, the results are added up
across all age groups to get a single total-housing-need figure for each county (and for
the region as a whole) for that year.

## Step 5: Shortage and long-run need

- **Current housing shortage**: the current-year estimated housing need minus the actual
  number of housing units currently reported for that county. A positive number means the
  estimated need (based on year-2000 rates of household formation) exceeds today's actual
  housing stock.
- **Long-run housing need**: the forecast-year estimated housing need, representing how
  many housing units the region or county would need by that future year to house the
  forecast population at year-2000 rates of household formation.
- **Growth/need between the current year and the forecast year**: the forecast-year
  estimated need minus the current number of housing units, which combines both the
  current shortage and the additional need created by population growth. Dividing this by
  the number of years between the current year and the forecast year gives an average
  annual housing need figure.

These figures are combined with the homelessness-based need estimate (see the separate
homelessness methodology) to produce the final regional summary, though the homelessness
component is only estimated at the regional level and is not broken out by county.
