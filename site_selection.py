# this has been tested and ran in Python 2.7
# see documentation on overview of algorithm
# email matthew@mdnorris.com with any questions
# last updated 12/31/19

# need to document each section along with
# an outside document that matches with it

import pandas as pd
import numpy as np
import timeit

# start_time = timeit.default_timer()
# SECTION 1: DATA INPUTS

# SITES TEST DAILY DATA (this is fictitious site and bin data)
sites = pd.read_csv('C:/Users/usrMain/Desktop/site selection/sites.csv',
                    delimiter=',')
# for testing purposes

# temp_sites_1 = sites.groupby('fict_site')['Sum_GBs'].mean().reset_index()
# temp_sites_1 = temp_sites_1.drop(['Sum_GBs'], axis=1)
# temp_sites_2 = temp_sites_1.sample(frac=.50, random_state=1)
# sites = pd.merge(sites, temp_sites_2, on='fict_site')

init_sites = sites.drop(['Type', 'Morphology'], axis=1)

# SITES TEST HOURLY DATA (this is fictitious site and bin data)

hr_sites = pd.read_csv(
    'C:/Users/usrMain/Desktop/site selection/hourly_sites.csv', delimiter=',')

init_hr_sites = hr_sites

# NPV DATA

# All relevant NPV values from original Alteryx workflow
# future financial estimates may need to be implemented

npv_values = pd.read_csv('C:/Users/usrMain/Desktop/site selection/npv.csv',
                         delimiter=',')

# column headers for morphology calculations
# to be used in morph function

npv_values.columns = ['non', 'off_du', 'off_u', 'off_s', 'on_du', 'on_u',
                      'on_s', 'roe_du', 'roe_u', 'roe_s']

# This creates time periods for xnpv function (for more information,
# see documentation) changes in time periods can drastically alter
# npv values

st_date = pd.date_range(start=pd.Timestamp('2019-01-01'), periods=11, freq='AS')

# LTE INPUTS

# LTE constants - these will not likely change in future versions
# but some are not used yet

# sites['temp_k'] = 294.61111111111
# sites['kt'] = -173.90667746295
# sites['ktb'] = -101.353952411912
sites['rx_sensitivity_db'] = -93.3539524119117

# LTE Assumptions File (this will also not likely change in the future)

lte_params = pd.read_csv(
    'C:/Users/usrMain/Desktop/site selection/lte_assumptions.csv',
    delimiter=',')

# RF ASSUMPTIONS all constants, some are not used yet

# sites['ambient_temp_f'] = 70.0
# sites['mw_db_coeff'] = 30.0
# sites['ue_nf_db'] = 8.0
# sites['bw_mhz'] = 20.0
# sites['enb_eirp_dbm'] = 37.0

# XPNV Values
# these are the NPV constants, may change

disc_rt = .15
other = 60.0

# creates empty arrays for npv values
# used in the finarrays function

cpx = np.empty([11, 1])
opx = np.empty([11, 1])
growth = np.empty([11, 1])
mvno = np.empty([11, 1])
value = np.empty([11, 1])


# SECTION 2: FUNCTIONS

# this function takes the type and morphology and converts
# it into a code to make the xnpv function work faster


def morph(type, morph):
    if type == 'Off-Strand' and morph == 'Dense Urban':
        morph_code = 1
    elif type == 'Off-Strand' and morph == 'Urban':
        morph_code = 2
    elif type == 'Off-Strand' and morph == 'Suburban':
        morph_code = 3
    elif type == 'On-Strand' and morph == 'DenseUrban':
        morph_code = 4
    elif type == 'On-Strand' and morph == 'Urban':
        morph_code = 5
    elif type == 'On-Strand' and morph == 'Suburban':
        morph_code = 6
    elif type == 'ROE Building' and morph == 'Dense Urban':
        morph_code = 7
    elif type == 'ROE Building' and morph == 'Urban':
        morph_code = 8
    else:
        morph_code = 9
    return morph_code


# this function is used inside the xnpv function
# to change the values depending on morphology


