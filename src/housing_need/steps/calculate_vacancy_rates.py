from pathlib import Path

import pandas as pd


def calculate_vacancy_rates(vacancy_inputs):
    """Return vacancy rate (1 - occupied_units / total_units) per county."""
    df = vacancy_inputs.copy()
    df['vacancy_rate'] = 1 - df['occupied_units'] / df['total_units']
    return df[['county_id', 'year', 'vacancy_rate']]


def run_step(context):
    intermediate_dir = Path(context['output_dir']) / "intermediate"
    vacancy_inputs = pd.read_csv(intermediate_dir / "vacancy_rate_inputs.csv")

    vacancy_rates = calculate_vacancy_rates(vacancy_inputs)
    vacancy_rates.to_csv(intermediate_dir / "vacancy_rates.csv", index=False)

    return context
