"""Estimates housing need and current shortage by county.

Current population by age group is split into group-quarters and household population
using group-quarters rates, then 2000 headship rates (household formation rates by age,
from a period before household formation was suppressed by housing scarcity) are applied
to household population to estimate how many households would form absent that
constraint. Applying vacancy rates converts households into total housing units needed.
Comparing this estimated need against OFM's current housing unit counts for the same year
yields the "housing shortage" - how many additional units would be needed for headship
rates to return to their 2000 levels. The same rates are also applied to a population
forecast for a future year to estimate long-run housing need.
"""

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


def calculate_summary(housing_need, ofm_housing, ofm_year, forecast_year, county_map, homelessness_need):
    """Reduce the age-group/year detail to one row per county (plus a regional total), with
    the OFM current housing units, resulting shortage, and total housing need for each year
    as separate columns. Homelessness housing need is only estimated at the regional level,
    so the columns that fold it in are left blank for individual counties."""
    totals = housing_need.groupby(["county_id", "year"], as_index=False)["total_housing_need"].sum()
    region = totals.groupby("year", as_index=False)["total_housing_need"].sum()
    region.insert(0, "county_id", "Region")
    totals = pd.concat([totals, region], ignore_index=True)

    ofm_col = f"est_total_housing_need_{ofm_year}"
    forecast_col = f"est_total_housing_need_{forecast_year}"
    ofm_incl_homeless_col = f"{ofm_col}_incl_homelessness"
    forecast_incl_homeless_col = f"{forecast_col}_incl_homelessness"
    summary = totals.pivot(index="county_id", columns="year", values="total_housing_need").reset_index()
    summary = summary.rename(columns={ofm_year: ofm_col, forecast_year: forecast_col})

    region_housing_units = pd.DataFrame(
        {"county_id": ["Region"], "ofm_current_housing_units": [ofm_housing["ofm_current_housing_units"].sum()]}
    )
    ofm_housing = pd.concat([ofm_housing, region_housing_units], ignore_index=True)
    summary = summary.merge(ofm_housing, on="county_id", how="left")
    summary["est_housing_shortage"] = summary[ofm_col] - summary["ofm_current_housing_units"]
    summary["est_total_growth_need"] = summary[forecast_col] - summary["ofm_current_housing_units"]
    n_forecast_years = forecast_year - ofm_year
    summary["est_avg_annual_need"] = summary["est_total_growth_need"] / n_forecast_years

    is_region = summary["county_id"] == "Region"
    summary["est_shortage_from_homelessness"] = float("nan")
    summary.loc[is_region, "est_shortage_from_homelessness"] = homelessness_need
    summary["est_total_current_shortage"] = summary["est_housing_shortage"] + summary["est_shortage_from_homelessness"]
    summary[ofm_incl_homeless_col] = summary[ofm_col] + summary["est_shortage_from_homelessness"]
    summary[forecast_incl_homeless_col] = summary[forecast_col] + summary["est_shortage_from_homelessness"]
    summary["est_total_growth_incl_homelessness"] = (
        summary["est_total_growth_need"] + summary["est_shortage_from_homelessness"]
    )
    summary["est_avg_annual_incl_homelessness"] = summary["est_total_growth_incl_homelessness"] / n_forecast_years
    # Only reported for the region, since it's a breakdown of the region-only growth/homelessness check above.
    summary["est_forecast_not_incl_shortage"] = (summary[forecast_col] - summary[ofm_col]).where(is_region)

    id_to_name = {county_id: name for name, county_id in county_map.items()}
    summary["county"] = summary["county_id"].map(id_to_name).fillna("Region")

    cols = [
        "county", "county_id", "ofm_current_housing_units",
        "est_housing_shortage", "est_shortage_from_homelessness", "est_total_current_shortage",
        ofm_col, ofm_incl_homeless_col,
        forecast_col, "est_forecast_not_incl_shortage", forecast_incl_homeless_col,
        "est_avg_annual_need", "est_total_growth_need",
        "est_total_growth_incl_homelessness", "est_avg_annual_incl_homelessness",
    ]
    summary = summary[cols]
    county_sort_key = pd.to_numeric(summary["county_id"], errors="coerce")
    summary = (
        summary.assign(_sort=county_sort_key)
        .sort_values("_sort", na_position="last")
        .drop(columns=["_sort", "county_id"])
        .reset_index(drop=True)
    )
    years = f"{ofm_year}-{forecast_year}"
    return summary.rename(columns={
        "county": "County",
        "ofm_current_housing_units": f"OFM Current Housing Units {ofm_year}",
        "est_housing_shortage": "Est. Current Housing Shortage",
        "est_shortage_from_homelessness": "Est. Current Shortage from Homelessness",
        "est_total_current_shortage": "Est. Total Current Housing Shortage",
        ofm_col: f"Est. Total Housing Need {ofm_year}",
        ofm_incl_homeless_col: f"Est. Total Housing Need {ofm_year} (incl. Homelessness)",
        forecast_col: f"Est. Total Housing Need {forecast_year}",
        "est_forecast_not_incl_shortage": f"Est. Housing Need {forecast_year} (not incl. current shortage)",
        forecast_incl_homeless_col: f"Est. Total Housing Need {forecast_year} (incl. Homelessness)",
        "est_avg_annual_need": f"Avg. Annual Housing Need {years}",
        "est_total_growth_need": f"Est. Total Housing Growth/Need {years}",
        "est_total_growth_incl_homelessness": f"Est. Total Housing Growth/Need {years} (incl. Homelessness)",
        "est_avg_annual_incl_homelessness": f"Avg. Annual Housing Need {years} (incl. Homelessness)",
    })


def load_homelessness_summary(intermediate_dir):
    """Region-wide housing need by homelessness category, computed in sum_need_from_homelessness."""
    return pd.read_csv(intermediate_dir / "homelessness_housing_need_summary.csv")


def run_step(context):
    intermediate_dir = Path(context["output_dir"]) / "intermediate"
    gq_rates = pd.read_csv(intermediate_dir / "gq_rates.csv")
    headship_rates = pd.read_csv(intermediate_dir / "headship_rates.csv")
    vacancy_rates = pd.read_csv(intermediate_dir / "vacancy_rates.csv")
    homelessness_summary = load_homelessness_summary(intermediate_dir)
    total_row = homelessness_summary["category"] == "Total homelessness housing need estimate"
    homelessness_need = homelessness_summary.loc[total_row, "housing_need"].iloc[0]

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

    try:
        ofm_year = context["ofm_year"]
    except KeyError:
        raise ValueError("OFM year not found in context. Ensure 'clean_ofm_estimates' step has been run.")

    summary = calculate_summary(
        housing_need, ofm_housing, ofm_year, context["forecast_year"],
        context["county_map"], homelessness_need,
    )

    output_path = Path(context["output_dir"]) / "housing_need.xlsx"
    with pd.ExcelWriter(output_path) as writer:
        summary.to_excel(writer, sheet_name="summary", index=False)
        housing_need.rename(columns=ESTIMATED_COLUMN_LABELS).to_excel(writer, sheet_name="data", index=False)
        homelessness_summary.to_excel(writer, sheet_name="homelessness", index=False)

    print("Housing need calculation complete. Summary saved to", output_path)
    return context
