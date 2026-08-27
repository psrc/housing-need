import pandas as pd

def load_data():
    xwalk = pd.read_csv("output/intermediate/puma_geog_lookup_cnty.csv")
    h = (
        pd.read_csv('output/intermediate/psam_h53.csv')
        .query('PUMA.isin(@xwalk["PUMA"]) & TYPEHUGQ == 1')
    )

    p = (
    pd.read_csv('output/intermediate/psam_p53.csv')
    .query('SERIALNO.isin(@h["SERIALNO"])')
    )
    return h, p

def calculate_non_k12_doubled_up(h, p):
    cost_burdened = (h['GRPIP'] >= 50)
    over_crowding = (h['NP'] / h['BDSP'] > 1.5) | (h['NP'] / h['RMSP'] > 1.5)
    no_k_12_children = (~h['HUPAOC'].isin([2,3])) & (~h['HUPAOC'].isin([2,3]))
    h_filter = cost_burdened & over_crowding & no_k_12_children
    poverty_mask = (p['POVPIP'] < 200)
    relatives_mask = (~p['RELSHIPP'].isin([20,21,22,23,24])) & (p['AGEP'] > 25)
    p_filter = p.loc[poverty_mask & relatives_mask]['SERIALNO']
    return h.loc[h_filter & p['SERIALNO'].isin(p_filter)]['WGTP'].sum()

def run_step(context):
    # Load the household and person data
    households, persons = load_data()
    # Calculate the number of non-K12 doubled-up households
    non_k12_doubled_up = calculate_non_k12_doubled_up(households, persons)
    # Store the result in the context dictionary
    context['non_k12_doubled_up'] = non_k12_doubled_up
    return context