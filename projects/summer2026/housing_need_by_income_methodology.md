# Projected housing needs by income level

The total net new housing needed in each county through 2060 is distributed across income levels, expressed as a share of Area Median Income (AMI). The method follows the approach in Commerce's *Establishing Housing Targets for Your Community* (HB 1220 Book 1) and uses the same income levels: 0-30%, >30-50%, >50-80%, >80-100%, >100-120% and >120% of AMI. The >80-100% and >100-120% levels together make up the moderate-income level (>80-120% AMI) defined in RCW 36.70A.030. Needs above 120% AMI are included so that the income levels sum to the total net new housing needed.

For each income level, net new housing need is the sum of three components:

1. **Housing to eliminate baseline renter cost burden.** New units needed so that cost-burdened renter households have housing affordable at their income level.
2. **Housing for the baseline homeless population.** Permanent housing for households currently experiencing homelessness.
3. **Additional housing to accommodate population growth.** The remaining net new need, distributed across income levels in proportion to today's households.

The sum across all income levels is controlled to the county's total net new housing need, so the income-level results always add back to the total.

Results below are for King, Kitsap, Pierce and Snohomish counties. The base year is 2025 (OFM April 1 housing estimates) and the projection year is 2060.

## Data sources

- **Total net new housing need, 2025-2060**: PSRC housing need estimate (see the housing need methodology), minus OFM 2025 housing units, plus the regional homelessness estimate.
- **Cost-burdened renter households**: HUD Comprehensive Housing Affordability Strategy (CHAS), 2018-2022 ACS, renter households by income level that spend more than 30% of income on housing.
- **Affordability of units occupied by renters**: HUD CHAS Table 18C, renter-occupied units by rent affordability level and household income.
- **Households by income level**: HUD CHAS, all households by income level.
- **Household income detail above 100% AMI**: Census ACS Public Use Microdata Sample (PUMS), 2024 1-year.
- **Area Median Income**: HUD FY2024 Income Limits (4-person median family income by county), adjusted for household size.
- **Housing units and vacancy**: OFM April 1 housing estimates and 2020 Census vacancy rates (5.3% King, 6.6% Kitsap, 5.5% Pierce and 4.6% Snohomish).
- **Homelessness**: PSRC regional estimate of households experiencing homelessness (see the homelessness methodology).

## Total net new housing need

Net new housing need excluding homelessness is the estimated housing needed in 2060 minus the housing units in 2025. Because the 2060 estimate is based on household formation rates that are not constrained by housing supply, this includes both housing to address the current shortage and housing for future population growth. The 2060 estimate does not include housing for households experiencing homelessness, so that need (allocated to counties as described under Component 2) is added to get the total net new housing need.

**Table 1. Total net new housing need, 2025-2060**

| County | Total housing need, 2060 | Housing units, 2025 | Net new housing needed (excl. homelessness) | Homelessness (allocated) | Total net new housing needed |
|---|---:|---:|---:|---:|---:|
| King | 1,639,260 | 1,060,733 | 578,527 | 22,347 | 600,874 |
| Kitsap | 150,086 | 120,648 | 29,438 | 2,542 | 31,980 |
| Pierce | 531,995 | 381,090 | 150,905 | 8,029 | 158,934 |
| Snohomish | 548,740 | 345,122 | 203,618 | 7,271 | 210,889 |
| **Region** | **2,870,081** | **1,907,593** | **962,488** | **40,188** | **1,002,676** |

## Component 1: Housing to eliminate baseline renter cost burden

A cost-burdened household spends more than 30% of its income on housing, which indicates a shortage of housing affordable at that household's income level. Only renter households are included, because owners hold equity in their homes and have other options available to them.

The calculation has three steps:

1. **Scale CHAS households to current levels.** CHAS counts cost-burdened renters at each income level for 2018-2022. These counts are scaled up to match current OFM household estimates, using one ratio per county (current OFM households divided by total CHAS households). The scaling ratios are 1.10 for King, 1.06 for Kitsap, 1.05 for Pierce and 1.07 for Snohomish. CHAS reports all cost-burdened households above 100% AMI as one group, and all of them are assigned to the >100-120% AMI level.
2. **Build housing over time.** One twenty-fifth of the need at each income level is built each year, which assumes the existing backlog is eliminated over 25 years (by 2050) rather than the full 2025-2060 projection period. The remaining years of the projection are assumed to add only housing for population growth. A new unit at a given income level houses one cost-burdened household (accounting for the vacancy rate, so that about 95% of new units are occupied).
3. **Account for vacated units.** The household that moves into a new unit leaves a unit behind. CHAS Table 18C shows what affordability level the units occupied by renter households at each income level have, which determines the affordability of the vacated unit. The vacated unit becomes available to another cost-burdened household, who in turn vacates a unit, and so on until no cost-burdened renter households remain. These vacated units reduce the number of new units needed at higher income levels.

