import pandas as pd
import requests


class CensusApi:
    def __init__(self, api_key, timeout=15):
        self.api_key = api_key
        self.timeout = timeout

    def get_table(self, variables, year, for_predicates, in_predicates, dataset_url):
        """
        Takes in a list of variables and returns a dataframe
        """
        HOST = "https://api.census.gov/data"
        base_url = "/".join([HOST, str(year), dataset_url])
        chunks = [variables[x:x+45] for x in range(0, len(variables), 45)]
        df = pd.DataFrame()
        for chunk in chunks:
            predicates = {}
            predicates["get"] = ",".join(chunk)
            predicates["for"] = for_predicates
            if in_predicates is not None:
                predicates["in"] = in_predicates
            predicates["key"] = self.api_key
            r = requests.get(base_url, params=predicates, timeout=self.timeout)
            chunk_df = pd.DataFrame(r.json()[1:], columns=r.json()[0])
            if df.empty:
                df = chunk_df
            else:
                df.drop(columns=['state', 'county', 'tract'], inplace=True, errors='ignore')
                df = df.merge(chunk_df, left_index=True, right_index=True)
        return df

    @staticmethod
    def combine_groups(variables_dict, df):
        """
        Takes in a dictionary of variables and a dataframe and sums any variables that 
        are made up of multiple census columns.
        """
        for key, value in variables_dict.items():
            df[key] = df[value].astype(float).sum(axis=1)
            df = df.drop(value, axis=1)
        return df

    @staticmethod
    def create_in_predicates(geog, county_ids, state_id):
        """
        Takes in a geography and returns in_predicates
        """
        county_ids_str = [str(county_id)[2:] for county_id in county_ids]
        if geog in ['tract', 'block group', 'block']:
            counties_str = ','.join(county_ids_str)
            in_predicates = f'state:{str(state_id)}', f'county:{counties_str}'
        elif geog in ['county', 'place', 'congressional district']:
            in_predicates = f'state:{str(state_id)}'
        elif geog == 'state':
            in_predicates = None
        else:
            raise ValueError("geog must be: 'state', 'county', 'congressional district', 'place', 'tract', 'block group' or 'block'")
        return in_predicates

    def get_dec_data(self, variables_dict, year, geog, dataset, county_ids, state_id):
        """
        Takes in a dictionary of variables and returns decennial data in a dataframe.
        """
        in_predicates = self.create_in_predicates(geog, county_ids, state_id)
        for_predicates = f'{geog}:*'
        dataset_url = f'dec/{dataset}'
        start_vars = ['GEO_ID', 'NAME']
        variables = [i for j in variables_dict.values() for i in j]
        variables = start_vars + variables
        df = self.get_table(variables, year, for_predicates, in_predicates, dataset_url)
        df = self.combine_groups(variables_dict, df)
        df = self.create_geoid(geog, df)
        df.rename(columns={'NAME': 'name'}, inplace=True)
        df = df[['geoid', 'name'] + list(variables_dict.keys())]
        return df

    def create_geoid(self, geog, df):
        geog_slices = {
            'block': -15,
            'tract': -11,
            'block group': -12,
            'county': -5,
            'place': -7,
            'state': -2
        }
        df['geoid'] = df['GEO_ID'].str.slice(start=geog_slices[geog]).astype('int64')
        return df


# ---------------------------------------------------------------------------
# Decennial census variable specifications
# ---------------------------------------------------------------------------

# 2000 SF4 PCT005: SEX BY AGE FOR THE POPULATION IN HOUSEHOLDS.
POP_DICT_SF4_2000 = {
    'age_15_24': [
        'PCT005006', 'PCT005007', 'PCT005008', 'PCT005009', 'PCT005010',
        'PCT005030', 'PCT005031', 'PCT005032', 'PCT005033', 'PCT005034',
    ],
    'age_25_34': ['PCT005011', 'PCT005012', 'PCT005035', 'PCT005036'],
    'age_35_44': ['PCT005013', 'PCT005014', 'PCT005037', 'PCT005038'],
    'age_45_54': ['PCT005015', 'PCT005016', 'PCT005039', 'PCT005040'],
    'age_55_64': [
        'PCT005017', 'PCT005018', 'PCT005019',
        'PCT005041', 'PCT005042', 'PCT005043',
    ],
    'age_65_74': [
        'PCT005020', 'PCT005021', 'PCT005022',
        'PCT005044', 'PCT005045', 'PCT005046',
    ],
    'age_75_84': ['PCT005023', 'PCT005024', 'PCT005047', 'PCT005048'],
    'age_85_plus': ['PCT005025', 'PCT005049'],
}

