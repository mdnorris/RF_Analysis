
# this is the same program as given to
# Robert Resch, with the exception
# of example code to calculate the new
# npv values on the finalized selected
# dataframe. note that the xnpv function
# has an example of cell-splitting by
# if else statements concerning 2 x the
# monthly cap. also pay attention to the end
# of the for loop where npv is ranked
# by the sum of selected and candidate npv
# but the value of the candidate is set to
# the minimum npv. finally, see the
# code after the for loop for the final
# npv calculation. testing has shown
# this last calculation flattens the distribution
# of npv values but does not change the total

import pandas as pd
import numpy as np
import timeit

# SECTION 1: DATA INPUTS

# SITES TEST DAILY DATA (this is fictitious site and bin data) sites

sites = pd.read_csv('C:/Users/norri/Desktop/site_selection/sites.csv',
                    delimiter=',')
hr_sites = pd.read_csv(
    'C:/Users/norri/Desktop/site_selection/hourly_sites.csv', delimiter=',')
npv_values = pd.read_csv('C:/Users/norri/Desktop/site_selection/npv.csv',
                         delimiter=',')
lte_params = pd.read_csv(
    'C:/Users/norri/Desktop/site_selection/lte_assumptions.csv',
    delimiter=',')

# ***this matches up with lines 79-82; in python, it was used
# to prevent duplicate column names

init_sites = sites.drop(['Type', 'Morphology'], axis=1)

# *** this variable is used in several calculations,
# and the merge with the larger hourly data set is resource
# intensive, so dropping observations that do not impact
# these calculations saves a significant amount of time
# in regards to your comment on 162, since I have been trying
# to find a way to make that merge run faster, I made a copy
# to test, but I don't think it's strictly necessary,
# as long as hr_sites isn't altered permanently

# for the comment starting on 110, I changed the non
# to actually prevent an accidental assignment and added
# another if statement

init_hr_sites = hr_sites[hr_sites.Hour_GBs > 0]

# NPV DATA

# All relevant NPV values from original Alteryx workflow future financial
# estimates may need to be implemented npv_values

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
# lte_params

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

# SECTION 2: FUNCTIONS

# this function takes the type and morphology and converts
# it into a code to make the xnpv function work faster
# more data could improve speed, like stats on most common
# morphologies and organizing by those
# testing shows nearly 30% decrease in runtime when the most
# frequent morphologies appear at top of list
# it should only be run once as long as the morph code carries through
# the iterations

# *** in reference to your funtions at 201-317, the morph function
# sets a morph_code that persists through the iterations (ir written
# properly, and allows for different NPV assumptions to be added ifmain
# easily)

def morph(type, morph):
    if type == 'Off-Strand' and morph == 'Dense Urban':
        morph_code = 1
    elif type == 'Off-Strand' and morph == 'Urban':
        morph_code = 2
    elif type == 'Off-Strand' and morph == 'Suburban':
        morph_code = 3
    elif type == 'On-Strand' and morph == 'Dense Urban':
        morph_code = 4
    elif type == 'On-Strand' and morph == 'Urban':
        morph_code = 5
    elif type == 'On-Strand' and morph == 'Suburban':
        morph_code = 6
    elif type == 'ROE Building' and morph == 'Dense Urban':
        morph_code = 7
    elif type == 'ROE Building' and morph == 'Urban':
        morph_code = 8
    elif type == 'ROE Building' and morph == 'Suburban':
        morph_code = 9
    else:
        print('error')
    return morph_code


# this function is used inside the xnpv function
# to change the values depending on morphology
# sane that applies here as above


def fin_arrays(code):
    cpx = np.empty([11, 1])
    opx = np.empty([11, 1])
    growth = np.empty([11, 1])
    mvno = np.empty([11, 1])
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
    elif code == 9:
        npv = npv_values.loc[:, 'roe_s']
    else:
        print('error')
    penet_rate = np.full((11, 1), float(npv[62]))
    for i in range(11):
        cpx[i] = float(npv[i + 3])
    for i in range(11):
        opx[i] = float(npv[i + 14])
    for i in range(11):
        growth[i] = float(npv[i + 40])
    for i in range(11):
        mvno[i] = float(npv[i + 51])
    array = np.hstack((cpx, opx, growth, mvno, penet_rate))
    return array


