"""Converts Point-in-Time (PIT) homeless person counts into household estimates.

The PIT count reports sheltered and unsheltered individuals by county, along with the
share of each group living in families (from the CoC data). We split each county's
sheltered/unsheltered counts into a "family" portion and an "individual" portion using
those shares, then convert the family portion into households by dividing by the average
family household size (calculated from the lowest income quartile of ACS households in
that county, since PIT-counted families are assumed to skew low-income). Individuals are
each counted as their own household. Summing the resulting family and individual household
estimates gives the total sheltered/unsheltered households per county, with a Region row
appended as the sum across all counties.
"""

import os

import pandas as pd


def load_household_data(context):
    """Load ACS household records with county_id and income quartile assigned."""
    intermediate_dir = os.path.join(context['output_dir'], 'intermediate')
    xwalk = pd.read_csv(os.path.join(intermediate_dir, 'puma_geog_lookup_cnty.csv'))
    h = (
        pd.read_csv(os.path.join(intermediate_dir, 'psam_h53.csv'))
        .query('PUMA.isin(@xwalk["PUMA"]) & TYPEHUGQ == 1')
        .copy()
        .assign(
            county_id=lambda df: df['PUMA'].map(xwalk.set_index('PUMA')['county_id']),
            family_income_qrt=lambda df: pd.qcut(df['FINCP'], 4, labels=False) + 1,
        )
    )
    return h


def calculate_avg_household_size(h):
    """Weighted average family size per county, among the lowest income quartile."""
    low_income_families = h.loc[(h['NPF'] > 1) & (h['family_income_qrt'] == 1)]
    num_people = low_income_families.groupby(['county_id', 'NPF'])['WGTP'].sum()

    return (
        num_people
        .rename('WGTP')
        .reset_index()
        .assign(weighted_size=lambda df: df['NPF'] * df['WGTP'])
        .groupby('county_id')
        .apply(lambda df: df['weighted_size'].sum() / df['WGTP'].sum())
    )


def load_county_map(context):
    """Map county names (without the ' County' suffix) to county_id."""
    return {k.replace(' County', ''): v for k, v in context['county_map'].items()}


def load_pit_data(context, counties, avg_household_size):
    """Load PIT homelessness counts joined with family share and avg household size."""
    data_dir = context['data_dir']
    families = (
        pd.read_csv(os.path.join(data_dir, context['data']['homeless_families_counts']))
        [['county', 'pct_in_families_sheltered', 'pct_in_families_unsheltered']]
        .dropna(subset=['county'])
    )

    return (
        pd.read_csv(os.path.join(data_dir, context['data']['current_homelessness_counts']))
        .rename(columns={'County': 'county'})
        .merge(families, on='county', how='left')
        .assign(
            county_id=lambda df: df['county'].map(counties),
            avg_hhsz=lambda df: df['county_id'].map(avg_household_size),
        )
    )


def calculate_household_estimates(pit):
    """Convert PIT person counts into estimated sheltered/unsheltered family and individual households."""
    pit = pit.copy()
    pit['sheltered_families'] = (pit['Sheltered'] * pit['pct_in_families_sheltered']).round(0)
    pit['unsheltered_families'] = (pit['Unsheltered'] * pit['pct_in_families_unsheltered']).round(0)
    pit['sheltered_family_hh'] = (pit['sheltered_families'] / pit['avg_hhsz']).round(0)
    pit['unsheltered_family_hh'] = (pit['unsheltered_families'] / pit['avg_hhsz']).round(0)
    pit['sheltered_individuals'] = (pit['Sheltered'] * (1 - pit['pct_in_families_sheltered'])).round(0)
    pit['unsheltered_individuals'] = (pit['Unsheltered'] * (1 - pit['pct_in_families_unsheltered'])).round(0)
    pit['sheltered_hh_total'] = pit['sheltered_family_hh'] + pit['sheltered_individuals']
    pit['unsheltered_hh_total'] = pit['unsheltered_family_hh'] + pit['unsheltered_individuals']
    return pit


def add_region_row(pit):
    """Append a Region row summing the county-level values."""
    numeric_cols = pit.select_dtypes('number').columns.drop('county_id')
    region = pit[numeric_cols].sum().to_frame().T
    region.insert(0, 'county_id', 'Region')
    region.insert(0, 'county', 'Region')
    return pd.concat([pit, region], ignore_index=True)


def run_step(context):
    h = load_household_data(context)
    avg_household_size = calculate_avg_household_size(h)
    counties = load_county_map(context)

    pit = load_pit_data(context, counties, avg_household_size)
    pit = calculate_household_estimates(pit)
    pit = add_region_row(pit)

    output_path = os.path.join(context['output_dir'], 'intermediate', 'pit_homeless_to_hh.csv')
    pit.to_csv(output_path, index=False)
    return context