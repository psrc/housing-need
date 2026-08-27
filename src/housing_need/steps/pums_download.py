import us
import os
from zipfile import ZipFile
import io
from urllib.request import urlopen


def get_data(census_year, pums_table, state_id_str, state_abbr, context, overwrite=True):
    """
    Downloads PUMS data from the Census FTP and saves it as a CSV file in the data directory.
    If the file already exists, it will not download unless 'overwrite' is set to True.

    Args:
        census_year (int): Year of the PUMS data to download.
        pums_table (str): 'h' for household table, 'p' for person table.
        state_id_str (str): State FIPS code as a string.
        state_abbr (str): State abbreviation in lowercase.
        overwrite (bool): If True, delete existing file and download new one.
    """
    intermediate_dir = context['output_dir'] + "/intermediate"
    os.makedirs(intermediate_dir, exist_ok=True)
    file_name = f"psam_{pums_table}{state_id_str}.csv"
    file_path = os.path.join(intermediate_dir, file_name)

    if os.path.exists(file_path):
        if overwrite:
            os.remove(file_path)
            print(f"Deleted existing file: {file_path}")
        else:
            print(f"File already exists, skipping download: {file_path}")
            return

    pums_type = context['pums_type']
    pums_url = f"https://www2.census.gov/programs-surveys/acs/data/pums/{census_year}/{pums_type}/csv_{pums_table}{state_abbr}.zip"
    print(f"Downloading PUMS data from: {pums_url}")
    r = urlopen(pums_url).read()
    archive = ZipFile(io.BytesIO(r))
    archive.extract(file_name, intermediate_dir)
    print(f"Downloaded and extracted: {file_name} to {intermediate_dir}")

def run_step(context):
    print("Downloading PUMS data...")
    base_year = context['pums_year']
    state_id_str = str(context['state_id'])
    state_abbr = us.states.mapping('fips', 'abbr')[state_id_str].lower()
    get_data(base_year,'h',state_id_str,state_abbr,context,overwrite=True)
    get_data(base_year,'p',state_id_str,state_abbr,context,overwrite=True)
    return context