# 2010 SF1 PCT013: SEX BY AGE FOR THE POPULATION IN HOUSEHOLDS.
POP_DICT_SF1_2010 = {
    'age_15_24': [
        'PCT013006', 'PCT013007', 'PCT013008', 'PCT013009', 'PCT013010',
        'PCT013030', 'PCT013031', 'PCT013032', 'PCT013033', 'PCT013034',
    ],
    'age_25_34': ['PCT013011', 'PCT013012', 'PCT013035', 'PCT013036'],
    'age_35_44': ['PCT013013', 'PCT013014', 'PCT013037', 'PCT013038'],
    'age_45_54': ['PCT013015', 'PCT013016', 'PCT013039', 'PCT013040'],
    'age_55_64': [
        'PCT013017', 'PCT013018', 'PCT013019',
        'PCT013041', 'PCT013042', 'PCT013043',
    ],
    'age_65_74': [
        'PCT013020', 'PCT013021', 'PCT013022',
        'PCT013044', 'PCT013045', 'PCT013046',
    ],
    'age_75_84': ['PCT013023', 'PCT013024', 'PCT013047', 'PCT013048'],
    'age_85_plus': ['PCT013025', 'PCT013049'],
}

# 2020 DHC PCT13: SEX BY AGE FOR THE POPULATION IN HOUSEHOLDS.
POP_DICT_DHC_2020 = {
    'age_15_24': [
        'PCT13_006N', 'PCT13_007N', 'PCT13_008N', 'PCT13_009N', 'PCT13_010N',
        'PCT13_030N', 'PCT13_031N', 'PCT13_032N', 'PCT13_033N', 'PCT13_034N',
    ],
    'age_25_34': ['PCT13_011N', 'PCT13_012N', 'PCT13_035N', 'PCT13_036N'],
    'age_35_44': ['PCT13_013N', 'PCT13_014N', 'PCT13_037N', 'PCT13_038N'],
    'age_45_54': ['PCT13_015N', 'PCT13_016N', 'PCT13_039N', 'PCT13_040N'],
    'age_55_64': [
        'PCT13_017N', 'PCT13_018N', 'PCT13_019N',
        'PCT13_041N', 'PCT13_042N', 'PCT13_043N',
    ],
    'age_65_74': [
        'PCT13_020N', 'PCT13_021N', 'PCT13_022N',
        'PCT13_044N', 'PCT13_045N', 'PCT13_046N',
    ],
    'age_75_84': ['PCT13_023N', 'PCT13_024N', 'PCT13_047N', 'PCT13_048N'],
    'age_85_plus': ['PCT13_025N', 'PCT13_049N'],
}

YEAR_CONFIG = {
    2000: {
        'hh': ('sf1', {
            'age_15_24': ['P021003', 'P021012'],
            'age_25_34': ['P021004', 'P021013'],
            'age_35_44': ['P021005', 'P021014'],
            'age_45_54': ['P021006', 'P021015'],
            'age_55_64': ['P021007', 'P021016'],
            'age_65_74': ['P021008', 'P021017'],
            'age_75_84': ['P021009', 'P021018'],
            'age_85_plus': ['P021010', 'P021019'],
        }),
        'pop': ('sf4', POP_DICT_SF4_2000),
    },
    2010: {
        'hh': ('sf1', {
            'age_15_24': ['P022003', 'P022013'],
            'age_25_34': ['P022004', 'P022014'],
            'age_35_44': ['P022005', 'P022015'],
            'age_45_54': ['P022006', 'P022016'],
            'age_55_64': ['P022007', 'P022017', 'P022008', 'P022018'],
            'age_65_74': ['P022009', 'P022019'],
            'age_75_84': ['P022010', 'P022020'],
            'age_85_plus': ['P022011', 'P022021'],
        }),
        'pop': ('sf1', POP_DICT_SF1_2010),
    },
    2020: {
        'hh': ('dhc', {
            'age_15_24': ['PCT3_003N', 'PCT3_013N'],
            'age_25_34': ['PCT3_004N', 'PCT3_014N'],
            'age_35_44': ['PCT3_005N', 'PCT3_015N'],
            'age_45_54': ['PCT3_006N', 'PCT3_016N'],
            'age_55_64': ['PCT3_007N', 'PCT3_017N', 'PCT3_008N', 'PCT3_018N'],
            'age_65_74': ['PCT3_009N', 'PCT3_019N'],
            'age_75_84': ['PCT3_010N', 'PCT3_020N'],
            'age_85_plus': ['PCT3_011N', 'PCT3_021N'],
        }),
        'pop': ('dhc', POP_DICT_DHC_2020),
    },
}


