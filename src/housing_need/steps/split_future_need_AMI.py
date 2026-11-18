"""Splits projected net new housing need across income levels (% of AMI).

Follows Commerce's "Establishing Housing Targets for your Community" (2023) method. Net new
need by income level is the sum of three components:

1. Housing to eliminate baseline renter cost burden, from CHAS cost-burdened renter households
   scaled to current OFM households and run through a vacancy-chain model (Exhibit 21).
2. Housing for the baseline homeless population, allocated to counties by share of current
   housing units and split across income levels (Exhibit 22).
3. Additional housing to accommodate population growth, which is the total net new need minus
   the first two components, distributed by the share of households at each income level
   (Exhibits 23 and 24).

Exhibit 25 combines the components. Results are written to an Excel workbook, one tab per exhibit.
"""

import io
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter

# First est column of each structure-type block in CHAS Table 18C (est2, est27, est52, est77).
T18C_BLOCK_STARTS = (2, 27, 52, 77)
INCOME_LEVEL_LABEL = 'Income Level (% of AMI)'


# --- Exhibit 21: housing needed to eliminate renter cost burden ---

def load_chas_cost_burden(path, county_map, levels):
    """Read CHAS renter cost burden by income level, labelled with the model's income levels.

    CHAS reports five income brackets per county; the top one (>100% HAMFI) is assumed to
    fall entirely in the >100-120% level."""
    chas = pd.read_excel(path, sheet_name='Data').rename(columns={
        'Income by Cost Burden': 'income_by_cost_burden',
        'Cost burden > 30%  (Renters only)': 'cost_burden_over_30',
        'Total (Renters and Owners)': 'total_hh',
    })
    chas['county_id'] = chas['County'].map(county_map)
    chas['income_level'] = chas.groupby('county_id').cumcount().map(dict(enumerate(levels)))
    return chas


def scale_cost_burden_to_ofm(chas, vacancy_rates, ofm_housing):
    """Scale CHAS cost-burdened households to current OFM household counts, by county."""
    vacancy = vacancy_rates.set_index('county_id')['vacancy_rate']
    units = ofm_housing.set_index('county_id')['total_housing_units']
    ofm_hh = (units * (1 - vacancy)).round(0)
    adj_ratio = ofm_hh / chas.groupby('county_id')['total_hh'].sum()

    chas = chas.copy()
    chas['adj_ratio'] = chas['county_id'].map(adj_ratio)
    chas['cost_burden_over_30_adj'] = (chas['cost_burden_over_30'] * chas['adj_ratio']).round(0)
    return chas


def load_t18c(path):
    """CHAS Table 18C (renter-occupied units by unit affordability and occupant income), by county."""
    t18c = pd.read_csv(path, dtype={'st': str, 'cnty': str})
    return t18c.set_index((t18c['st'] + t18c['cnty']).astype(int).rename('county_id'))


def unit_afford_matrix(row):
    """Return a 4x5 array: rows are unit affordability levels, columns are occupant income levels."""
    m = np.zeros((4, 5))
    for start in T18C_BLOCK_STARTS:
        for a in range(4):
            for k in range(5):
                m[a, k] += row[f'T18C_est{start + 2 + 6 * a + k}']
    return m


def move_out_probs(m):
    """Share of a moving cost-burdened household's vacated units by unit level (4 levels).

    Cost-burdened households are assumed to live in units priced above their income band."""
    p = np.zeros((5, 4))
    for i in range(5):
        lowest = min(min(i, 3) + 1, 3)
        allowed = np.arange(4) >= lowest
        counts = m[:, i] * allowed
        p[i] = counts / counts.sum()
    return p


def vacancy_chain(cost_burden_hh, m, vacancy_rate, years):
    """Build 1/years of each level's need per year; vacated units are re-occupied until no cost burden remains.

    Returns new production and units vacated that address need, by income level."""
    p = move_out_probs(m)
    occupancy = 1 - vacancy_rate
    need = np.asarray(cost_burden_hh, dtype=float).copy()
    annual = need / occupancy / years
    new_prod, vacated = np.zeros(5), np.zeros(5)

    for _ in range(years):
        build = np.minimum(annual, need / occupancy)
        new_prod += build
        need -= build * occupancy
        movers = build * occupancy
        for _ in range(500):
            if movers.sum() < 1e-9:
                break
            released = movers @ p
            # Units above 80% AMI are split between the 80-100 and 100-120 bands by remaining need.
            top_need = need[3:]
            top_share = top_need / top_need.sum() if top_need.sum() > 0 else np.zeros(2)
            avail = np.concatenate([released[:3], released[3] * top_share])
            housed = np.minimum(avail * occupancy, need)
            need -= housed
            vacated += housed / occupancy
            movers = housed
    return new_prod, vacated


