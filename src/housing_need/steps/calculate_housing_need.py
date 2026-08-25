from pathlib import Path

import pandas as pd

# total_pop and ofm_current_housing_units are observed values; everything else is derived by
# applying gq/headship/vacancy rates (each from their own base year) to that population, so we
# label those columns "est_" to make clear they are model estimates, not reported figures.
ESTIMATED_COLUMN_LABELS = {
    "gq_pop": "est_gq_pop",
    "hhpop": "est_hhpop",
    "hh": "est_hh",
    "occupancy_rate": "est_occupancy_rate",
    "total_housing_need": "est_total_housing_need",
}


def calculate_hhpop(pop, gq_rates):
    """Apply group-quarters rates to total population to estimate household population."""
    rates = gq_rates[["county_id", "age_group", "gq_rate"]]
    pop = pop.merge(rates, on=["county_id", "age_group"], how="left")
    pop["gq_rate"] = pop["gq_rate"].fillna(0)
    pop["gq_pop"] = pop["total_pop"] * pop["gq_rate"]
    pop["hhpop"] = pop["total_pop"] - pop["gq_pop"]
    return pop


def calculate_hh(pop, headship_rates):
    """Apply headship rates to household population to estimate households, by age group."""
    rates = headship_rates[["county_id", "age_group", "headship_rate"]]
    pop = pop.merge(rates, on=["county_id", "age_group"], how="left")
    pop["headship_rate"] = pop["headship_rate"].fillna(0)
    pop["hh"] = pop["hhpop"] * pop["headship_rate"]
    return pop


def calculate_housing_units(pop, vacancy_rates):
    """Apply vacancy rates (by county) to households to estimate occupancy rate and total housing need."""
    rates = vacancy_rates[["county_id", "vacancy_rate"]]
    pop = pop.merge(rates, on="county_id", how="left")
    pop["occupancy_rate"] = 1 - pop["vacancy_rate"]
    pop["total_housing_need"] = pop["hh"] / pop["occupancy_rate"]
    return pop.drop(columns="vacancy_rate")


def calculate_housing_need(pop, gq_rates, headship_rates, vacancy_rates):
    """Chain group-quarters, headship, and vacancy calculations into a single housing-need
    table, keeping the county and age group disaggregations."""
    pop = calculate_hhpop(pop, gq_rates)
    pop = calculate_hh(pop, headship_rates)
    pop = calculate_housing_units(pop, vacancy_rates)
    cols = [
        "county_id", "year", "age_group",
        "total_pop", "gq_rate", "gq_pop", "hhpop", "headship_rate", "hh",
        "occupancy_rate", "total_housing_need",
    ]
    return pop[cols].sort_values(["year", "county_id", "age_group"]).reset_index(drop=True)


def calculate_summary(housing_need, ofm_housing, ofm_year, forecast_year, county_map):
    """Reduce the age-group/year detail to one row per county (plus a regional total), with
    the OFM current housing units, resulting shortage, and total housing need for each year
    as separate columns."""
    totals = housing_need.groupby(["county_id", "year"], as_index=False)["total_housing_need"].sum()
    region = totals.groupby("year", as_index=False)["total_housing_need"].sum()
    region.insert(0, "county_id", "Region")
    totals = pd.concat([totals, region], ignore_index=True)

    ofm_col = f"est_total_housing_need_{ofm_year}"
    forecast_col = f"est_total_housing_need_{forecast_year}"
    summary = totals.pivot(index="county_id", columns="year", values="total_housing_need").reset_index()
    summary = summary.rename(columns={ofm_year: ofm_col, forecast_year: forecast_col})

    region_housing_units = pd.DataFrame(
        {"county_id": ["Region"], "ofm_current_housing_units": [ofm_housing["ofm_current_housing_units"].sum()]}
    )
    ofm_housing = pd.concat([ofm_housing, region_housing_units], ignore_index=True)
    summary = summary.merge(ofm_housing, on="county_id", how="left")
    summary["est_housing_shortage"] = summary[ofm_col] - summary["ofm_current_housing_units"]

    id_to_name = {county_id: name for name, county_id in county_map.items()}
    summary["county"] = summary["county_id"].map(id_to_name).fillna("Region")

    cols = ["county", "county_id", "ofm_current_housing_units", "est_housing_shortage", ofm_col, forecast_col]
    summary = summary[cols]
    county_sort_key = pd.to_numeric(summary["county_id"], errors="coerce")
    summary = (
        summary.assign(_sort=county_sort_key)
        .sort_values("_sort", na_position="last")
        .drop(columns=["_sort", "county_id"])
        .reset_index(drop=True)
    )
    return summary.rename(columns={
        "county": "County",
        "ofm_current_housing_units": f"OFM Current Housing Units {ofm_year}",
        "est_housing_shortage": "Est. Current Housing Shortage",
        ofm_col: f"Est. Total Housing Need {ofm_year}",
        forecast_col: f"Est. Total Housing Need {forecast_year}",
    })


def run_step(context):
    intermediate_dir = Path(context["output_dir"]) / "intermediate"
    gq_rates = pd.read_csv(intermediate_dir / "gq_rates.csv")
    headship_rates = pd.read_csv(intermediate_dir / "headship_rates.csv")
    vacancy_rates = pd.read_csv(intermediate_dir / "vacancy_rates.csv")

    # ofm_pop_estimates.csv holds a single year of population (context['ofm_year']) with no year column.
    ofm_pop = pd.read_csv(intermediate_dir / "ofm_pop_estimates.csv")
    ofm_pop["year"] = context["ofm_year"]

    remi_pop = pd.read_csv(intermediate_dir / "remi_forecast.csv")
    forecast_pop = remi_pop[remi_pop["year"] == context["forecast_year"]]

    pop = pd.concat([ofm_pop, forecast_pop], ignore_index=True)
    housing_need = calculate_housing_need(pop, gq_rates, headship_rates, vacancy_rates)

    ofm_housing = pd.read_csv(intermediate_dir / "ofm_housing_estimates.csv").rename(
        columns={"total_housing_units": "ofm_current_housing_units"}
    )
    summary = calculate_summary(
        housing_need, ofm_housing, context["ofm_year"], context["forecast_year"], context["county_map"]
    )

    output_path = Path(context["output_dir"]) / "housing_need.xlsx"
    with pd.ExcelWriter(output_path) as writer:
        housing_need.rename(columns=ESTIMATED_COLUMN_LABELS).to_excel(writer, sheet_name="data", index=False)
        summary.to_excel(writer, sheet_name="summary", index=False)

    return context
