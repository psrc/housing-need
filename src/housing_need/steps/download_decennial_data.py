import os
import pandas as pd
from pathlib import Path

from housing_need.util import CensusApi, YEAR_CONFIG, GQ_YEAR_CONFIG, VACANCY_YEAR_CONFIG


def fetch_age_table(census_api, cols_dict, year, dataset, county_ids, state_id):
    """Pull a decennial table and return a long DataFrame with one row per
    county/age group. Age groups match AGE_GROUP_MAP in clean_ofm_estimates.py."""
    df = census_api.get_dec_data(cols_dict, year, 'county', dataset, county_ids, state_id)
    df = (
        df.loc[df['geoid'].isin(county_ids)]
        .drop(columns=['name'])
        .rename(columns={'geoid': 'county_id'})
        .melt(id_vars='county_id', var_name='age_group', value_name='value')
    )
    return df


def download_gq_inputs(census_api, year, county_ids, state_id):
    """Fetch total population and group-quarters population by age group,
    for computing group-quarters rates (gq_pop / total_pop)."""
    if year not in GQ_YEAR_CONFIG:
        raise ValueError(
            f"No group-quarters age tables configured for {year}. "
            f"Supported years: {sorted(GQ_YEAR_CONFIG)}"
        )
    total_dataset, total_cols = GQ_YEAR_CONFIG[year]['total_pop']
    gq_dataset, gq_cols = GQ_YEAR_CONFIG[year]['gq_pop']

    total_pop = fetch_age_table(census_api, total_cols, year, total_dataset, county_ids, state_id)
    total_pop = total_pop.rename(columns={'value': 'total_pop'})
    gq_pop = fetch_age_table(census_api, gq_cols, year, gq_dataset, county_ids, state_id)
    gq_pop = gq_pop.rename(columns={'value': 'gq_pop'})

    df = total_pop.merge(gq_pop, on=['county_id', 'age_group'])
    df['year'] = year
    return df


def download_headship_inputs(census_api, year, county_ids, state_id):
    """Fetch householders and population-in-households by age group, for
    computing headship rates (householders / pop_in_households)."""
    if year not in YEAR_CONFIG:
        raise ValueError(
            f"No headship-rate age tables configured for {year}. "
            f"Supported years: {sorted(YEAR_CONFIG)}"
        )
    hh_dataset, hh_cols = YEAR_CONFIG[year]['hh']
    pop_dataset, pop_cols = YEAR_CONFIG[year]['pop']

    householders = fetch_age_table(census_api, hh_cols, year, hh_dataset, county_ids, state_id)
    householders = householders.rename(columns={'value': 'householders'})
    pop_in_hh = fetch_age_table(census_api, pop_cols, year, pop_dataset, county_ids, state_id)
    pop_in_hh = pop_in_hh.rename(columns={'value': 'pop_in_households'})

    df = householders.merge(pop_in_hh, on=['county_id', 'age_group'])
    df['year'] = year
    return df


def download_vacancy_inputs(census_api, year, county_ids, state_id):
    """Fetch total and occupied housing units by county, for computing
    vacancy rates (1 - occupied_units / total_units)."""
    if year not in VACANCY_YEAR_CONFIG:
        raise ValueError(
            f"No vacancy tables configured for {year}. "
            f"Supported years: {sorted(VACANCY_YEAR_CONFIG)}"
        )
    dataset, cols = VACANCY_YEAR_CONFIG[year]
    df = census_api.get_dec_data(cols, year, 'county', dataset, county_ids, state_id)
    df = df.loc[df['geoid'].isin(county_ids)].drop(columns=['name']).rename(columns={'geoid': 'county_id'})
    df['year'] = year
    return df


def run_step(context):
    census_api = CensusApi(os.getenv(context['census_key']), timeout=90)
    county_ids = context['county_ids']
    state_id = context['state_id']

    intermediate_dir = Path(context['output_dir']) / "intermediate"
    intermediate_dir.mkdir(parents=True, exist_ok=True)

    gq_inputs = download_gq_inputs(census_api, context['gq_rates_year'], county_ids, state_id)
    gq_inputs.to_csv(intermediate_dir / "gq_rate_inputs.csv", index=False)

    headship_inputs = download_headship_inputs(
        census_api, context['headship_rates_year'], county_ids, state_id
    )
    headship_inputs_recent = download_headship_inputs(
        census_api, context['most_recent_decennial_year'], county_ids, state_id
    )
    headship_inputs = pd.concat([headship_inputs, headship_inputs_recent], ignore_index=True)
    headship_inputs.to_csv(intermediate_dir / "headship_rate_inputs.csv", index=False)

    vacancy_inputs = download_vacancy_inputs(
        census_api, context['vacancy_rates_year'], county_ids, state_id
    )
    vacancy_inputs.to_csv(intermediate_dir / "vacancy_rate_inputs.csv", index=False)

    return context
    
