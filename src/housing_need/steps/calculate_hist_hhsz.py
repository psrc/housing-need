import os
import pandas as pd

from housing_need.util import CensusApi

COUNTIES = {
  "King": 53033,
  "Kitsap": 53035,
  "Pierce": 53053,
  "Snohomish": 53061
}

def get_county_data(census_api, year, dataset, cols_dict, county_ids, state_id):
    df = (census_api.get_dec_data(cols_dict, year, 'county', dataset, county_ids, state_id)
            .query('geoid in @county_ids') 
            .assign(
                hhpop = lambda x: x.total_pop - x.gq
            )
            [['households','hhpop']].sum(numeric_only=True).to_frame().T
            .assign(
                hhsz = lambda x: x.hhpop / x.households,
                year = year
            )
    )
    return df

def run_step(context):
    county_ids = context["county_ids"]
    state_id = context["state_id"]
    census_api = CensusApi(os.getenv(context['census_key']), timeout=90)

    cols_dict20 = {
    'total_pop': ['P1_001N'],
    'gq': ['P18_001N'],
    'households': ['H3_002N'],
    }
    df20 = get_county_data(census_api, 2020, 'dhc', cols_dict20, county_ids, state_id)

    cols_dict10 = {
    'total_pop': ['P001001'],   # P1: Total population
    'gq': ['P042001'],          # P42: Group quarters population
    'households': ['H003002'],  # H3: Occupied housing units
    }
    df10 = get_county_data(census_api, 2010, 'sf1', cols_dict10, county_ids, state_id)

    cols_dict00 = {
    'total_pop': ['P001001'],   # P1: Total population
    'gq': ['P037001'],          # P42: Group quarters population
    'households': ['H003002'],  # H3: Occupied housing units
    }
    df00 = get_county_data(census_api, 2000, 'sf1', cols_dict00, county_ids, state_id)

    df90 = pd.read_csv(os.path.join(context['data_dir'], 'nhgis0024_ds120_1990_county.csv'), usecols=['COUNTY','ET1001','EUO001','ET7011','ET7012'])
    df90 = df90.rename(columns={
        'COUNTY': 'county',
        'ET1001': 'total_pop',
        'EUO001': 'households'
    })

    df90['gq'] = df90['ET7011'] + df90['ET7012']
    df90['hhpop'] = df90['total_pop'] - df90['gq']
    df90['county_id'] = df90['county'].map(COUNTIES)
    df90 = df90.loc[df90['county_id'].isin(county_ids)][['households', 'hhpop']].sum(numeric_only=True).to_frame().T
    df90['hhsz'] = df90['hhpop'] / df90['households']
    df90['year'] = 1990

    df_out = pd.concat([df90,df00,df10,df20], ignore_index=True)
    df_out.to_csv(os.path.join(context['output_dir'], 'historical_hhsz.csv'), index=False)
    return context