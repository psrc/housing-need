"""Summarizes homelessness-related housing need into a single check table.

Combines the region-wide sheltered/unsheltered household estimates from
calculate_hh_from_pit with the doubled-up household estimates from
calculate_k12_doubled_up and calculate_non_k12_doubled_up, so the four
components and their total can be checked in one place.
"""

import os

import pandas as pd


def load_pit_totals(context):
    """Region-level sheltered/unsheltered household estimates from the PIT step's output."""
    intermediate_dir = os.path.join(context['output_dir'], 'intermediate')
    pit = pd.read_csv(os.path.join(intermediate_dir, 'pit_homeless_to_hh.csv'))
    region = pit.loc[pit['county'] == 'Region'].iloc[0]
    return region['unsheltered_hh_total'], region['sheltered_hh_total']


def build_summary(unsheltered_hh, sheltered_hh, k12_doubled_up_hh, non_k12_doubled_up_hh):
    """Build the housing-need-by-category table, with a total row summing all four."""
    summary = pd.DataFrame(
        [
            ('Housing need for unsheltered population', unsheltered_hh),
            ('Housing need for sheltered population', sheltered_hh),
            ('Doubled up (with K-12 children)', k12_doubled_up_hh),
            ('Doubled up (no K-12 children)', non_k12_doubled_up_hh),
        ],
        columns=['category', 'housing_need'],
    )
    summary['housing_need'] = summary['housing_need'].round(0).astype(int)

    total = pd.DataFrame([{
        'category': 'Total homelessness housing need estimate',
        'housing_need': summary['housing_need'].sum(),
    }])
    return pd.concat([summary, total], ignore_index=True)


def run_step(context):
    unsheltered_hh, sheltered_hh = load_pit_totals(context)

    summary = build_summary(
        unsheltered_hh,
        sheltered_hh,
        context['doubled_up_households'],
        context['non_k12_doubled_up'],
    )

    output_path = os.path.join(context['output_dir'], 'intermediate', 'homelessness_housing_need_summary.csv')
    summary.to_csv(output_path, index=False)
    return context
