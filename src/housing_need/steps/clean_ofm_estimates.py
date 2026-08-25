
from pathlib import Path

import numpy as np
import pandas as pd

# Maps each aggregated age group to the OFM 5-year age brackets it comprises.
AGE_GROUP_MAP = {
    'age_0_14': ['0-4', '5-9', '10-14'],
    'age_15_24': ['15-19', '20-24'],
    'age_25_34': ['25-29', '30-34'],
    'age_35_44': ['35-39', '40-44'],
    'age_45_54': ['45-49', '50-54'],
    'age_55_64': ['55-59', '60-64'],
    'age_65_74': ['65-69', '70-74'],
    'age_75_84': ['75-79', '80-84'],
    'age_85_plus': ['85+'],
}


def _validate_age_group_totals(total_pop, age_pop, rtol=1e-6, atol=1e-3):
    """Raise if the aggregated age groups don't sum back to the OFM total."""
    age_sum = age_pop.groupby(['county_id', 'year'])['total_pop'].sum().reset_index(name='age_sum')
    check = total_pop.merge(age_sum, on=['county_id', 'year'], how='left')
    mismatched = check[~np.isclose(check['total_pop'], check['age_sum'], rtol=rtol, atol=atol)]
    if not mismatched.empty:
        raise ValueError(
            "Age group totals do not match OFM total population:\n"
            f"{mismatched[['county_id', 'year', 'total_pop', 'age_sum']].to_string(index=False)}"
        )


def clean_ofm_estimates(ofm_file_path, county_ids):
    """Read the OFM Total sheet and return the most recent year's population
    by aggregated age group (age_0_14 ... age_85_plus), per county, in long
    format, along with that year.

    Validates that the age groups sum to the OFM-reported total population
    before dropping that total, since it becomes redundant once confirmed."""
    df = pd.read_excel(ofm_file_path, sheet_name='Total')

    # OFM exports pad Area ID/Year/Age Group with trailing whitespace.
    for col in ('Area ID', 'Year', 'Age Group'):
        df[col] = df[col].astype(str).str.strip()
    df['Total'] = pd.to_numeric(df['Total'], errors='coerce')

    county_ids_str = [str(county_id) for county_id in county_ids]
    df = df[df['Area ID'].isin(county_ids_str)]

    total_pop = (
        df.loc[df['Age Group'] == 'Total', ['Area ID', 'Year', 'Total']]
        .rename(columns={'Area ID': 'county_id', 'Year': 'year', 'Total': 'total_pop'})
    )
    total_pop['county_id'] = total_pop['county_id'].astype('int64')
    total_pop['year'] = total_pop['year'].astype('int64')

    bracket_to_group = {
        bracket: group for group, brackets in AGE_GROUP_MAP.items() for bracket in brackets
    }
    age_df = df[df['Age Group'].isin(bracket_to_group)].copy()
    age_df['age_group'] = age_df['Age Group'].map(bracket_to_group)

    age_pop = (
        age_df.groupby(['Area ID', 'Year', 'age_group'])['Total']
        .sum()
        .reset_index()
        .rename(columns={'Area ID': 'county_id', 'Year': 'year', 'Total': 'total_pop'})
    )
    age_pop['county_id'] = age_pop['county_id'].astype('int64')
    age_pop['year'] = age_pop['year'].astype('int64')

    _validate_age_group_totals(total_pop, age_pop)

    latest_year = int(age_pop['year'].max())
    age_pop = age_pop.loc[age_pop['year'] == latest_year].drop(columns='year')
    age_pop['age_group'] = pd.Categorical(
        age_pop['age_group'], categories=list(AGE_GROUP_MAP.keys()), ordered=True
    )
    age_pop = age_pop.sort_values(['county_id', 'age_group']).reset_index(drop=True)
    return latest_year, age_pop


def clean_ofm_housing_estimates(ofm_housing_path, county_map, year):
    """Read the OFM Housing Units sheet and return total housing units per county for the given year."""
    df = pd.read_excel(ofm_housing_path, sheet_name='Housing Units', header=3)

    # Column names vary by year (e.g. "Base Census Estimate" vs "Postcensal Estimate", footnote marks).
    year_col = next(
        (col for col in df.columns if str(col).strip().startswith(str(year)) and 'Total Housing Units' in col),
        None,
    )
    if year_col is None:
        raise ValueError(f"No 'Total Housing Units' column found for year {year} in {ofm_housing_path}")

    # County-level rows are the ones whose Jurisdiction is "<County> County" (e.g. "King County").
    df = df[df['Jurisdiction'].isin(county_map)].copy()
    df['county_id'] = df['Jurisdiction'].map(county_map)
    df = df.rename(columns={year_col: 'total_housing_units'})
    return df[['county_id', 'total_housing_units']].sort_values('county_id').reset_index(drop=True)


def run_step(context):
    data_dir = context['data_dir']
    output_dir = context['output_dir']
    county_ids = context['county_ids']
    county_map = context['county_map']
    ofm_pop_path = Path(data_dir) / context['data']['ofm_population_estimates']
    ofm_housing_path = Path(data_dir) / context['data']['ofm_housing_estimates']

    ofm_year, pop_df = clean_ofm_estimates(ofm_pop_path, county_ids)
    context['ofm_year'] = ofm_year

    housing_df = clean_ofm_housing_estimates(ofm_housing_path, county_map, ofm_year)

    intermediate_dir = Path(output_dir) / "intermediate"
    intermediate_dir.mkdir(parents=True, exist_ok=True)
    pop_df.to_csv(intermediate_dir / "ofm_pop_estimates.csv", index=False)
    housing_df.to_csv(intermediate_dir / "ofm_housing_estimates.csv", index=False)
    return context