def fin_arrays(code):
    if code == 1:
        npv = npv_values.loc[:, 'off_du']
    elif code == 2:
        npv = npv_values.loc[:, 'off_u']
    elif code == 3:
        npv = npv_values.loc[:, 'off_s']
    elif code == 4:
        npv = npv_values.loc[:, 'on_du']
    elif code == 5:
        npv = npv_values.loc[:, 'on_u']
    elif code == 6:
        npv = npv_values.loc[:, 'on_s']
    elif code == 7:
        npv = npv_values.loc[:, 'roe_du']
    elif code == 8:
        npv = npv_values.loc[:, 'roe_u']
    else:
        npv = npv_values.loc[:, 'roe_s']
    penet_rate = float(npv[62])
    for i in range(11):
        cpx[i] = float(npv[i + 3])
    for i in range(11):
        opx[i] = float(npv[i + 14])
    for i in range(11):
        growth[i] = float(npv[i + 40])
    for i in range(11):
        mvno[i] = float(npv[i + 51])
    return penet_rate, cpx, opx, growth, mvno


# XNPV Function - is called repeatedly to estimate
# the NPV oF a site

# changing the number of days in xnpv can affect the output
# so this variable is to test for those sorts of discrepancies

day_diff = 0.0

# the cell split is calculated by the elif when the site
# capacity has been met, the cell_split variable sets
# value for the new cap, not to exceed 2.0

cell_split = 2.0


def xnpv(gbs, mo_cap, code):
    penet_rate, cpx, opx, growth, mvno = fin_arrays(code)
    count = 0
    for i in range(11):
        if (gbs * penet_rate * (growth[i]) * 12) < (mo_cap * 12):
            value[i] = gbs * penet_rate * 12 * mvno[i] * growth[i] - \
                       opx[i] - other
        elif gbs * penet_rate * (growth[i]) * 12 < (mo_cap * 12 * cell_split):
            value[i] = mo_cap * 12 * (mvno[i]) - (cpx[i]) - \
                       (opx[i]) - other
        else:
            value[i] = gbs * penet_rate * 12 * mvno[i] * growth[i] - \
                       (2 * opx[i]) - other
            count += 1
    date_0 = st_date[0]
    value[0] = value[0] - cpx[0]
    if count != 0:
        j = 11 - count
        value[j] = value[j] - cpx[j]
    return sum([value_i / ((1.0 + disc_rt) **
                           (((date_i - date_0).days - day_diff) / 365.0))
                for value_i, date_i in zip(value, st_date)])


# SECTION 3: FIRST ITERATION TO GENERATE INHERENT NPV

# LTE and SINR calculations

# this section makes sinr calculation for matching in with lte
# parameters, and also creates a few important fields
sites['rx_signal_strength_db'] = 37.0 - sites['path_loss_umi_db']
sites['sinr'] = sites['rx_signal_strength_db'] - sites['rx_sensitivity_db']
sites['sinr'] = sites['sinr'].round(0)
sites['rx_signal_strength_mw'] = ((10 ** ((37.0 -
                                           sites['path_loss_umi_db'])
                                          / 10) / 1000.000000000))

bin_sinr = sites[['GridName', 'sinr', 'rx_signal_strength_mw',
                  'rx_signal_strength_db', 'rx_sensitivity_db']]

# this sections, which runs every iteration, drops anything with SINR
# under -7, one of the two criteria for dropping observations

sites = sites[sites.sinr >= -7.0]

# sums up the site offload capability by site, daily

tot_sum_gbs = sites.groupby('fict_site')['Sum_GBs'].sum().reset_index()
tot_sum_gbs = tot_sum_gbs.rename(columns={'Sum_GBs': 'gb_offload'})
sites = pd.merge(sites, tot_sum_gbs, on='fict_site')

# brings daily and hourly data together, does calculations
# to get the busy hour

sites = pd.merge(sites, hr_sites, on='GridName').reset_index()
sites['bin_req_hr_mbps'] = (sites['Hour_GBs'] * 8 * (2 ** 10)) / 3600
site_req = sites.groupby(['fict_site', 'event_hour'])['bin_req_hr_mbps']. \
    sum().reset_index()
sum_req = site_req.sort_values(by=['fict_site', 'bin_req_hr_mbps'],
                               ascending=[True, False])
sum_req = sum_req.groupby('fict_site').first().reset_index()
sites = pd.merge(sites, sum_req, how='inner', left_on=['fict_site',
                                                       'event_hour'],
                 right_on=['fict_site', 'event_hour']).reset_index()

# merges in lte parameters to find throughput, the sinr of a grid
# matches in variables that change rb_thru_put which affects npv

