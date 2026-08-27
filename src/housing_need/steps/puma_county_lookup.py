import os

import pandas as pd
import geopandas as gpd


#------------------------------
# Create PUMA to County Lookup
#------------------------------
# This uses the PUMA centroids to spatially join to counties
# to create a lookup table of PUMA to County relationships.
# This happens to work well for PSRC because no PUMAs cross county
# lines. If that were to change, a different method would be needed.

def create_puma_county_lookup(context):
    # create county geoid list
    counties = context['county_ids']
    county_geoids_str = [str(c) for c in counties]

    intermediate_dir = context['output_dir'] + "/intermediate"
    os.makedirs(intermediate_dir, exist_ok=True)
    

    # download county shapefile from tigerweb
    cnty = (
        gpd.read_file('https://www2.census.gov/geo/tiger/TIGER2025/COUNTY/tl_2025_us_county.zip')
        .query('GEOID.isin(@county_geoids_str)')
        .assign(GEOID =lambda df: df['GEOID'].astype(int))
        .rename(columns={'GEOID':'county_id'})
        [['county_id', 'geometry']]
    )

    # download puma shapefile from tigerweb
    puma = (
        gpd.read_file('https://www2.census.gov/geo/tiger/TIGER2025/PUMA20/tl_2025_53_puma20.zip')
        .assign(puma_id = lambda df: df['GEOID20'].astype(int))
        .rename(columns={'PUMACE20':'PUMA'})
        [['PUMA','puma_id', 'geometry']]
    )

    # get centroids of pumas
    puma.geometry = puma.representative_point()

    # spatial join pumas to counties
    puma_cnty = gpd.sjoin(puma, cnty, how='inner', predicate='within').drop(columns='index_right')

    # create region column
    puma_cnty['region'] = 1

    # save to csv in data directory
    puma_cnty[['PUMA','puma_id','county_id','region']].to_csv(intermediate_dir + '/puma_geog_lookup_cnty.csv', index=False)


def run_step(context):
    # pypyr step to run load_data.py
    print("Creating PUMA <-> County Lookup table...")
    create_puma_county_lookup(context)
    return context