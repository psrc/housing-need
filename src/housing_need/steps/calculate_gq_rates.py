from pathlib import Path

import pandas as pd


def calculate_gq_rates(gq_inputs):
    """Return group-quarters rate (gq_pop / total_pop) per county and age group."""
    df = gq_inputs.copy()
    df['gq_rate'] = df['gq_pop'] / df['total_pop']
    return df[['county_id', 'age_group', 'year', 'gq_rate']]


def run_step(context):
    intermediate_dir = Path(context['output_dir']) / "intermediate"
    gq_inputs = pd.read_csv(intermediate_dir / "gq_rate_inputs.csv")

    gq_rates = calculate_gq_rates(gq_inputs)
    gq_rates.to_csv(intermediate_dir / "gq_rates.csv", index=False)

    return context