sites = pd.merge(sites, lte_params, left_on='sinr', right_on='SINR')
sites['rb_thru_put'] = (((sites['Code Rate'] * sites['symbols/SF'] *
                          1000 * 12 * 400 *
                          sites['2x2 MIMO Gain'] * sites['subframe allocation'])
                         / 1000000) * ((1 - sites['retrans']) *
                                       (1 - sites['high  layer overhead'])) -
                        (sites['overhead TP kbps'] / 1000)) / 400

# final calculations to determine max_cap and gb_offload,
# and also derives site type and morphology, to finish
# the inputs for the xnpv function

sites['bh_req_rbs'] = ((sites['Hour_GBs'] * 8 * (2 ** 10)) / 3600) / \
                      sites['rb_thru_put']
agg_sites = sites.groupby('fict_site')['bh_req_rbs'].sum().reset_index()
agg_sites['enb_util'] = np.ceil(agg_sites['bh_req_rbs']) / 400
temp_agg_sites = sites.groupby('fict_site')['gb_offload'].mean().reset_index()
agg_sites = pd.merge(agg_sites, temp_agg_sites, on='fict_site')
agg_sites['max_cap'] = (agg_sites['gb_offload'] / agg_sites['enb_util'])
site_type = sites.groupby('fict_site')['Type'].first().reset_index()
site_morph = sites.groupby('fict_site')['Morphology'].first().reset_index()
agg_sites = pd.merge(agg_sites, site_type, on='fict_site')
agg_sites = pd.merge(agg_sites, site_morph, on='fict_site')

# FIRST ITERATION OF ALGORITHM, runs functions, then
# orders and ranks the sites

agg_sites['morph_code'] = agg_sites.apply(lambda x:
                                          morph(x['Type'],
                                                x['Morphology']), axis=1)

agg_sites['npv'] = agg_sites.apply(lambda x:
                                   xnpv(x['gb_offload'], x['max_cap'],
                                        x['morph_code']), axis=1)
agg_sites['npv'] = agg_sites.npv.astype(int)

ranking = agg_sites.loc[agg_sites['npv'] >= 0]
ranking['rank'] = ranking['npv'].rank(ascending=False)
ranking = ranking.sort_values(by='rank')

init_ranking = ranking

# creates array to be filled with the best
# site candidate

selected = (pd.DataFrame(init_ranking.iloc[0, :])).T

# all remaining positive NPV will be compared
# against any remaining NPV positive sites
# which will be in this candidates list

candidates = pd.DataFrame(init_ranking.iloc[1:, :])

# PART 4: END OF FIRST ITERATION, LOOPED UNTIL COMPLETE

# TEST: to evaluate time of loop
# init_time = timeit.default_timer() - start_time
# init_time = np.empty((len(candidates), 1))

