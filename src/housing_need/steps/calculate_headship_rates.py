from pathlib import Path

import pandas as pd


def calculate_headship_rates(headship_inputs):
    """Return headship rate (householders / pop_in_households) per county and age group."""
    df = headship_inputs.copy()
    df['headship_rate'] = df['householders'] / df['pop_in_households']
    return df[['county_id', 'age_group', 'year', 'headship_rate']]


def run_step(context):
    intermediate_dir = Path(context['output_dir']) / "intermediate"
    headship_inputs = pd.read_csv(intermediate_dir / "headship_rate_inputs.csv")

    headship_rates = calculate_headship_rates(headship_inputs)
    headship_rates.to_csv(intermediate_dir / "headship_rates.csv", index=False)

    return context