# morph_array function used to call proper
# npv array based on morph code


def morph_array(code):
    if code == 1:
        return off_du
    elif code == 2:
        return off_u
    elif code == 3:
        return off_s
    elif code == 4:
        return on_du
    elif code == 5:
        return on_u
    elif code == 6:
        return on_s
    elif code == 7:
        return roe_du
    elif code == 8:
        return roe_u
    elif code == 9:
        return roe_s
    else:
        print('error')


# XNPV Function - is called repeatedly to estimate
# the NPV oF a site

# changing the number of days in xnpv can affect the output
# so this variable is to test for those sorts of discrepancies

day_diff = 0.0

# the cell split is calculated by the elif when the site
# capacity has been met, the cell_split variable sets
# value for the new cap, not to exceed 2.0

cell_split = 2.0

# *** i'm not sure if your comment on 358 was about the xnpv function
# but since cell splits frequently occur and at all years,
# I can't think of a way to get this out of a loop, and it also
# runs very quickly


# relating to line 399, this sounds good, but take a look at that formula
# I put in my original documentation to make sure it stays intact


def xnpv(gbs, mo_cap, code):
    # slice 0 is cpx, 1 is opx, 2 is growth, 3 is mvno, 4 is penet_rate
    # *** note that I modified this to take the generic array, fixed
    # some calculations, and set an 'a' that defines when a site incurs
    # its second capital expenditure
    array = morph_array(code)
    flag = 0
    a = 0
    for i in range(11):
        if (gbs * array[i][4] * (array[i][2]) * 12) < (
                cell_split * mo_cap * 12):
            if (gbs * array[i][4] * (array[i][2]) * 12) < (mo_cap * 12):
                value[i] = gbs * array[i][4] * 12 * array[i][3] * array[i][2] - \
                           array[i][1] - other
            else:
                value[i] = gbs * array[i][4] * 12 * array[i][3] * array[i][2] - \
                           (2 * array[i][1]) - other
                if flag == 0:
                    a = i
                    flag = 1
        else:
            value[i] = gbs * array[i][4] * 12 * array[i][3] * array[i][2] - \
                       (2 * array[i][1]) - other
    date_0 = st_date[0]
    value[a] = value[a] - array[a][0]
    return int(sum([value_i / ((1.0 + disc_rt) **
                               (((date_i - date_0).days - day_diff) / 365.0))
                    for value_i, date_i in zip(value, st_date)]))


# SECTION 3: FIRST ITERATION TO GENERATE INHERENT NPV

# create npv arrays

# ***this creates permanent arrays that are called via index
# in the xnpv function, I found it saved quite a bit of time

# slice 0 is opex, 1 is opx, 2 is growth, 3 is mvno, 4 is penet_rate
off_du = fin_arrays(1)
off_u = fin_arrays(2)
off_s = fin_arrays(3)
on_du = fin_arrays(4)
on_u = fin_arrays(5)
on_s = fin_arrays(6)
roe_du = fin_arrays(7)
roe_u = fin_arrays(8)
roe_s = fin_arrays(9)
value = np.empty([11, 1])

# LTE and SINR calculations

# *** for these more complicated equations, I will verify them with Jason
# and let you know if anything changes

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

# *** referring to line 513, either first, last, etc. would have worked,
# but I thought the mean would be good for testing. the line below demonstrates
# a common practice in this program: figure out a value and put it in a
# column so each site has the same values

sites['gb_offload'] = sites.groupby('fict_site')['Sum_GBs'].transform(sum)

# brings daily and hourly data together, does calculations
# to get the busy hour

# *** this merge took about 50% of the total run time of my testing,
# so improving it would make it much faster

sites = pd.merge(sites, hr_sites, on='GridName').reset_index(drop=True)
sites['bin_req_hr_mbps'] = (sites['Hour_GBs'] * 8 * (2 ** 10)) / 3600
site_req = sites.groupby(['fict_site', 'event_hour'])['bin_req_hr_mbps']. \
    sum().reset_index()
sum_req = site_req.sort_values(by=['fict_site', 'bin_req_hr_mbps'],
                               ascending=[True, False])
sum_req = sum_req.groupby('fict_site').first().reset_index()
sites = pd.merge(sites, sum_req, left_on=['fict_site',
                                          'event_hour'],
                 right_on=['fict_site', 'event_hour']).reset_index(drop=True)

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