Cost-burdened households are assumed to live in units priced above their income band, so no units affordable at 0-30% AMI are vacated and the entire need at 0-30% AMI must be met by new production.

**Table 2. Cost-burdened renter households scaled to 2025 OFM estimates**

| Income level (% of AMI) | King | Kitsap | Pierce | Snohomish | Region |
|---|---:|---:|---:|---:|---:|
| 0-30% | 67,026 | 5,161 | 17,434 | 18,435 | 108,056 |
| >30-50% | 52,080 | 3,917 | 16,591 | 15,271 | 87,859 |
| >50-80% | 43,310 | 4,730 | 20,349 | 12,065 | 80,454 |
| >80-100% | 13,467 | 1,408 | 4,301 | 2,569 | 21,745 |
| >100-120% | 9,740 | 611 | 1,945 | 963 | 13,259 |
| **Total** | **185,623** | **15,827** | **60,620** | **49,303** | **311,373** |

**Table 3. New production to address renter cost burden**

| Income level (% of AMI) | King | Kitsap | Pierce | Snohomish | Region |
|---|---:|---:|---:|---:|---:|
| 0-30% | 70,785 | 5,524 | 18,442 | 19,318 | 114,069 |
| >30-50% | 41,550 | 3,019 | 14,040 | 11,732 | 70,341 |
| >50-80% | 16,466 | 2,228 | 9,719 | 4,046 | 32,459 |
| >80-100% | 569 | 60 | 182 | 108 | 919 |
| >100-120% | 411 | 26 | 82 | 40 | 559 |
| **Total** | **129,781** | **10,857** | **42,465** | **35,244** | **218,347** |

**Table 4. Units vacated that address cost-burden need**

| Income level (% of AMI) | King | Kitsap | Pierce | Snohomish | Region |
|---|---:|---:|---:|---:|---:|
| 0-30% | 0 | 0 | 0 | 0 | 0 |
| >30-50% | 13,451 | 1,174 | 3,510 | 4,270 | 22,405 |
| >50-80% | 29,273 | 2,835 | 11,806 | 8,597 | 52,511 |
| >80-100% | 13,653 | 1,447 | 4,368 | 2,584 | 22,052 |
| >100-120% | 9,875 | 628 | 1,975 | 969 | 13,447 |
| **Total** | **66,252** | **6,084** | **21,659** | **16,420** | **110,415** |

Cost burden is concentrated at the lowest incomes. At 0-30% AMI, new production is larger than the number of cost-burdened households (for example, 70,785 new units for 67,026 households in King County), because about 5% of new units remain vacant. At 80% AMI and above, almost all of the need is met by units vacated at lower income levels.

## Component 2: Housing for the baseline homeless population

PSRC estimates that 40,188 households in the region are experiencing homelessness and need permanent housing. This estimate is only available at the regional level, so it is allocated to counties in proportion to each county's share of the region's 2025 housing units.

Following Commerce's assumption, 90% of these households need housing affordable at 0-30% AMI and 10% need housing affordable at >30-50% AMI. No homeless housing need is assigned to higher income levels.

**Table 5. Housing needed for households experiencing homelessness**

| County | Housing units, 2025 | Households experiencing homelessness (allocated) | 0-30% AMI (90%) | >30-50% AMI (10%) |
|---|---:|---:|---:|---:|
| King | 1,060,733 | 22,347 | 20,112 | 2,235 |
| Kitsap | 120,648 | 2,542 | 2,288 | 254 |
| Pierce | 381,090 | 8,029 | 7,226 | 803 |
| Snohomish | 345,122 | 7,271 | 6,544 | 727 |
| **Region** | **1,907,593** | **40,188** | **36,170** | **4,019** |

## Component 3: Additional housing to accommodate population growth

The first two components address baseline needs. The remaining net new housing is needed for population growth. It is calculated as the total net new housing need (Table 1) minus the housing for cost burden (Table 3) and the housing for homelessness (Table 5).

**Table 6. Additional housing to accommodate population growth, 2025-2060**