def calculate_cost_burden_need(chas, t18c, vacancy_rates, county_ids, levels, years):
    """Run the vacancy-chain model for each county; one row per county and income level."""
    vacancy = vacancy_rates.set_index('county_id')['vacancy_rate']
    results = []
    for county_id in county_ids:
        county_chas = chas.loc[chas['county_id'] == county_id].set_index('income_level').reindex(levels)
        cost_burden = county_chas['cost_burden_over_30_adj'].to_numpy()
        prod, vacated = vacancy_chain(
            cost_burden, unit_afford_matrix(t18c.loc[county_id]), vacancy[county_id], years
        )
        results.append(pd.DataFrame({
            'county_id': county_id,
            'income_level': levels,
            'cost_burden_hh_chas': county_chas['cost_burden_over_30'].to_numpy(),
            'cost_burden_hh': cost_burden,
            'new_production': prod.round(),
            'units_vacated': vacated.round(),
        }))
    return pd.concat(results, ignore_index=True)


# --- Exhibits 22 and 23: homelessness and population growth ---

def load_housing_need_summary(path, county_map, ofm_year, forecast_year):
    """Regional homelessness need plus each county's current housing units and forecast-year housing need."""
    summary = pd.read_excel(path, sheet_name='summary')
    units_col = f'OFM Current Housing Units {ofm_year}'
    need_col = f'Est. Total Housing Need {forecast_year}'

    homeless_total = summary.loc[summary['County'] == 'Region', 'Est. Current Shortage from Homelessness'].iloc[0]
    counties = summary[summary['County'].isin(county_map)].copy()
    counties['county_id'] = counties['County'].map(county_map)
    counties = counties.set_index('county_id').rename(
        columns={units_col: 'ofm_units', need_col: 'housing_need_forecast'}
    )
    return homeless_total, counties[['ofm_units', 'housing_need_forecast']]


def allocate_homelessness(homeless_total, ofm_units, income_split):
    """Allocate regional homeless housing need to counties by share of current housing units,
    then split it across income levels."""
    hl = pd.DataFrame({'ofm_units': ofm_units})
    hl['hh_homeless'] = homeless_total * hl['ofm_units'] / hl['ofm_units'].sum()
    for level, share in income_split.items():
        hl[level] = (hl['hh_homeless'] * share).round()
    return hl


def calculate_growth_component(counties, cost_burden_need, homeless):
    """Additional housing for population growth: total net new need less the two baseline components.

    The forecast housing need excludes homelessness, so the homeless need is added to the total net new need.
    If baseline needs exceed the total, the total is raised to match and growth is zero."""
    result = pd.DataFrame({
        'cost_burden_prod': cost_burden_need.groupby('county_id')['new_production'].sum(),
        'homeless': homeless,
    })
    result.insert(0, 'total_net_new', counties['housing_need_forecast'] - counties['ofm_units'] + homeless)
    result['growth'] = (
        result['total_net_new'] - result['cost_burden_prod'] - result['homeless']
    ).clip(lower=0)
    result['total_net_new_adj'] = result[['cost_burden_prod', 'homeless', 'growth']].sum(axis=1)
    return result


# --- Exhibit 24: share of households by income level ---

def read_hud_income_limits(path):
    """Read a HUD Income Limits workbook, dropping its core-properties part (malformed dates break openpyxl)."""
    buf = io.BytesIO()
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(buf, 'w') as zout:
        for item in zin.infolist():
            if item.filename != 'docProps/core.xml':
                zout.writestr(item, zin.read(item.filename))
    buf.seek(0)
    return pd.read_excel(buf)