# for testing, you could evaluate whether gb_0ffload and max_cap
# change in each iteration, at least to to rule that out as a cause
# for NPV staying the same.

sites['bh_req_rbs'] = ((sites['Hour_GBs'] * 8 * (2 ** 10)) / 3600) / \
                      sites['rb_thru_put']
agg_sites = sites.groupby('fict_site')['bh_req_rbs'].sum().reset_index()
agg_sites['enb_util'] = np.ceil(agg_sites['bh_req_rbs']) / 400
temp_agg = sites.groupby('fict_site')['gb_offload'].mean().reset_index()
agg_sites['max_cap'] = (temp_agg['gb_offload'] / agg_sites['enb_util'])
site_t_m = sites.groupby('fict_site')[
    ('Type', 'Morphology')].first().reset_index()
agg_sites = pd.merge(agg_sites, site_t_m, on='fict_site')
agg_sites = pd.merge(agg_sites, temp_agg, on='fict_site')

# FIRST ITERATION OF ALGORITHM, runs functions, then
# orders and ranks the sites

# this morph code is only generated once to save time, it
# should stick with the sites through the loops

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

# *** dropped columns to avoid values carrying through loop and also
# automatic renaming
selected = (pd.DataFrame(init_ranking.iloc[0, :])).T
selected = selected[['fict_site', 'morph_code', 'npv']]

# all remaining positive NPV will be compared
# against any remaining NPV positive sites
# which will be in this candidates list

candidates = pd.DataFrame(init_ranking.iloc[1:, :]).reset_index(drop=True)
candidates = candidates[['fict_site', 'morph_code', 'npv']]

# for selected, candidates, and next_best, keeping just these
# three columns prevents duplicates and values carrying over through
# iterations

# PART 4: END OF FIRST ITERATION, LOOPED UNTIL COMPLETE

# ************* the outer loop here is definitely the next_best
# place to parallelize the algorithm, then just compare the outputs
# afterwards