| County | Total net new housing needed | Cost burden | Homelessness | Population growth |
|---|---:|---:|---:|---:|
| King | 600,874 | 129,781 | 22,347 | 448,746 |
| Kitsap | 31,980 | 10,857 | 2,542 | 18,581 |
| Pierce | 158,934 | 42,465 | 8,029 | 108,440 |
| Snohomish | 210,889 | 35,244 | 7,271 | 168,374 |
| **Region** | **1,002,676** | **218,347** | **40,188** | **744,141** |

Future household growth is assumed to occur across the entire income spectrum, with the same shares at each income level as today's households. The shares come from CHAS households by income level. CHAS groups all households above 100% AMI together, so PUMS is used to split that group into >100-120% and >120% AMI. Each household's income is compared to the HUD FY2024 median family income for its county, adjusted for household size (70% of the 4-person median for a 1-person household, up to 132% for 8 or more people).

**Table 7. Share of households by income level**

| County | 0-30% AMI | >30-50% AMI | >50-80% AMI | >80-100% AMI | >100-120% AMI | >120% AMI |
|---|---:|---:|---:|---:|---:|---:|
| King | 12.5% | 10.0% | 12.8% | 9.2% | 8.5% | 47.0% |
| Kitsap | 10.2% | 8.8% | 17.6% | 11.4% | 10.6% | 41.4% |
| Pierce | 9.9% | 9.9% | 17.8% | 11.5% | 10.4% | 40.5% |
| Snohomish | 12.1% | 11.7% | 15.8% | 11.6% | 10.0% | 39.0% |

These shares are applied to each county's population growth component (Table 6) to distribute it across income levels.

If the first two components were ever larger than the total net new need, the total would be raised to equal them, population growth would be zero and no need would be assigned above 120% AMI. This did not occur in any of the four counties.

## Total net new housing need by income level

For each income level, the three components are added together. The totals across income levels equal the total net new housing need in Table 1.

**Table 8. Total net new housing need by income level, 2025-2060**

| Income level (% of AMI) | King | Kitsap | Pierce | Snohomish | Region |
|---|---:|---:|---:|---:|---:|
| 0-30% | 146,961 | 9,699 | 36,368 | 46,200 | 239,228 |
| >30-50% | 88,544 | 4,913 | 25,603 | 32,085 | 151,145 |
| >50-80% | 73,926 | 5,490 | 29,001 | 30,661 | 139,078 |
| >80-100% | 41,956 | 2,179 | 12,681 | 19,562 | 76,378 |
| >100-120% | 38,650 | 1,999 | 11,390 | 16,794 | 68,833 |
| >120% | 210,838 | 7,700 | 43,890 | 65,588 | 328,016 |
| **Total** | **600,874** | **31,980** | **158,934** | **210,889** | **1,002,676** |

**Table 9. Regional net new housing need by component and income level, 2025-2060**

| Income level (% of AMI) | Eliminate renter cost burden | Homelessness | Population growth | Total |
|---|---:|---:|---:|---:|
| 0-30% | 114,069 | 36,170 | 88,989 | 239,228 |
| >30-50% | 70,341 | 4,019 | 76,785 | 151,145 |
| >50-80% | 32,459 | 0 | 106,619 | 139,078 |
| >80-100% | 919 | 0 | 75,459 | 76,378 |
| >100-120% | 559 | 0 | 68,274 | 68,833 |
| >120% | 0 | 0 | 328,016 | 328,016 |
| **Total** | **218,347** | **40,188** | **744,141** | **1,002,676** |

*Tables may not sum exactly due to rounding.*

About 24% of the region's net new housing need is at 0-30% AMI and a further 15% is at >30-50% AMI. Cost burden and homelessness are the largest drivers of need at those levels: together they account for 63% of the need at 0-30% AMI. At 80% AMI and above, the need is almost entirely driven by population growth.

## Key assumptions

- Cost-burdened households are assumed to live in units priced above their income band when estimating which units are vacated.
- Cost-burdened households with incomes above 100% AMI are all assumed to be in the >100-120% AMI level, because that is how CHAS reports them.
- Units above 80% AMI that are vacated are split between the >80-100% and >100-120% levels in proportion to the remaining need.
- Homeless housing need is allocated to counties by share of housing units, and 90% of it is assumed to need 0-30% AMI housing and 10% to need >30-50% AMI housing.
- The distribution of future household growth by income level is assumed to remain the same as today's distribution of households.
- Housing units lost to demolition, and loss of affordability over time, are not modeled.
- Vacation homes and migrant worker housing are not removed from the 2025 housing unit count.
- Needs for permanent supportive housing and emergency housing are not separated from the 0-30% AMI level.
