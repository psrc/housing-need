"""Calculates housing need using current age group proportions applied to
the forecast year population. Still uses past headship rates so it
includes any un-doubling up of households that an increase in supply
would bring.
"""

from pathlib import Path

import pandas as pd


def calculate_future_population(ofm_pop, remi_forecast, forecast_year):
    """Distribute the REMI county population forecast across age groups using
    each county's current OFM age-group proportions."""
    ofm_pop = ofm_pop.copy()
    ofm_pop['pop_pct'] = ofm_pop['total_pop'] / ofm_pop.groupby('county_id')['total_pop'].transform('sum')

    remi_totals = (
        remi_forecast.loc[remi_forecast['year'] == forecast_year]
        .groupby('county_id')['total_pop'].sum()
        .rename('remi_total_pop')
    )
    ofm_pop = ofm_pop.merge(remi_totals, on='county_id', how='left')
    ofm_pop['pop_future'] = (ofm_pop['pop_pct'] * ofm_pop['remi_total_pop']).round(0).astype(int)
    return ofm_pop.drop(columns=['pop_pct', 'remi_total_pop'])


def calculate_future_households(pop, headship_rates, headship_rates_year):
    """Apply headship rates for the given year to future population, by age group."""
    rates = headship_rates.loc[
        headship_rates['year'] == headship_rates_year, ['county_id', 'age_group', 'headship_rate']
    ]
    pop = pop.merge(rates, on=['county_id', 'age_group'], how='left')
    pop['hh_future'] = (pop['pop_future'] * pop['headship_rate']).round(0).fillna(0).astype(int)
    return pop


def calculate_future_units(pop, vacancy_rates, vacancy_rates_year):
    """Apply vacancy rates for the given year to future households, by county."""
    rates = vacancy_rates.loc[vacancy_rates['year'] == vacancy_rates_year, ['county_id', 'vacancy_rate']]
    pop = pop.merge(rates, on='county_id', how='left')
    pop['units_future'] = (pop['hh_future'] / (1 - pop['vacancy_rate'])).round(0).fillna(0).astype(int)
    return pop


def calculate_demographic_future_households(remi_forecast, forecast_year, headship_rates, headship_rates_year):
    """Apply headship rates for the given year directly to the REMI forecast population, so the
    age structure reflects REMI's own demographic change instead of OFM's current age mix."""
    pop = remi_forecast.loc[remi_forecast['year'] == forecast_year].rename(columns={'total_pop': 'pop_future'})
    return calculate_future_households(pop, headship_rates, headship_rates_year)


def run_step(context):
    intermediate_dir = Path(context['output_dir']) / "intermediate"
    ofm_pop = pd.read_csv(intermediate_dir / "ofm_pop_estimates.csv")
    remi_forecast = pd.read_csv(intermediate_dir / "remi_forecast.csv")
    headship_rates = pd.read_csv(intermediate_dir / "headship_rates.csv")
    vacancy_rates = pd.read_csv(intermediate_dir / "vacancy_rates.csv")

    # non-demographic housing need
    future_pop = calculate_future_population(ofm_pop, remi_forecast, context['forecast_year'])
    pop = calculate_future_households(future_pop, headship_rates, context['headship_rates_year'])
    pop = calculate_future_units(pop, vacancy_rates, context['vacancy_rates_year'])

    output = pop[['county_id', 'age_group', 'units_future']].rename(
        columns={'units_future': 'non_demographic_housing_need'}
    )
    output.to_csv(intermediate_dir / "non_demographic_housing_need.csv", index=False)

    # non-demographic housing need using most recent decennial year headship rates, starting
    # fresh from future_pop so the earlier headship/vacancy columns aren't merged twice.
    pop = calculate_future_households(future_pop, headship_rates, context['most_recent_decennial_year'])
    pop = calculate_future_units(pop, vacancy_rates, context['vacancy_rates_year'])

    output = pop[['county_id', 'age_group', 'units_future']].rename(
        columns={'units_future': f'non_demographic_{context["most_recent_decennial_year"]}_hr_rates'}
    )
    output.to_csv(intermediate_dir / f"non_demographic_{context['most_recent_decennial_year']}_hr_rates.csv", index=False)

    # demographic housing need with most recent decennial headship rate
    pop = calculate_demographic_future_households(
        remi_forecast, context['forecast_year'], headship_rates, context['most_recent_decennial_year']
    )
    pop = calculate_future_units(pop, vacancy_rates, context['vacancy_rates_year'])

    output = pop[['county_id', 'age_group', 'units_future']].rename(
        columns={'units_future': 'demographic_housing_need'}
    )
    output.to_csv(intermediate_dir / f"demographic_housing_need_{context['most_recent_decennial_year']}_hr_rates.csv", index=False)

    return context