import os
import re

import pandas as pd
from rapidfuzz import fuzz, process

# strip generic suffixes/district numbers so matching is driven by the distinctive part of the name
# (otherwise "School District"/"Public Schools" being shared tokens inflates scores for unrelated districts)
# lookahead (not \b) after the optional "." since punctuation followed by whitespace has no word boundary
GENERIC_SUFFIXES = re.compile(
    r'\b(School District|Public Schools|Community Schools|Schools|Historical|Hist\.?|Elementary)(?=\s|$)',
    re.IGNORECASE,
)
DISTRICT_NUMBER = re.compile(r'(No\.?\s*)?#?\s*\d+\s*$', re.IGNORECASE)

MATCH_SCORE_CUTOFF = 95


def normalize(name):
    name = DISTRICT_NUMBER.sub('', name)
    name = GENERIC_SUFFIXES.sub('', name)
    return re.sub(r'\s+', ' ', name).strip(' .')


def load_mvs_data(context):
    """Load school-district enrollment characteristics (incl. doubled-up counts) and district names."""
    data_dir = context['data_dir']
    dist = pd.read_csv(os.path.join(data_dir, context['data']['school_districts']))
    mvs = pd.read_csv(os.path.join(data_dir, context['data']['mvs_data']))
    return dist, mvs


def match_lea_to_district(lea_names, dist_names):
    """Fuzzy-match each LEA name to its closest normalized school district name."""
    normalized_dist = {normalize(d): d for d in dist_names}

    lea_to_dist = {}
    for lea in lea_names:
        match = process.extractOne(
            normalize(lea), normalized_dist.keys(), scorer=fuzz.ratio, score_cutoff=MATCH_SCORE_CUTOFF
        )
        lea_to_dist[lea] = normalized_dist[match[0]] if match else None
    return lea_to_dist


def apply_district_match(mvs, lea_to_dist):
    """Attach matched district names to the MVS rows, dropping LEAs with no match."""
    mvs = mvs[mvs['LEA'].map(lea_to_dist).notna()].copy()
    mvs['School District'] = mvs['LEA'].map(lea_to_dist)
    return mvs


def save_doubled_up_students(mvs_matched, intermediate_dir):
    """Write per-LEA doubled-up student counts to file and return the region-wide total."""
    doubled_up = mvs_matched.loc[mvs_matched['Characteristics'] == 'Doubled-up', ['LEA', 'Value']]
    doubled_up = doubled_up.sort_values(by='LEA').rename(columns={'Value': 'Doubled-up students'})
    doubled_up.to_csv(os.path.join(intermediate_dir, 'doubled_up_students.csv'))

    return doubled_up['Doubled-up students'].str.replace(',', '').apply(pd.to_numeric).sum()


def load_household_person_data(intermediate_dir):
    """Load PUMS households and persons within the region."""
    xwalk = pd.read_csv(os.path.join(intermediate_dir, 'puma_geog_lookup_cnty.csv'))
    h = (
        pd.read_csv(os.path.join(intermediate_dir, 'psam_h53.csv'))
        .query('PUMA.isin(@xwalk["PUMA"]) & TYPEHUGQ == 1')
    )
    p = (
        pd.read_csv(os.path.join(intermediate_dir, 'psam_p53.csv'))
        .query('SERIALNO.isin(@h["SERIALNO"])')
    )
    return h, p


def calculate_avg_children_per_hh(h, p):
    """Weighted average number of school-age (5-17) kids, among households that have at least one."""
    age_mask = (p['AGEP'] >= 5) & (p['AGEP'] < 18)
    children = p.loc[age_mask].groupby('SERIALNO').size()
    hh_children = h.merge(children.rename('num_children'), on='SERIALNO', how='inner')
    return (hh_children['num_children'] * hh_children['WGTP']).sum() / hh_children['WGTP'].sum()


def run_step(context):
    intermediate_dir = os.path.join(context['output_dir'], 'intermediate')

    dist, mvs = load_mvs_data(context)
    lea_to_dist = match_lea_to_district(mvs['LEA'].dropna().unique(), dist['School District'].dropna().unique())
    mvs_matched = apply_district_match(mvs, lea_to_dist)
    total_doubled_up_students = save_doubled_up_students(mvs_matched, intermediate_dir)

    h, p = load_household_person_data(intermediate_dir)
    avg_children_per_hh = calculate_avg_children_per_hh(h, p)

    context['doubled_up_households'] = total_doubled_up_students / avg_children_per_hh
    return context