for j in range(len(candidates)):
    start = timeit.default_timer()
    selected_bins = pd.merge(selected, init_sites, on='fict_site')
    temp_nb = pd.DataFrame([])
    for i in range(len(candidates)):
        # next_best is taken from the list of candidates
        # and selects one site to compare against the selected
        # dataframe, then daily sites are merged in so the bins
        # belonging to that candidate can be tested
        # gb_offload is calculated before adding hourly
        # in as it is above

        # *** in this version next_best is also used heavily later

        next_best = (pd.DataFrame(candidates.iloc[i, :])).T
        candidates_bins = pd.merge(next_best, init_sites, on='fict_site')
        ranked_bins = selected_bins.append(candidates_bins)
        rankbin_grp = ranked_bins.groupby('fict_site')
        ranked_bins['gb_offload'] = rankbin_grp['Sum_GBs'].transform(sum)

        sinr_bins = pd.merge(ranked_bins, bin_sinr, on='GridName')

        sinr_bins_unique = sinr_bins.drop_duplicates(subset='GridName')
        sinr_bins_dups = sinr_bins.loc[sinr_bins['GridName'].duplicated(), :]
        sbin_dup_grp = sinr_bins_dups.groupby('GridName')
        sinr_bins_dups['sum_rx_signal'] = sbin_dup_grp[
            'rx_signal_strength_mw'].transform(sum)
        sinr_bins = sinr_bins_unique.append(sinr_bins_dups)

        # this calculates an adjusted sinr from the comparison
        # of the selected list to the each candidate, once
        # per inner loop, and drops grids with low sinr

        # this portion is a part of what may be an unfinished functions
        # from Jason, I'll keep you updated

        sinr_bins_a = sinr_bins[sinr_bins['sum_rx_signal'].notnull()]
        sinr_bins_a['sinr_new'] = \
            sinr_bins['sum_rx_signal'].where(
                sinr_bins['sum_rx_signal'].isnull(),
                sinr_bins['rx_signal_strength_db'] -
                (np.log10((sinr_bins['sum_rx_signal'] +
                           (10 ** (sinr_bins['rx_sensitivity_db'] / 10)) /
                           1000) * 1000) * 10))
        sinr_bins_b = sinr_bins[sinr_bins['sum_rx_signal'].isnull()]
        sinr_bins_b['sinr_new'] = sinr_bins['sum_rx_signal'].where(
            sinr_bins['sum_rx_signal'].notnull(),
            sinr_bins['sinr'], axis=0)
        sinr_bins = sinr_bins_a.append(sinr_bins_b)

        sinr_bins = sinr_bins[sinr_bins.sinr_new >= -7.0]

        # *** I rounded here because it was causing issues with merging

        sinr_bins['sinr_new'] = sinr_bins['sinr_new'].round(0)
        sinr_bins = pd.merge(sinr_bins, lte_params, left_on='sinr_new',
                             right_on='SINR')
        sinr_bins['rb_thru_put'] = \
            (((sinr_bins['Code Rate'] * sinr_bins['symbols/SF'] *
               1000 * 12 * 400 * sinr_bins['2x2 MIMO Gain'] *
               sinr_bins['subframe allocation']) / 1000000) *
             ((1 - sinr_bins['retrans']) *
              (1 - sinr_bins['high  layer overhead'])) -
             (sinr_bins['overhead TP kbps'] / 1000)) / 400

        # at this point, make sure morph_code, etc are carried
        # through to lower the number of calculations made
        # *** drop columns here to avoid carrying NPV values through
        # similar to dropping rows in init_hr_sites, this does
        # lower the run time a little bit whenever rb_thru_put
        # is non-positive

        sinr_bins = sinr_bins[['GridName', 'fict_site', 'rb_thru_put',
                               'morph_code', 'gb_offload']]
        sinr_bins = sinr_bins[sinr_bins.rb_thru_put > 0]
        sinr_bins = pd.merge(sinr_bins, init_hr_sites, on='GridName')

        sinr_bins['bh_req_rbs'] = ((sinr_bins['Hour_GBs'] *
                                    8 * (2 ** 10)) / 3600) / \
                                  sinr_bins['rb_thru_put']
        agg_morph = sinr_bins.groupby('fict_site')[
            'morph_code'].first().reset_index()
        agg_sinr = sinr_bins.groupby('fict_site')[
            'bh_req_rbs'].sum().reset_index()

        # this final section does the same as above, creating
        # the inputs for the xnpv function

        agg_sinr['enb_util'] = np.ceil(agg_sinr['bh_req_rbs']) / 400

        temp_agg_sites = sinr_bins.groupby('fict_site')[
            'gb_offload'].mean().reset_index()
        agg_sinr = pd.merge(agg_sinr, temp_agg_sites, on='fict_site')
        agg_sinr = pd.merge(agg_sinr, agg_morph, on='fict_site')
        agg_sinr['max_cap'] = (
                agg_sinr['gb_offload'] / agg_sinr['enb_util'])


        agg_sinr['xnpv'] = agg_sinr.apply(lambda x:
                                          xnpv(x['gb_offload'], x['max_cap'],
                                               x['morph_code']), axis=1)

        # *** here I only had to make one function call instead of the previous
        # two

        # *** your comment in 762 is apt; there are actually two Values
        # in the adj_npv column, with the min being the new npv,
        # and the sum being the value that should be ranked on


        next_best['adj_npv'] = agg_sinr['xnpv'].min()
        next_best['sum_npv'] = agg_sinr['xnpv'].sum()
        next_best = next_best[['fict_site', 'adj_npv', 'sum_npv']]
        temp_nb = temp_nb.append(next_best)

        # end of inner loop

    # *** now the temp_nb is dropped when zero or less, make sure
    # the data is appending properly without duplicating

    new_ranking = temp_nb.loc[temp_nb['adj_npv'] > 0]

    # *** it's very important to rank by the summed npv, But
    # set the new site npv to the minimum (as the other values
    # is the dataframe of selected sites), so the next best sites
    # is the one that adds the most net value to a county, and
    # its NPV is adjusted by the existing interference from selected
    # bins

    new_ranking['rank'] = new_ranking['sum_npv'].rank(ascending=False)
    new_ranking = new_ranking.sort_values(by='rank').reset_index(drop='True')
    temp_candidates = pd.merge(new_ranking, candidates, on='fict_site')
    temp_candidates['npv'] = temp_candidates['adj_npv']
    temp_candidates = temp_candidates[['fict_site', 'morph_code', 'npv']]
    temp_selected = (pd.DataFrame(temp_candidates.iloc[0, :])).T
    selected = selected.append(temp_selected)
    candidates = pd.DataFrame(temp_candidates.iloc[1:, :])
    print(len(candidates))
    # put this in because sites will drop, making a full run
    # the length of sites uncessary
    if len(candidates) == 0:
        break