def load_county_median_income(path, state_id, year):
    """HUD 4-person median family income by county_id."""
    hud = read_hud_income_limits(path)
    hud = hud[hud['state'] == state_id].assign(county_id=lambda d: d['fips'] // 100000)
    return hud.set_index('county_id')[f'median{year}']


def load_pums_income_ratios(intermediate_dir, median_income, size_factors):
    """PUMS households with income as a ratio of HAMFI (HUD median adjusted for household size)."""
    puma_cnty = pd.read_csv(intermediate_dir / 'puma_geog_lookup_cnty.csv')[['PUMA', 'county_id']]
    pums = (
        pd.read_csv(intermediate_dir / 'psam_h53.csv', usecols=['PUMA', 'HINCP', 'ADJINC', 'NP', 'WGTP', 'TYPEHUGQ'])
        .query('TYPEHUGQ == 1 and NP > 0 and WGTP > 0')
        .dropna(subset=['HINCP'])
        .merge(puma_cnty, on='PUMA')
    )
    hamfi = pums['NP'].clip(upper=max(size_factors)).map(size_factors) * pums['county_id'].map(median_income)
    # ADJINC carries six implied decimals.
    pums['ratio'] = pums['HINCP'] * pums['ADJINC'] / 1e6 / hamfi
    return pums


def share_up_to_upper_ami(pums_county, upper_ami):
    """Share of households above 100% HAMFI that are at or below `upper_ami` (e.g. 1.2 for 120%)."""
    ratio, weight = pums_county['ratio'].to_numpy(), pums_county['WGTP'].to_numpy()
    return weight[(ratio > 1) & (ratio <= upper_ami)].sum() / weight[ratio > 1].sum()


def calculate_income_shares(chas, pums, levels, upper_ami):
    """Share of households at each income level, by county.

    CHAS lumps all >100% HAMFI households together, so PUMS splits them into the top two levels."""
    hh_by_income = chas.pivot_table(
        index='county_id', columns=chas.groupby('county_id').cumcount(), values='total_hh'
    )
    shares = pd.DataFrame(index=hh_by_income.index, columns=levels, dtype=float)
    for county_id, row in hh_by_income.iterrows():
        total_hh = row.sum()
        upper_share = share_up_to_upper_ami(pums[pums['county_id'] == county_id], upper_ami)
        over_100 = row.iloc[4] / total_hh
        shares.loc[county_id] = [*(row.iloc[:4] / total_hh), over_100 * upper_share, over_100 * (1 - upper_share)]
    return shares


# --- Exhibit 25: total net new housing need by income level ---

def build_total_need(cost_burden_need, homeless, growth, income_shares, levels, split_levels):
    """Combine the three components by county and income level, with a total row per county."""
    cb_by_level = cost_burden_need.pivot(
        index='county_id', columns='income_level', values='new_production'
    ).reindex(columns=levels, fill_value=0.0)
    homeless_by_level = pd.DataFrame(0.0, index=cb_by_level.index, columns=levels)
    homeless_by_level[split_levels] = homeless[split_levels]
    growth_by_level = income_shares.mul(growth['growth'], axis=0)

    rows = []
    for county_id in cb_by_level.index:
        df = pd.DataFrame({
            'cost_burden': cb_by_level.loc[county_id],
            'homeless': homeless_by_level.loc[county_id],
            'growth': growth_by_level.loc[county_id],
        })
        df['total'] = df.sum(axis=1)
        df.loc['Total'] = df.sum()
        df.index.name = 'income_level'
        rows.append(df.assign(county_id=county_id).reset_index())
    total = pd.concat(rows, ignore_index=True)
    return total[['county_id', 'income_level', 'cost_burden', 'homeless', 'growth', 'total']].round()


# --- Export ---

def _add_region_total(df):
    total = df.drop(columns='County').sum()
    return pd.concat([df, pd.DataFrame([{'County': 'Region', **total}])], ignore_index=True)


def build_report_tables(cost_burden_need, homeless, growth, income_shares, total_need, county_map, income_split):
    """One presentation table per exhibit, with county names and readable headings.

    Returns {sheet name: (table, Excel number format)}."""
    county_names = {v: k for k, v in county_map.items()}

    t21 = cost_burden_need.copy()
    t21.insert(0, 'County', t21.pop('county_id').map(county_names))
    t21.columns = [
        'County', INCOME_LEVEL_LABEL, 'Cost-Burdened Renter Households (CHAS)',
        'Cost-Burdened Renter Households (Scaled to OFM Estimates)',
        'New Production to Address Need', 'Units Vacated That Address Need',
    ]
    parts = []
    for county, group in t21.groupby('County', sort=False):
        total = {'County': county, INCOME_LEVEL_LABEL: 'Total', **group.drop(columns=['County', INCOME_LEVEL_LABEL]).sum()}
        parts += [group, pd.DataFrame([total])]
    t21 = pd.concat(parts, ignore_index=True)

    t22 = homeless.reset_index()
    t22.insert(0, 'County', t22.pop('county_id').map(county_names))
    t22 = _add_region_total(t22)
    t22.columns = [
        'County', 'Current Housing Units (OFM)', 'Households Experiencing Homelessness (Allocated)',
        *[f'Housing Needed at {level} of AMI ({share:.0%})' for level, share in income_split.items()],
    ]

    t23 = growth.reset_index()
    t23.insert(0, 'County', t23.pop('county_id').map(county_names))
    t23 = _add_region_total(t23)
    t23.columns = [
        'County', 'Total Projected Net New Units Needed', 'Housing to Eliminate Baseline Renter Cost Burden',
        'Housing for Baseline Homeless Population', 'Additional Housing to Accommodate Population Growth',
        'Total Net New Units Needed (Adjusted)',
    ]

    t24 = income_shares.reset_index()
    t24.insert(0, 'County', t24.pop('county_id').map(county_names))
    t24.columns = ['County'] + [f'{level} of AMI' for level in income_shares.columns]

    t25 = total_need.copy()
    t25.insert(0, 'County', t25.pop('county_id').map(county_names))
    t25.columns = [
        'County', INCOME_LEVEL_LABEL, 'Housing Production Needed to Eliminate Renter Cost Burden',
        'Housing Needed for Population Experiencing Homelessness',
        'Additional Housing to Accommodate Population Growth', 'Total Net New Housing Needed',
    ]

    return {
        'Cost Burden Housing Need': (t21, '#,##0'),
        'Homelessness Housing Need': (t22, '#,##0'),
        'Population Growth Housing Need': (t23, '#,##0'),
        'Household Income Shares': (t24, '0.0%'),
        'Total Need by Income Level': (t25, '#,##0'),
    }


def write_workbook(tables, path):
    """Write each table to its own sheet with bold wrapped headers, number formats and a frozen header row."""
    with pd.ExcelWriter(path, engine='openpyxl') as writer:
        for name, (df, number_format) in tables.items():
            df.to_excel(writer, sheet_name=name, index=False)
            ws = writer.sheets[name]
            ws.row_dimensions[1].height = 48
            for i, col in enumerate(df.columns, start=1):
                letter = get_column_letter(i)
                header = ws[f'{letter}1']
                header.font = Font(bold=True)
                header.alignment = Alignment(wrap_text=True, vertical='center', horizontal='center')
                if pd.api.types.is_numeric_dtype(df[col]):
                    ws.column_dimensions[letter].width = 22
                    for cell in ws[letter][1:]:
                        cell.number_format = number_format
                else:
                    ws.column_dimensions[letter].width = 24
            ws.freeze_panes = 'A2'


def run_step(context):
    settings = context['split_need_ami']
    data_dir = Path(context['data_dir'])
    output_dir = Path(context['output_dir'])
    intermediate_dir = output_dir / 'intermediate'
    county_ids = context['county_ids']
    county_map = context['county_map']

    levels = settings['income_levels']
    income_split = settings['homeless_income_split']
    cost_burden_levels = levels[:-1]  # CHAS covers every level except the top (>120% AMI) one

    vacancy_rates = pd.read_csv(intermediate_dir / 'vacancy_rates.csv')
    vacancy_rates = vacancy_rates.loc[vacancy_rates['year'] == context['vacancy_rates_year']]
    ofm_housing = pd.read_csv(intermediate_dir / 'ofm_housing_estimates.csv')

    # Exhibit 21
    chas = load_chas_cost_burden(data_dir / context['data']['hud_chas'], county_map, cost_burden_levels)
    chas = scale_cost_burden_to_ofm(chas, vacancy_rates, ofm_housing)
    t18c = load_t18c(data_dir / context['data']['hud_chas_t18c'])
    cost_burden_need = calculate_cost_burden_need(
        chas, t18c, vacancy_rates, county_ids, cost_burden_levels, settings['cost_burden_build_years']
    )

    # Exhibits 22 and 23
    homeless_total, counties = load_housing_need_summary(
        output_dir / 'housing_need.xlsx', county_map, context['ofm_year'], context['forecast_year']
    )
    homeless = allocate_homelessness(homeless_total, counties['ofm_units'], income_split)
    growth = calculate_growth_component(counties, cost_burden_need, homeless['hh_homeless'])

    # Exhibit 24
    median_income = load_county_median_income(
        data_dir / context['data']['hud_income_limits'], context['state_id'], settings['hud_income_limits_year']
    )
    pums = load_pums_income_ratios(intermediate_dir, median_income, settings['hamfi_size_factors'])
    income_shares = calculate_income_shares(chas, pums, levels, settings['moderate_income_upper_ami'])

    # Exhibit 25
    total_need = build_total_need(cost_burden_need, homeless, growth, income_shares, levels, list(income_split))

    tables = build_report_tables(
        cost_burden_need, homeless, growth, income_shares, total_need, county_map, income_split
    )
    write_workbook(tables, output_dir / settings['output_file'])

    return context