for j in range((len(candidates))):
    start = timeit.default_timer()
    selected_bins = pd.merge(selected, init_sites, on='fict_site')
    for i in range((len(candidates))):
        # next_best is taken from the list of candidates
        # and selects one site to compare against the selected
        # dataframe, then daily sites are merged in so the bins
        # belonging to that candidate can be tested
        # gb_offload is calculated before adding hourly
        # in as it is above

        next_best = (pd.DataFrame(candidates.iloc[i, :])).T
        candidates_bins = pd.merge(next_best, init_sites, on='fict_site')
        ranked_bins = selected_bins.append(candidates_bins)
        ranked_bins = ranked_bins.drop(['gb_offload'], axis=1)
        tot_sum_gbs = ranked_bins.groupby('fict_site')['Sum_GBs']. \
            sum().reset_index()
        tot_sum_gbs = tot_sum_gbs.rename(columns={'Sum_GBs': 'gb_offload'})
        ranked_bins = pd.merge(ranked_bins, tot_sum_gbs, on='fict_site')

        # hourly sites are merged so that hourly bin data is available

        all_bins = pd.merge(ranked_bins, init_hr_sites, on='GridName')
        all_bins = pd.merge(all_bins, bin_sinr, on='GridName')
        sinr_bins = all_bins
        sinr_bins = sinr_bins.sort_values(by=['GridName', 'sinr'],
                                          ascending=[True, False])
        sinr_bins_unique = sinr_bins.drop_duplicates(subset='GridName')
        sinr_bins_dups = sinr_bins.loc[sinr_bins['GridName'].duplicated(), :]
        sum_rx_signal = \
            sinr_bins_dups.groupby('GridName')['rx_signal_strength_mw'].sum()
        sinr_bins = sinr_bins_unique.append(sinr_bins_dups)

        # this calculates an adjusted sinr from the comparison
        # of the selected list to the each candidate, once
        # per inner loop, and drops grids with low sinr

        if len(sum_rx_signal) > 0:
            sinr_bins['sinr_new'] = sinr_bins['sinr']
        else:
            sinr_bins['sinr_new'] = sinr_bins['rx_signal_strength_db'] - \
                                    (np.log10((sum_rx_signal +
                                               (10 **
                                                (sinr_bins['rx_sensitivity_db']
                                                 / 10))) / 1000) * 1000) * 10
        sinr_bins = sinr_bins[sinr_bins.sinr_new >= -7.0]

        # for calculation and efficiency purposes, this selects
        # the candidate from the next_best df and drops all others
        # then runs the lte calculations

        nb = next_best['fict_site']
        sinr_bins = sinr_bins.loc[sinr_bins['fict_site'].isin(nb)]


        sinr_bins = pd.merge(sinr_bins, lte_params, left_on='sinr_new',
                             right_on='SINR')
        sinr_bins['rb_thru_put'] = \
            (((sinr_bins['Code Rate'] * sinr_bins['symbols/SF'] *
               1000 * 12 * 400 * sinr_bins['2x2 MIMO Gain'] *
               sinr_bins['subframe allocation']) / 1000000) *
             ((1 - sinr_bins['retrans']) *
              (1 - sinr_bins['high  layer overhead'])) -
             (sinr_bins['overhead TP kbps'] / 1000)) / 400

        # derives site type and morphology, and finishes
        # the inputs for the xnpv function
        sinr_bins['bh_req_rbs'] = ((sinr_bins['Hour_GBs'] *
                                    8 * (2 ** 10)) / 3600) / \
                                  sinr_bins['rb_thru_put']

        agg_sinr = sinr_bins.groupby('fict_site')[
            'bh_req_rbs'].sum().reset_index()

        # this final section does the same as above, creating
        # the inputs for the xnpv function

        agg_sinr['enb_util'] = np.ceil(agg_sinr['bh_req_rbs']) / 400

        temp_agg_sites = sinr_bins.groupby('fict_site')[
            'gb_offload'].mean()
        agg_sinr = pd.merge(agg_sinr, temp_agg_sites, on='fict_site')
        agg_sinr['max_cap'] = (
                agg_sinr['gb_offload'] / agg_sinr['enb_util'])
        site_type = sinr_bins.groupby('fict_site')['Type'].first()
        site_morph = sinr_bins.groupby('fict_site')[
            'Morphology'].first().reset_index()
        agg_sinr = pd.merge(agg_sinr, site_type, on='fict_site')
        agg_sinr = pd.merge(agg_sinr, site_morph, on='fict_site')

        agg_sinr['morph_code'] = \
            agg_sinr.apply(lambda x: morph(x['Type'],
                                           x['Morphology']), axis=1)

        # since each candidate has one npv value, the inputs
        # for the sinr function were converted to floats from
        # series

        gb_offload = agg_sinr['gb_offload'].loc[0]
        max_cap = agg_sinr['max_cap'].loc[0]
        morph_code = agg_sinr['morph_code'].loc[0]
        adj_npv = xnpv(gb_offload, max_cap, morph_code)
        candidates['npv'][i] = adj_npv
    new_ranking = candidates.loc[candidates['npv'] > 0]
    new_ranking['new_rank'] = new_ranking['npv'].rank(ascending=False)
    new_ranking = new_ranking.sort_values(by='new_rank')
    temp_selected = (pd.DataFrame(new_ranking.iloc[0, :])).T
    selected = selected.append(temp_selected)
    candidates = pd.DataFrame(new_ranking.iloc[1:, :])
    # init_time[j] = timeit.default_timer() - start
    # print(len(candidates))
    if len(candidates) == 0:
        break

init_ranking.to_csv('first_ranking.csv')
selected.to_csv('final_ranking.csv')
# np.savetxt('time.csv', init_time, delimiter=',')
# end_time = timeit.default_timer() - start_time