ranked_bins = pd.merge(selected, init_sites, on='fict_site')
rankbin_grp = ranked_bins.groupby('fict_site')
ranked_bins['gb_offload'] = rankbin_grp['Sum_GBs'].transform(sum)
sinr_bins = pd.merge(ranked_bins, bin_sinr, on='GridName')
sinr_bins_unique = sinr_bins.drop_duplicates(subset='GridName')
sinr_bins_dups = sinr_bins.loc[sinr_bins['GridName'].duplicated(), :]
sbin_dup_grp = sinr_bins_dups.groupby('GridName')
sinr_bins_dups['sum_rx_signal'] = sbin_dup_grp[
    'rx_signal_strength_mw'].transform(sum)
sinr_bins = sinr_bins_unique.append(sinr_bins_dups)
sinr_bins_a = sinr_bins[sinr_bins['sum_rx_signal'].notnull()]
sinr_bins_a['sinr_new'] = \
    sinr_bins['sum_rx_signal'].where(
        sinr_bins['sum_rx_signal'].isnull(),
        sinr_bins['rx_signal_strength_db'] -
        (np.log10((sinr_bins['sum_rx_signal'] +
                   (10 ** (sinr_bins['rx_sensitivity_db'] / 10)) /
                   1000) * 1000) * 10))
sinr_bins_b = sinr_bins[sinr_bins['sum_rx_signal'].isnull()]
sinr_bins_b['sinr_new'] = sinr_bins['sum_rx_signal'].where(
    sinr_bins['sum_rx_signal'].notnull(),
    sinr_bins['sinr'], axis=0)
sinr_bins = sinr_bins_a.append(sinr_bins_b)
sinr_bins = sinr_bins[sinr_bins.sinr_new >= -7.0]
sinr_bins['sinr_new'] = sinr_bins['sinr_new'].round(0)
sinr_bins = pd.merge(sinr_bins, lte_params, left_on='sinr_new',
                     right_on='SINR')
sinr_bins['rb_thru_put'] = \
    (((sinr_bins['Code Rate'] * sinr_bins['symbols/SF'] *
       1000 * 12 * 400 * sinr_bins['2x2 MIMO Gain'] *
       sinr_bins['subframe allocation']) / 1000000) *
     ((1 - sinr_bins['retrans']) *
      (1 - sinr_bins['high  layer overhead'])) -
     (sinr_bins['overhead TP kbps'] / 1000)) / 400
sinr_bins = sinr_bins[['GridName', 'fict_site', 'rb_thru_put',
                       'morph_code', 'gb_offload']]
sinr_bins = sinr_bins[sinr_bins.rb_thru_put > 0]
sinr_bins = pd.merge(sinr_bins, init_hr_sites, on='GridName')
sinr_bins['bh_req_rbs'] = ((sinr_bins['Hour_GBs'] *
                            8 * (2 ** 10)) / 3600) / \
                          sinr_bins['rb_thru_put']
agg_morph = sinr_bins.groupby('fict_site')[
    'morph_code'].first().reset_index()
agg_sinr = sinr_bins.groupby('fict_site')[
    'bh_req_rbs'].sum().reset_index()
agg_sinr['enb_util'] = np.ceil(agg_sinr['bh_req_rbs']) / 400
temp_agg_sites = sinr_bins.groupby('fict_site')[
    'gb_offload'].mean().reset_index()
agg_sinr = pd.merge(agg_sinr, temp_agg_sites, on='fict_site')
agg_sinr = pd.merge(agg_sinr, agg_morph, on='fict_site')
agg_sinr['max_cap'] = (
        agg_sinr['gb_offload'] / agg_sinr['enb_util'])
agg_sinr['xnpv'] = agg_sinr.apply(lambda x:
                                  xnpv(x['gb_offload'], x['max_cap'],
                                       x['morph_code']), axis=1)

#  something similar here would be a good test to see fi Values
# do change

# init_ranking.to_csv('first_ranking.csv')
# agg_sinr.to_csv('final_ranking_b.csv')
