import re
from pathlib import Path

import pandas as pd

# REMI population figures are reported in thousands.
REMI_POP_SCALE = 1000

# Aggregated 10-year age bins matching the age groups used elsewhere in the pipeline.
_AGE_BIN_EDGES = [
    (0, 14),
    (15, 24),
    (25, 34),
    (35, 44),
    (45, 54),
    (55, 64),
    (65, 74),
    (75, 84),
]


def _parse_age_group(category):
    """Convert a REMI category like 'Population - Ages 25-29 - All Races - Total'
    into an aggregated age group label such as 'age_25_34' (or 'age_85_plus')."""
    match = re.search(r"Ages\s+(\d+)(?:-(\d+))?(\+)?", str(category))
    if not match:
        return None
    start, plus = match.group(1), match.group(3)
    if plus:
        return "age_85_plus"
    start = int(start)
    for lo, hi in _AGE_BIN_EDGES:
        if lo <= start <= hi:
            return f"age_{lo}_{hi}"
    return None


def clean_remi_forecast(remi_path, county_map):
    """Read the REMI workbook and return a long DataFrame with columns
    [county_id, age_group, year, total_pop], with population scaled to people."""
    df = pd.read_excel(remi_path, sheet_name="All", header=5)
    df = df.rename(columns={df.columns[0]: "region", df.columns[1]: "category"})
    year_cols = list(df.columns[3:])

    pop = df[df["category"].astype(str).str.startswith("Population - Ages")].copy()
    pop["county_id"] = pop["region"].map(county_map)
    pop["age_group"] = pop["category"].map(_parse_age_group)
    pop = pop.dropna(subset=["county_id", "age_group"])
    pop["county_id"] = pop["county_id"].astype(int)

    long = pop.melt(
        id_vars=["county_id", "age_group"],
        value_vars=year_cols,
        var_name="year",
        value_name="total_pop",
    )
    long["year"] = long["year"].astype(float).astype(int)
    long["total_pop"] = long["total_pop"].astype(float) * REMI_POP_SCALE

    # Multiple 5-year REMI categories map to the same 10-year age_group bin.
    long = long.groupby(["county_id", "age_group", "year"], as_index=False)["total_pop"].sum()
    return long.sort_values(["year", "county_id", "age_group"]).reset_index(drop=True)


def run_step(context):
    output_dir = context["output_dir"]
    remi_forecast_dir = context["remi_forecast_dir"]
    county_map = context["county_map"]
    remi_path = Path(remi_forecast_dir) / context["remi_forecast"]

    remi_pop = clean_remi_forecast(remi_path, county_map)

    intermediate_dir = Path(output_dir) / "intermediate"
    intermediate_dir.mkdir(parents=True, exist_ok=True)
    remi_pop.to_csv(intermediate_dir / "remi_forecast.csv", index=False)
    return context