# 2020 DHC P12: SEX BY AGE (total population), used for group-quarters rates.
# Age groups match AGE_GROUP_MAP in steps/clean_ofm_estimates.py.
GQ_TOTAL_POP_DICT_2020 = {
    'age_0_14': ['P12_003N', 'P12_027N', 'P12_004N', 'P12_028N', 'P12_005N', 'P12_029N'],
    'age_15_24': [
        'P12_006N', 'P12_007N', 'P12_030N', 'P12_031N', 'P12_008N',
        'P12_009N', 'P12_010N', 'P12_032N', 'P12_033N', 'P12_034N',
    ],
    'age_25_34': ['P12_011N', 'P12_035N', 'P12_012N', 'P12_036N'],
    'age_35_44': ['P12_013N', 'P12_037N', 'P12_014N', 'P12_038N'],
    'age_45_54': ['P12_015N', 'P12_039N', 'P12_016N', 'P12_040N'],
    'age_55_64': ['P12_017N', 'P12_041N', 'P12_018N', 'P12_019N', 'P12_042N', 'P12_043N'],
    'age_65_74': ['P12_020N', 'P12_021N', 'P12_044N', 'P12_045N', 'P12_022N', 'P12_046N'],
    'age_75_84': ['P12_023N', 'P12_047N', 'P12_024N', 'P12_048N'],
    'age_85_plus': ['P12_025N', 'P12_049N'],
}

# 2020 DHC PCO1: SEX BY AGE FOR THE POPULATION IN GROUP QUARTERS.
GQ_POP_DICT_2020 = {
    'age_0_14': ['PCO1_003N', 'PCO1_022N', 'PCO1_004N', 'PCO1_023N', 'PCO1_005N', 'PCO1_024N'],
    'age_15_24': ['PCO1_006N', 'PCO1_025N', 'PCO1_007N', 'PCO1_026N'],
    'age_25_34': ['PCO1_008N', 'PCO1_027N', 'PCO1_009N', 'PCO1_028N'],
    'age_35_44': ['PCO1_010N', 'PCO1_029N', 'PCO1_011N', 'PCO1_030N'],
    'age_45_54': ['PCO1_012N', 'PCO1_031N', 'PCO1_013N', 'PCO1_032N'],
    'age_55_64': ['PCO1_014N', 'PCO1_033N', 'PCO1_015N', 'PCO1_034N'],
    'age_65_74': ['PCO1_016N', 'PCO1_035N', 'PCO1_017N', 'PCO1_036N'],
    'age_75_84': ['PCO1_018N', 'PCO1_037N', 'PCO1_019N', 'PCO1_038N'],
    'age_85_plus': ['PCO1_020N', 'PCO1_039N'],
}

GQ_YEAR_CONFIG = {
    2020: {
        'total_pop': ('dhc', GQ_TOTAL_POP_DICT_2020),
        'gq_pop': ('dhc', GQ_POP_DICT_2020),
    },
}

# 2020 PL 94-171 H1: OCCUPANCY STATUS, used for vacancy rates.
VACANCY_YEAR_CONFIG = {
    2020: ('pl', {
        'total_units': ['H1_001N'],
        'occupied_units': ['H1_002N'],
    }),
}
