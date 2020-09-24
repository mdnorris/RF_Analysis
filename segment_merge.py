# last updated 3/10/2020, merges segments and provides final
# county npv calculation

import numpy as np
import pandas as pd

sites = pd.read_csv('site_daily.csv', delimiter=',')
hr_sites = pd.read_csv('bin_daily.csv', delimiter=',')
npv_values = pd.read_csv('npv_high_vz_prop.csv', delimiter=',')
lte_params = pd.read_csv('lte_assumptions.csv', delimiter=',')

# initial site information
sites['type_morph'] = sites['asset_type'] + sites['morphology']

print('initial sites', end='  ')
print(len(sites['asset_id'].unique()))
initial_sites = pd.Series(len(sites['asset_id'].unique()))

print('initial bins', end='  ')
print(len(hr_sites['bin_10'].unique()))
init_bins = pd.Series(len(sites['bin_10'].unique()))

print('initial gbs', end='  ')
print(hr_sites['hourly_usage_gb'].sum())
init_gbs = pd.Series(hr_sites['hourly_usage_gb'].sum())

print('morphology counts', end='  ')
print(sites['morphology'].value_counts())
init_morphology = pd.DataFrame(sites['morphology'].value_counts())

print('asset_type_counts', end='  ')
print(sites['asset_type'].value_counts())
init_asset_type = pd.DataFrame(sites['asset_type'].value_counts())

print('type/morph counts', end='  ')
print(sites['type_morph'].value_counts())
init_type_morph = pd.DataFrame(sites['asset_type'].value_counts())

print((sites.isna().sum()) / len(sites) * 100)
sites = sites.dropna()

print((hr_sites.isna().sum() / len(sites)) * 100)
hr_sites = hr_sites.dropna()

sites = sites.rename(columns={'bin_10': 'GridName', 'sum_GBs_hourly_monthly': 'Sum_GBs',
                              'asset_id': 'fict_site', 'asset_type': 'Type',
                              'path_loss_db': 'path_loss_umi_db', 'morphology': 'Morphology'})
hr_sites = hr_sites.rename(columns={'bin_10': 'GridName', 'hourly_usage_gb': 'Hour_GBs'})

rb_bins = pd.merge(sites, hr_sites, on='GridName')
rb_bins['bin_req_hr_mbps'] = (rb_bins['Hour_GBs'] * 8 * (2 ** 10)) / 3600
sum_req = rb_bins.sort_values(by=['GridName', 'bin_req_hr_mbps'], ascending=[True, False])
bin_req = rb_bins.groupby('GridName')['bin_req_hr_mbps'].max().reset_index()

day_usage = hr_sites.groupby('GridName')['Hour_GBs'].sum().reset_index()
sites = pd.merge(sites, day_usage, on='GridName')
sites = sites.drop(['segment', 'Sum_GBs', 'fips'], axis=1)
init_sites = sites

# NPV DATA

npv_values.columns = ['non', 'pole_du', 'pole_u', 'pole_s', 'pole_r', 'off_du', 'off_u',
                      'off_s', 'off_r', 'roe_du', 'roe_u', 'roe_s', 'roe_r',
                      'smb_du', 'smb_u', 'smb_s', 'smb_r']

# This creates time periods for npv
st_date20 = pd.date_range(start='2020-06-30', periods=11, freq='12M')
st_date21 = pd.date_range(start='2021-06-30', periods=10, freq='12M')
st_date22 = pd.date_range(start='2022-06-30', periods=9, freq='12M')
st_date23 = pd.date_range(start='2023-06-30', periods=8, freq='12M')
st_date24 = pd.date_range(start='2024-06-30', periods=7, freq='12M')
st_date25 = pd.date_range(start='2025-06-30', periods=6, freq='12M')
st_date26 = pd.date_range(start='2026-06-30', periods=5, freq='12M')
st_date27 = pd.date_range(start='2027-06-30', periods=4, freq='12M')
st_date28 = pd.date_range(start='2028-06-30', periods=3, freq='12M')
st_date29 = pd.date_range(start='2029-06-30', periods=2, freq='12M')
st_date30 = pd.date_range(start='2030-06-30', periods=1, freq='12M')

disc_rt = .15

# LTE INPUTS

rx_sensitivity_db = -89.4


# SECTION 2: FUNCTIONS


def morph(type, morph):
    global morph_code
    if type == 'Pole' and morph == 'Dense Urban':
        morph_code = 1
    elif type == 'Pole' and morph == 'Urban':
        morph_code = 2
    elif type == 'Pole' and morph == 'Suburban':
        morph_code = 3
    elif type == 'Pole' and morph == 'Rural':
        morph_code = 4
    elif type == 'Off' and morph == 'Dense Urban':
        morph_code = 5
    elif type == 'Off' and morph == 'Urban':
        morph_code = 6
    elif type == 'Off' and morph == 'Suburban':
        morph_code = 7
    elif type == 'Off' and morph == 'Rural':
        morph_code = 8
    elif type == 'ROE' and morph == 'Dense Urban':
        morph_code = 9
    elif type == 'ROE' and morph == 'Urban':
        morph_code = 10
    elif type == 'ROE' and morph == 'Suburban':
        morph_code = 11
    elif type == 'ROE' and morph == 'Rural':
        morph_code = 12
    elif type == 'SMB' and morph == 'Dense Urban':
        morph_code = 13
    elif type == 'SMB' and morph == 'Urban':
        morph_code = 14
    elif type == 'SMB' and morph == 'Suburban':
        morph_code = 15
    elif type == 'SMB' and morph == 'Rural':
        morph_code = 16
    else:
        print('error')
    return morph_code


def fin_arrays(code):
    global npv
    cpx = np.empty([11, 1])
    opx = np.empty([11, 1])
    growth = np.empty([11, 1])
    mvno = np.empty([11, 1])
    if code == 1:
        npv = npv_values.loc[:, 'pole_du']
    elif code == 2:
        npv = npv_values.loc[:, 'pole_u']
    elif code == 3:
        npv = npv_values.loc[:, 'pole_s']
    elif code == 4:
        npv = npv_values.loc[:, 'pole_r']
    elif code == 5:
        npv = npv_values.loc[:, 'off_du']
    elif code == 6:
        npv = npv_values.loc[:, 'off_u']
    elif code == 7:
        npv = npv_values.loc[:, 'off_s']
    elif code == 8:
        npv = npv_values.loc[:, 'off_r']
    elif code == 9:
        npv = npv_values.loc[:, 'roe_du']
    elif code == 10:
        npv = npv_values.loc[:, 'roe_u']
    elif code == 11:
        npv = npv_values.loc[:, 'roe_s']
    elif code == 12:
        npv = npv_values.loc[:, 'roe_r']
    elif code == 13:
        npv = npv_values.loc[:, 'smb_du']
    elif code == 14:
        npv = npv_values.loc[:, 'smb_u']
    elif code == 15:
        npv = npv_values.loc[:, 'smb_s']
    elif code == 16:
        npv = npv_values.loc[:, 'smb_r']
    else:
        print('error')
    for i in range(11):
        cpx[i] = float(npv[i + 1])
    for i in range(11):
        opx[i] = float(npv[i + 12])
    for i in range(11):
        growth[i] = float(npv[i + 23])
    for i in range(11):
        mvno[i] = float(npv[i + 34])
    array = np.hstack((cpx, opx, growth, mvno))
    return array


def morph_array(code):
    if code == 1:
        return pole_du
    elif code == 2:
        return pole_u
    elif code == 3:
        return pole_s
    elif code == 4:
        return pole_r
    elif code == 5:
        return off_du
    elif code == 6:
        return off_u
    elif code == 7:
        return off_s
    elif code == 8:
        return off_r
    elif code == 9:
        return roe_du
    elif code == 10:
        return roe_u
    elif code == 11:
        return roe_s
    elif code == 12:
        return roe_r
    elif code == 13:
        return smb_du
    elif code == 14:
        return smb_u
    elif code == 15:
        return smb_s
    elif code == 16:
        return smb_r
    else:
        print('error')


day_diff = 0.0
cell_split = 2.0


def capex_21(gbs, mo_cap, code):
    array = morph_array(code)
    array = array[1:11, :]
    debit = 0
    for i in range(10):
        if (gbs * (array[i][2]) * 365) >= (mo_cap * 365):
            debit = array[i][0]
            return debit


def capex_22(gbs, mo_cap, code):
    array = morph_array(code)
    array = array[2:11, :]
    for i in range(9):
        if (gbs * (array[i][2]) * 365) >= (mo_cap * 365):
            debit = array[i][0]
            return debit


def capex_23(gbs, mo_cap, code):
    array = morph_array(code)
    array = array[3:11, :]
    debit = 0
    for i in range(8):
        if (gbs * (array[i][2]) * 365) >= (mo_cap * 365):
            debit = array[i][0]
            return debit


def capex_24(gbs, mo_cap, code):
    array = morph_array(code)
    array = array[4:11, :]
    debit = 0
    for i in range(7):
        if (gbs * (array[i][2]) * 365) >= (mo_cap * 365):
            debit = array[i][0]
            return debit


def capex_25(gbs, mo_cap, code):
    array = morph_array(code)
    array = array[5:11, :]
    debit = 0
    for i in range(6):
        if (gbs * (array[i][2]) * 365) >= (mo_cap * 365):
            debit = array[i][0]
            return debit


def capex_26(gbs, mo_cap, code):
    array = morph_array(code)
    array = array[6:11, :]
    debit = 0
    for i in range(5):
        if (gbs * (array[i][2]) * 365) >= (mo_cap * 365):
            debit = array[i][0]
            return debit


def capex_27(gbs, mo_cap, code):
    array = morph_array(code)
    array = array[7:11, :]
    debit = 0
    for i in range(4):
        if (gbs * (array[i][2]) * 365) >= (mo_cap * 365):
            debit = array[i][0]
            return debit


def capex_28(gbs, mo_cap, code):
    array = morph_array(code)
    array = array[8:11, :]
    debit = 0
    for i in range(3):
        if (gbs * (array[i][2]) * 365) >= (mo_cap * 365):
            debit = array[i][0]
            return debit


def capex_29(gbs, mo_cap, code):
    array = morph_array(code)
    array = array[9:11, :]
    debit = 0
    for i in range(2):
        if (gbs * (array[i][2]) * 365) >= (mo_cap * 365):
            debit = array[i][0]
            return debit


def capex_30(gbs, mo_cap, code):
    array = morph_array(code)
    array = array[10:11, :]
    debit = 0
    for i in range(10):
        if (gbs * (array[i][2]) * 365) >= (mo_cap * 365):
            debit = array[i][0]
            return debit


def opex_21(gbs, mo_cap, code):
    array = morph_array(code)
    array = array[1:11, :]
    debit = 0
    for i in range(10):
        if (gbs * (array[i][2]) * 365) >= (mo_cap * 365):
            debit = debit + array[i][1]
    return debit


def opex_22(gbs, mo_cap, code):
    array = morph_array(code)
    array = array[2:11, :]
    debit = 0
    for i in range(9):
        if (gbs * (array[i][2]) * 365) >= (mo_cap * 365):
            debit = debit + array[i][1]
    return debit


def opex_23(gbs, mo_cap, code):
    array = morph_array(code)
    array = array[3:11, :]
    debit = 0
    for i in range(8):
        if (gbs * (array[i][2]) * 365) >= (mo_cap * 365):
            debit = debit + array[i][1]
    return debit


def opex_24(gbs, mo_cap, code):
    array = morph_array(code)
    array = array[4:11, :]
    debit = 0
    for i in range(7):
        if (gbs * (array[i][2]) * 365) >= (mo_cap * 365):
            debit = debit + array[i][1]
    return debit


def opex_25(gbs, mo_cap, code):
    array = morph_array(code)
    array = array[5:11, :]
    debit = 0
    for i in range(6):
        if (gbs * (array[i][2]) * 365) >= (mo_cap * 365):
            debit = debit + array[i][1]
    return debit


def opex_26(gbs, mo_cap, code):
    array = morph_array(code)
    array = array[6:11, :]
    debit = 0
    for i in range(5):
        if (gbs * (array[i][2]) * 365) >= (mo_cap * 365):
            debit = debit + array[i][1]
    return debit


def opex_27(gbs, mo_cap, code):
    array = morph_array(code)
    array = array[7:11, :]
    debit = 0
    for i in range(4):
        if (gbs * (array[i][2]) * 365) >= (mo_cap * 365):
            debit = debit + array[i][1]
    return debit


def opex_28(gbs, mo_cap, code):
    array = morph_array(code)
    array = array[8:11, :]
    debit = 0
    for i in range(3):
        if (gbs * (array[i][2]) * 365) >= (mo_cap * 365):
            debit = debit + array[i][1]
    return debit


def opex_29(gbs, mo_cap, code):
    array = morph_array(code)
    array = array[9:11, :]
    debit = 0
    for i in range(2):
        if (gbs * (array[i][2]) * 365) >= (mo_cap * 365):
            debit = debit + array[i][1]
    return debit


def opex_30(gbs, mo_cap, code):
    array = morph_array(code)
    array = array[10:11, :]
    debit = 0
    for i in range(1):
        if (gbs * (array[i][2]) * 365) >= (mo_cap * 365):
            debit = debit + array[i][1]
    return debit


def split21(gbs, mo_cap, code):
    # slice 0 is cpx, 1 is opx, 2 is growth, 3 is mvno,
    array = morph_array(code)
    array = array[1:11, :]
    year = 1
    for i in range(10):
        if (gbs * (array[i][2]) * 365) >= (mo_cap * 365):
            return year
        else:
            year = year + 1


def split22(gbs, mo_cap, code):
    # slice 0 is cpx, 1 is opx, 2 is growth, 3 is mvno,
    value = np.empty([9, 1])
    array = morph_array(code)
    array = array[2:11, :]
    year = 2
    for i in range(9):
        if (gbs * (array[i][2]) * 365) >= (mo_cap * 365):
            return year
        else:
            year = year + 1


def split23(gbs, mo_cap, code):
    # slice 0 is cpx, 1 is opx, 2 is growth, 3 is mvno,
    value = np.empty([8, 1])
    array = morph_array(code)
    array = array[3:11, :]
    year = 3
    for i in range(8):
        if (gbs * (array[i][2]) * 365) >= (mo_cap * 365):
            return year
        else:
            year = year + 1


def split24(gbs, mo_cap, code):
    # slice 0 is cpx, 1 is opx, 2 is growth, 3 is mvno,
    value = np.empty([7, 1])
    array = morph_array(code)
    array = array[4:11, :]
    year = 4
    for i in range(7):
        if (gbs * (array[i][2]) * 365) >= (mo_cap * 365):
            return year
        else:
            year = year + 1


def split25(gbs, mo_cap, code):
    # slice 0 is cpx, 1 is opx, 2 is growth, 3 is mvno,
    value = np.empty([6, 1])
    array = morph_array(code)
    array = array[5:11, :]
    year = 5
    for i in range(6):
        if (gbs * (array[i][2]) * 365) >= (mo_cap * 365):
            return year
        else:
            year = year + 1


def split26(gbs, mo_cap, code):
    # slice 0 is cpx, 1 is opx, 2 is growth, 3 is mvno,
    value = np.empty([5, 1])
    array = morph_array(code)
    array = array[6:11, :]
    year = 6
    for i in range(5):
        if (gbs * (array[i][2]) * 365) >= (mo_cap * 365):
            return year
        else:
            year = year + 1


def split27(gbs, mo_cap, code):
    # slice 0 is cpx, 1 is opx, 2 is growth, 3 is mvno,
    value = np.empty([4, 1])
    array = morph_array(code)
    array = array[7:11, :]
    year = 7
    for i in range(4):
        if (gbs * (array[i][2]) * 365) >= (mo_cap * 365):
            return year
        else:
            year = year + 1


def split28(gbs, mo_cap, code):
    # slice 0 is cpx, 1 is opx, 2 is growth, 3 is mvno,
    value = np.empty([3, 1])
    array = morph_array(code)
    array = array[8:11, :]
    year = 8
    for i in range(3):
        if (gbs * (array[i][2]) * 365) >= (mo_cap * 365):
            return year
        else:
            year = year + 1


def split29(gbs, mo_cap, code):
    # slice 0 is cpx, 1 is opx, 2 is growth, 3 is mvno,
    value = np.empty([2, 1])
    array = morph_array(code)
    array = array[9:11, :]
    year = 9
    for i in range(2):
        if (gbs * (array[i][2]) * 365) >= (mo_cap * 365):
            return year
        else:
            year = year + 1


def split30(gbs, mo_cap, code):
    # slice 0 is cpx, 1 is opx, 2 is growth, 3 is mvno,
    value = np.empty([1, 1])
    array = morph_array(code)
    array = array[10:11, :]
    year = 10
    for i in range(1):
        if (gbs * (array[i][2]) * 365) >= (mo_cap * 365):
            return year
        else:
            year = year + 1


def npv21(gbs, code, mo_cap):
    # slice 0 is cpx, 1 is opx, 2 is growth, 3 is mvno,
    value = np.empty([10, 1])
    array = morph_array(code)
    array = array[1:11, :]
    for i in range(10):
        if (gbs * (array[i][2]) * 365) < (cell_split * mo_cap * 365):
            value[i] = gbs * 365 * array[i][3] * array[i][2] - array[i][1]
        else:
            value[i] = cell_split * mo_cap * 365
    date_0 = st_date20[0]
    value[0] = value[0] - array[0][0]
    return int(sum([value_i / ((1.0 + disc_rt) ** ((date_i - date_0).days / 365.0))
                    for value_i, date_i in zip(value, st_date21)]))


def npv22(gbs, code, mo_cap):
    # slice 0 is cpx, 1 is opx, 2 is growth, 3 is mvno,
    value = np.empty([9, 1])
    array = morph_array(code)
    array = array[2:11, :]
    a = 0
    for i in range(9):
        if (gbs * (array[i][2]) * 365) < (cell_split * mo_cap * 365):
            value[i] = gbs * 365 * array[i][3] * array[i][2] - array[i][1]
        else:
            value[i] = cell_split * mo_cap * 365
    date_0 = st_date20[0]

    return int(sum([value_i / ((1.0 + disc_rt) ** (((date_i - date_0).days - day_diff) / 365.0))
                    for value_i, date_i in zip(value, st_date22)]))


def npv23(gbs, code, mo_cap):
    # slice 0 is cpx, 1 is opx, 2 is growth, 3 is mvno,
    value = np.empty([8, 1])
    array = morph_array(code)
    array = array[3:11, :]
    a = 0
    for i in range(8):
        if (gbs * (array[i][2]) * 365) < (cell_split * mo_cap * 365):
            value[i] = gbs * 365 * array[i][3] * array[i][2] - array[i][1]
        else:
            value[i] = cell_split * mo_cap * 365
    date_0 = st_date20[0]
    value[a] = value[a] - array[a][0]
    return int(sum([value_i / ((1.0 + disc_rt) ** (((date_i - date_0).days - day_diff) / 365.0))
                    for value_i, date_i in zip(value, st_date23)]))


def npv24(gbs, code, mo_cap):
    # slice 0 is cpx, 1 is opx, 2 is growth, 3 is mvno,
    value = np.empty([7, 1])
    array = morph_array(code)
    array = array[4:11, :]
    a = 0
    for i in range(7):
        if (gbs * (array[i][2]) * 365) < (cell_split * mo_cap * 365):
            value[i] = gbs * 365 * array[i][3] * array[i][2] - array[i][1]
        else:
            value[i] = cell_split * mo_cap * 365
    date_0 = st_date20[0]
    value[a] = value[a] - array[a][0]
    return int(sum([value_i / ((1.0 + disc_rt) ** (((date_i - date_0).days - day_diff) / 365.0))
                    for value_i, date_i in zip(value, st_date24)]))


def npv25(gbs, code, mo_cap):
    # slice 0 is cpx, 1 is opx, 2 is growth, 3 is mvno,
    value = np.empty([6, 1])
    array = morph_array(code)
    array = array[5:11, :]
    a = 0
    for i in range(6):
        if (gbs * (array[i][2]) * 365) < (cell_split * mo_cap * 365):
            value[i] = gbs * 365 * array[i][3] * array[i][2] - array[i][1]
        else:
            value[i] = cell_split * mo_cap * 365
    date_0 = st_date20[0]
    value[a] = value[a] - array[a][0]
    return int(sum([value_i / ((1.0 + disc_rt) ** (((date_i - date_0).days - day_diff) / 365.0))
                    for value_i, date_i in zip(value, st_date25)]))


def npv26(gbs, code, mo_cap):
    # slice 0 is cpx, 1 is opx, 2 is growth, 3 is mvno,
    value = np.empty([5, 1])
    array = morph_array(code)
    array = array[6:11, :]
    a = 0
    for i in range(5):
        if (gbs * (array[i][2]) * 365) < (cell_split * mo_cap * 365):
            value[i] = gbs * 365 * array[i][3] * array[i][2] - array[i][1]
        else:
            value[i] = cell_split * mo_cap * 365
    date_0 = st_date20[0]
    value[a] = value[a] - array[a][0]
    return int(sum([value_i / ((1.0 + disc_rt) ** (((date_i - date_0).days - day_diff) / 365.0))
                    for value_i, date_i in zip(value, st_date26)]))


def npv27(gbs, code, mo_cap):
    # slice 0 is cpx, 1 is opx, 2 is growth, 3 is mvno,
    value = np.empty([4, 1])
    array = morph_array(code)
    array = array[7:11, :]
    a = 0
    for i in range(4):
        if (gbs * (array[i][2]) * 365) < (cell_split * mo_cap * 365):
            value[i] = gbs * 365 * array[i][3] * array[i][2] - array[i][1]
        else:
            value[i] = cell_split * mo_cap * 365
    date_0 = st_date20[0]
    value[a] = value[a] - array[a][0]
    return int(sum([value_i / ((1.0 + disc_rt) ** (((date_i - date_0).days - day_diff) / 365.0))
                    for value_i, date_i in zip(value, st_date27)]))


def npv28(gbs, code, mo_cap):
    # slice 0 is cpx, 1 is opx, 2 is growth, 3 is mvno,
    value = np.empty([3, 1])
    array = morph_array(code)
    array = array[8:11, :]
    for i in range(3):
        if (gbs * (array[i][2]) * 365) < (cell_split * mo_cap * 365):
            value[i] = gbs * 365 * array[i][3] * array[i][2] - array[i][1]
        else:
            value[i] = cell_split * mo_cap * 365
    date_0 = st_date20[0]
    value[0] = value[0] - array[0][0]
    return int(sum([value_i / ((1.0 + disc_rt) ** ((date_i - date_0).days / 365.0))
                    for value_i, date_i in zip(value, st_date28)]))


def npv29(gbs, code, mo_cap):
    # slice 0 is cpx, 1 is opx, 2 is growth, 3 is mvno,
    value = np.empty([2, 1])
    array = morph_array(code)
    array = array[9:11, :]
    a = 0
    for i in range(2):
        if (gbs * (array[i][2]) * 365) < (cell_split * mo_cap * 365):
            value[i] = gbs * 365 * array[i][3] * array[i][2] - array[i][1]
        else:
            value[i] = cell_split * mo_cap * 365
    date_0 = st_date20[0]
    value[a] = value[a] - array[a][0]
    return int(sum([value_i / ((1.0 + disc_rt) ** (((date_i - date_0).days - day_diff) / 365.0))
                    for value_i, date_i in zip(value, st_date29)]))


def npv30(gbs, code, mo_cap):
    # slice 0 is cpx, 1 is opx, 2 is growth, 3 is mvno,
    value = np.empty([1, 1])
    array = morph_array(code)
    array = array[10:11, :]
    a = 0
    for i in range(1):
        if (gbs * (array[i][2]) * 365) < (cell_split * mo_cap * 365):
            value[i] = gbs * 365 * array[i][3] * array[i][2] - array[i][1]
        else:
            value[i] = cell_split * mo_cap * 365
    date_0 = st_date20[0]
    value[a] = value[a] - array[a][0]
    return int(sum([value_i / ((1.0 + disc_rt) ** (((date_i - date_0).days - day_diff) / 365.0))
                    for value_i, date_i in zip(value, st_date30)]))


def extra_offload21(gbs, code, mo_cap):
    cap = np.empty([10, 1])
    array = morph_array(code)
    array = array[1:11, :]
    for i in range(10):
        if (gbs * (array[i][2]) * 365) < (cell_split * mo_cap * 365):
            cap[i] = (cell_split * mo_cap * 365) - (gbs * (array[i][2]) * 365)
        else:
            cap[i] = 0
    return cap


def extra_offload22(gbs, code, mo_cap):
    cap = np.empty([9, 1])
    array = morph_array(code)
    array = array[2:11, :]
    for i in range(9):
        if (gbs * (array[i][2]) * 365) < (cell_split * mo_cap * 365):
            cap[i] = (cell_split * mo_cap * 365) - (gbs * (array[i][2]) * 365)
        else:
            cap[i] = 0
    return cap


def extra_offload23(gbs, code, mo_cap):
    cap = np.empty([8, 1])
    array = morph_array(code)
    array = array[3:11, :]
    for i in range(8):
        if (gbs * (array[i][2]) * 365) < (cell_split * mo_cap * 365):
            cap[i] = (cell_split * mo_cap * 365) - (gbs * (array[i][2]) * 365)
        else:
            cap[i] = 0
    return cap


def extra_offload24(gbs, code, mo_cap):
    cap = np.empty([7, 1])
    array = morph_array(code)
    array = array[4:11, :]
    for i in range(7):
        if (gbs * (array[i][2]) * 365) < (cell_split * mo_cap * 365):
            cap[i] = (cell_split * mo_cap * 365) - (gbs * (array[i][2]) * 365)
        else:
            cap[i] = 0
    return cap


def extra_offload25(gbs, code, mo_cap):
    cap = np.empty([6, 1])
    array = morph_array(code)
    array = array[5:11, :]
    for i in range(6):
        if (gbs * (array[i][2]) * 365) < (cell_split * mo_cap * 365):
            cap[i] = (cell_split * mo_cap * 365) - (gbs * (array[i][2]) * 365)
        else:
            cap[i] = 0
    return cap


def extra_offload26(gbs, code, mo_cap):
    cap = np.empty([5, 1])
    array = morph_array(code)
    array = array[6:11, :]
    for i in range(5):
        if (gbs * (array[i][2]) * 365) < (cell_split * mo_cap * 365):
            cap[i] = (cell_split * mo_cap * 365) - (gbs * (array[i][2]) * 365)
        else:
            cap[i] = 0
    return cap


def extra_offload27(gbs, code, mo_cap):
    cap = np.empty([4, 1])
    array = morph_array(code)
    array = array[7:11, :]
    for i in range(4):
        if (gbs * (array[i][2]) * 365) < (cell_split * mo_cap * 365):
            cap[i] = (cell_split * mo_cap * 365) - (gbs * (array[i][2]) * 365)
        else:
            cap[i] = 0
    return cap


def extra_offload28(gbs, code, mo_cap):
    cap = np.empty([3, 1])
    array = morph_array(code)
    array = array[8:11, :]
    for i in range(3):
        if (gbs * (array[i][2]) * 365) < (cell_split * mo_cap * 365):
            cap[i] = (cell_split * mo_cap * 365) - (gbs * (array[i][2]) * 365)
        else:
            cap[i] = 0
    return cap


def extra_offload29(gbs, code, mo_cap):
    cap = np.empty([2, 1])
    array = morph_array(code)
    array = array[9:11, :]
    for i in range(2):
        if (gbs * (array[i][2]) * 365) < (cell_split * mo_cap * 365):
            cap[i] = (cell_split * mo_cap * 365) - (gbs * (array[i][2]) * 365)
        else:
            cap[i] = 0
    return cap


def extra_offload30(gbs, code, mo_cap):
    cap = np.empty([1, 1])
    array = morph_array(code)
    array = array[10:11, :]
    for i in range(1):
        if (gbs * (array[i][2]) * 365) < (cell_split * mo_cap * 365):
            cap[i] = (cell_split * mo_cap * 365) - (gbs * (array[i][2]) * 365)
        else:
            cap[i] = 0
    return cap


def rb_thru_put(code_rate, symbols, mimo, subframe, retrans, high_layer_over, over_tp_kbps):
    rb_thru = (((code_rate * symbols * 4800000 * mimo * subframe) / 1000000) *
               ((1 - retrans) * (1 - high_layer_over)) - (over_tp_kbps / 1000)) / 400
    return rb_thru


def rx_calc(path_loss_umi_db):
    rx_signal_strength_db = 37.0 - path_loss_umi_db
    sinr = (rx_signal_strength_db - rx_sensitivity_db).round(0).astype(int)
    rx_signal_strength_mw = (10 ** ((37.0 - path_loss_umi_db) / 10) / 1000.000000000)
    return rx_signal_strength_db, sinr, rx_signal_strength_mw


def sinr_new(sum_rx_signal, rx_signal_strength_db):
    # note that -89.4 here is rx_sensitivity_db
    sinr_nouveau = np.round(sum_rx_signal.where(sum_rx_signal.isnull(), rx_signal_strength_db -
                                                (np.log10((sum_rx_signal + (10 ** (-89.4 / 10)) / 1000) * 1000) * 10)),
                            0)
    return sinr_nouveau


def sinr_new2(sum_rx_signal, rx_signal_strength_db):
    # note that -89.4 here is rx_sensitivity_db
    sinr_nu = np.round(sum_rx_signal.where(sum_rx_signal.isnull(), rx_signal_strength_db -
                                           (np.log10((sum_rx_signal + (10 ** (-89.4 / 10)) / 1000) * 1000) * 10)), 0)
    return sinr_nu


def reverse_morph_type(code):
    global type, morph, type_morph
    if code == 1:
        type = 'Pole'
        morph = 'Dense Urban'
        type_morph = 'Pole/Dense Urban'
    elif code == 2:
        type = 'Pole'
        morph = 'Urban'
        type_morph = 'Pole/Urban'
    elif code == 3:
        type = 'Pole'
        morph = 'Suburban'
        type_morph = 'Pole / Suburban'
    elif code == 4:
        type = 'Pole'
        morph = 'Rural'
        type_morph = 'Pole / Rural'
    elif code == 5:
        type = 'Off'
        morph = 'Dense Urban'
        type_morph = 'Off / Dense Urban'
    elif code == 6:
        type = 'Off'
        morph = 'Urban'
        type_morph = 'Off / Urban'
    elif code == 7:
        type = 'Off'
        morph = 'Suburban'
        type_morph = 'Off / Suburban'
    elif code == 8:
        type = 'Off'
        morph = 'Rural'
        type_morph = 'Off / Rural'
    elif code == 9:
        type = 'ROE'
        morph = 'Dense Urban'
        type_morph = 'ROE / Dense Urban'
    elif code == 10:
        type = 'ROE'
        morph = 'Urban'
        type_morph = 'ROE / Urban'
    elif code == 11:
        type = 'ROE'
        morph = 'Suburban'
        type_morph = 'ROE / Suburban'
    elif code == 12:
        type = 'ROE'
        morph = 'Rural'
        type_morph = 'ROE / Rural'
    elif code == 13:
        type = 'SMB'
        morph = 'Dense Urban'
        type_morph = 'SMB / Dense Urban'
    elif code == 14:
        type = 'SMB'
        morph = 'Urban'
        type_morph = 'SMB / Urban'
    elif code == 15:
        type = 'SMB'
        morph = 'Suburban'
        type_morph = 'SMB / Suburban'
    elif code == 16:
        type = 'SMB'
        morph = 'Rural'
        type_morph = 'SMB / Rural'
    else:
        print('error')
    return type


def reverse_morph_morph(code):
    global type, morph, type_morph
    if code == 1:
        type = 'Pole'
        morph = 'Dense Urban'
        type_morph = 'Pole/Dense Urban'
    elif code == 2:
        type = 'Pole'
        morph = 'Urban'
        type_morph = 'Pole/Urban'
    elif code == 3:
        type = 'Pole'
        morph = 'Suburban'
        type_morph = 'Pole / Suburban'
    elif code == 4:
        type = 'Pole'
        morph = 'Rural'
        type_morph = 'Pole / Rural'
    elif code == 5:
        type = 'Off'
        morph = 'Dense Urban'
        type_morph = 'Off / Dense Urban'
    elif code == 6:
        type = 'Off'
        morph = 'Urban'
        type_morph = 'Off / Urban'
    elif code == 7:
        type = 'Off'
        morph = 'Suburban'
        type_morph = 'Off / Suburban'
    elif code == 8:
        type = 'Off'
        morph = 'Rural'
        type_morph = 'Off / Rural'
    elif code == 9:
        type = 'ROE'
        morph = 'Dense Urban'
        type_morph = 'ROE / Dense Urban'
    elif code == 10:
        type = 'ROE'
        morph = 'Urban'
        type_morph = 'ROE / Urban'
    elif code == 11:
        type = 'ROE'
        morph = 'Suburban'
        type_morph = 'ROE / Suburban'
    elif code == 12:
        type = 'ROE'
        morph = 'Rural'
        type_morph = 'ROE / Rural'
    elif code == 13:
        type = 'SMB'
        morph = 'Dense Urban'
        type_morph = 'SMB / Dense Urban'
    elif code == 14:
        type = 'SMB'
        morph = 'Urban'
        type_morph = 'SMB / Urban'
    elif code == 15:
        type = 'SMB'
        morph = 'Suburban'
        type_morph = 'SMB / Suburban'
    elif code == 16:
        type = 'SMB'
        morph = 'Rural'
        type_morph = 'SMB / Rural'
    else:
        print('error')
    return morph


def reverse_morph_type_morph(code):
    global type, morph, type_morph
    if code == 1:
        type = 'Pole'
        morph = 'Dense Urban'
        type_morph = 'Pole/Dense Urban'
    elif code == 2:
        type = 'Pole'
        morph = 'Urban'
        type_morph = 'Pole/Urban'
    elif code == 3:
        type = 'Pole'
        morph = 'Suburban'
        type_morph = 'Pole / Suburban'
    elif code == 4:
        type = 'Pole'
        morph = 'Rural'
        type_morph = 'Pole / Rural'
    elif code == 5:
        type = 'Off'
        morph = 'Dense Urban'
        type_morph = 'Off / Dense Urban'
    elif code == 6:
        type = 'Off'
        morph = 'Urban'
        type_morph = 'Off / Urban'
    elif code == 7:
        type = 'Off'
        morph = 'Suburban'
        type_morph = 'Off / Suburban'
    elif code == 8:
        type = 'Off'
        morph = 'Rural'
        type_morph = 'Off / Rural'
    elif code == 9:
        type = 'ROE'
        morph = 'Dense Urban'
        type_morph = 'ROE / Dense Urban'
    elif code == 10:
        type = 'ROE'
        morph = 'Urban'
        type_morph = 'ROE / Urban'
    elif code == 11:
        type = 'ROE'
        morph = 'Suburban'
        type_morph = 'ROE / Suburban'
    elif code == 12:
        type = 'ROE'
        morph = 'Rural'
        type_morph = 'ROE / Rural'
    elif code == 13:
        type = 'SMB'
        morph = 'Dense Urban'
        type_morph = 'SMB / Dense Urban'
    elif code == 14:
        type = 'SMB'
        morph = 'Urban'
        type_morph = 'SMB / Urban'
    elif code == 15:
        type = 'SMB'
        morph = 'Suburban'
        type_morph = 'SMB / Suburban'
    elif code == 16:
        type = 'SMB'
        morph = 'Rural'
        type_morph = 'SMB / Rural'
    else:
        print('error')
    return type_morph


pole_du = fin_arrays(1)
pole_u = fin_arrays(2)
pole_s = fin_arrays(3)
pole_r = fin_arrays(4)
off_du = fin_arrays(5)
off_u = fin_arrays(6)
off_s = fin_arrays(7)
off_r = fin_arrays(8)
roe_du = fin_arrays(9)
roe_u = fin_arrays(10)
roe_s = fin_arrays(11)
roe_r = fin_arrays(12)
smb_du = fin_arrays(13)
smb_u = fin_arrays(14)
smb_s = fin_arrays(15)
smb_r = fin_arrays(16)

# the following merges segments and prepares them for the final
# npv calculation
# the only new feature here is it counts each bin that a site
# has ownership and drops it if the count is not high enough
# then reassigns those bins to sites after the drop

# seg1 = pd.read_csv('wtg_271_30_seg1.csv', delimiter=',')
# seg4 = pd.read_csv('wtg_271_30_seg4.csv', delimiter=',')
# all_segs_init = seg1.append(seg4, sort=True)
all_segs_init = pd.read_csv('wtg_17_15.csv', delimiter=',')
all_segs_init = all_segs_init.drop(['Unnamed: 0', 'npv', 'build_yr', 'design_build_yr'], axis=1)
all_segs = all_segs_init

all_segs['rx_signal_strength_db'], all_segs['sinr'], all_segs['rx_signal_strength_mw'] = \
    rx_calc(all_segs['path_loss_umi_db'])
all_segs.loc[all_segs['sinr'] > 50, 'sinr'] = 50.0

sinr_bins_unique = all_segs.drop_duplicates(subset='GridName', keep=False).copy()
sinr_bins_dups = all_segs[all_segs.duplicated(['GridName'], keep=False)].copy()
sinr_bins_dups['sum_rx_signal'] = sinr_bins_dups.groupby('GridName')['rx_signal_strength_mw'].transform(sum)
all_segs = sinr_bins_unique.append(sinr_bins_dups)
sinr_bins_a = all_segs[all_segs['sum_rx_signal'].notnull()].copy().reset_index(drop=True)

sinr_bins_a['sinr_new'] = sinr_new2(sinr_bins_a['sum_rx_signal'], sinr_bins_a['rx_signal_strength_db'])

sinr_bins_b = all_segs[all_segs['sum_rx_signal'].isnull()].copy()
sinr_bins_b['sinr_new'] = sinr_bins_b['sum_rx_signal'].where(sinr_bins_b['sum_rx_signal'].notnull(),
                                                             sinr_bins_b['sinr'], axis=0)
all_segs = sinr_bins_a.append(sinr_bins_b)

# the previous section determines the owner of a bin, but if the sinr is below -2,
# it is dropped

all_segs = all_segs[all_segs.sinr_new >= -2.0]
all_segs['gb_offload'] = all_segs.groupby('fict_site')['Hour_GBs'].transform(sum)
all_segs = all_segs.drop(['path_loss_umi_db', 'rx_signal_strength_db', 'rx_signal_strength_mw', 'sinr',
                          'sum_rx_signal', 'gb_offload'], axis=1)
all_segs['grid_temp'] = all_segs['GridName'].str.replace(r'\D', '')
all_segs['grid_temp'] = all_segs['grid_temp'].str[-8:]
all_segs = all_segs.sort_values(['grid_temp', 'sinr_new', 'opt_build_year'])

all_segs_unique = all_segs.drop_duplicates(subset='grid_temp', keep=False).copy()
all_segs_dups = all_segs[all_segs.duplicated(['grid_temp'], keep=False)].copy()
if len(all_segs_dups) > 0:
    print('duplicates at end')
    all_segs_dups = all_segs_dups.groupby('grid_temp').last().reset_index()
    all_segs = all_segs_unique.append(all_segs_dups)

all_segs = pd.merge(all_segs, lte_params, left_on='sinr_new', right_on='SINR')
all_segs['rb_thru_put'] = rb_thru_put(all_segs['Code Rate'], all_segs['symbols/SF'], all_segs['2x2 MIMO Gain'],
                                      all_segs['subframe allocation'], all_segs['retrans'],
                                      all_segs['high  layer overhead'],
                                      all_segs['overhead TP kbps'])
all_segs['gb_offload'] = all_segs.groupby('fict_site')['Hour_GBs'].transform(sum)
test = all_segs[['GridName', 'fict_site']]

fict_site_count = test['fict_site'].value_counts().reset_index()
fict_site_count = fict_site_count.rename(columns={'index': 'fict_site', 'fict_site': 'fict_site_count'})
all_segs = pd.merge(all_segs, fict_site_count, on='fict_site')

fict_site_count = fict_site_count.loc[fict_site_count['fict_site_count'] > 61]

all_segs = all_segs.sort_values(by=['fict_site'], ascending=True)
mean_bins = all_segs.mean()
std_bins = all_segs.std()

# RESET BINS FOR SITES THAT HAVE BEEN DROPPED

all_segs = pd.merge(fict_site_count, all_segs_init, on='fict_site')

all_segs['rx_signal_strength_db'], all_segs['sinr'], all_segs['rx_signal_strength_mw'] = \
    rx_calc(all_segs['path_loss_umi_db'])
all_segs.loc[all_segs['sinr'] > 50, 'sinr'] = 50.0

sinr_bins_unique = all_segs.drop_duplicates(subset='GridName', keep=False).copy()
sinr_bins_dups = all_segs[all_segs.duplicated(['GridName'], keep=False)].copy()
sinr_bins_dups['sum_rx_signal'] = sinr_bins_dups.groupby('GridName')['rx_signal_strength_mw'].transform(sum)
all_segs = sinr_bins_unique.append(sinr_bins_dups)
sinr_bins_a = all_segs[all_segs['sum_rx_signal'].notnull()].copy().reset_index(drop=True)

sinr_bins_a['sinr_new'] = sinr_new2(sinr_bins_a['sum_rx_signal'], sinr_bins_a['rx_signal_strength_db'])

sinr_bins_b = all_segs[all_segs['sum_rx_signal'].isnull()].copy()
sinr_bins_b['sinr_new'] = sinr_bins_b['sum_rx_signal'].where(sinr_bins_b['sum_rx_signal'].notnull(),
                                                             sinr_bins_b['sinr'], axis=0)
all_segs = sinr_bins_a.append(sinr_bins_b)
all_segs = all_segs[all_segs.sinr_new >= -2.0]
all_segs['gb_offload'] = all_segs.groupby('fict_site')['Hour_GBs'].transform(sum)
all_segs = all_segs.drop(['path_loss_umi_db',
                          'rx_signal_strength_db', 'rx_signal_strength_mw', 'sinr',
                          'sum_rx_signal', 'gb_offload'], axis=1)
all_segs['grid_temp'] = all_segs['GridName'].str.replace(r'\D', '')
all_segs['grid_temp'] = all_segs['grid_temp'].str[-8:]
all_segs = all_segs.sort_values(['grid_temp', 'sinr_new', 'opt_build_year'])

all_segs_unique = all_segs.drop_duplicates(subset='grid_temp', keep=False).copy()
all_segs_dups = all_segs[all_segs.duplicated(['grid_temp'], keep=False)].copy()
if len(all_segs_dups) > 0:
    print('duplicates at end')
    all_segs_dups = all_segs_dups.groupby('grid_temp').last().reset_index()
    all_segs = all_segs_unique.append(all_segs_dups)

all_segs = pd.merge(all_segs, lte_params, left_on='sinr_new', right_on='SINR')
all_segs['rb_thru_put'] = rb_thru_put(all_segs['Code Rate'], all_segs['symbols/SF'], all_segs['2x2 MIMO Gain'],
                                      all_segs['subframe allocation'], all_segs['retrans'],
                                      all_segs['high  layer overhead'],
                                      all_segs['overhead TP kbps'])
all_segs['gb_offload'] = all_segs.groupby('fict_site')['Hour_GBs'].transform(sum)
test = all_segs[['GridName', 'fict_site']]

fict_site_count_2 = test['fict_site'].value_counts().reset_index()
fict_site_count_2 = fict_site_count_2.rename(columns={'index': 'fict_site', 'fict_site': 'fict_site_count_2'})
fict_site_check = pd.merge(fict_site_count, fict_site_count_2, on='fict_site')
fict_site_check['diff'] = fict_site_check['fict_site_count'] - fict_site_check['fict_site_count_2']

all_segs = pd.merge(all_segs, fict_site_count_2, on='fict_site')

all_segs = all_segs.sort_values(by=['fict_site'], ascending=True)

all_segs = pd.merge(all_segs, bin_req, on='GridName')
all_segs['bh_req_rbs'] = all_segs['bin_req_hr_mbps'] / all_segs['rb_thru_put']
all_segs = all_segs[['fict_site', 'morph_code', 'gb_offload', 'bh_req_rbs', 'opt_build_year']]
all_segs = all_segs.groupby('fict_site', as_index=False).agg(
    {'bh_req_rbs': sum, 'morph_code': 'mean', 'gb_offload': 'mean', 'opt_build_year': 'mean'})
all_segs['enb_util'] = np.ceil(all_segs['bh_req_rbs']) / 400
all_segs['max_cap'] = (all_segs['gb_offload'] / all_segs['enb_util'])
all_segs = pd.merge(all_segs, fict_site_count, on='fict_site')

# separate files into the optimal build year for npv calculations

npv2021 = all_segs[all_segs['opt_build_year'] == 1].copy().reset_index()
npv2022 = all_segs[all_segs['opt_build_year'] == 2].copy().reset_index()
npv2023 = all_segs[all_segs['opt_build_year'] == 3].copy().reset_index()
npv2024 = all_segs[all_segs['opt_build_year'] == 4].copy().reset_index()
npv2025 = all_segs[all_segs['opt_build_year'] == 5].copy().reset_index()
npv2026 = all_segs[all_segs['opt_build_year'] == 6].copy().reset_index()
npv2027 = all_segs[all_segs['opt_build_year'] == 7].copy().reset_index()
npv2028 = all_segs[all_segs['opt_build_year'] == 8].copy().reset_index()
npv2029 = all_segs[all_segs['opt_build_year'] == 9].copy().reset_index()
npv2030 = all_segs[all_segs['opt_build_year'] == 10].copy().reset_index()

# the npv calculations include a function to determine leftover offload
# that may be sellable

if len(npv2021) > 0:
    npv2021['npv'] = npv2021.apply(lambda x: npv21(x['gb_offload'], x['morph_code'], x['max_cap']),
                                   axis=1).astype(int)
    npv2021['split_yr'] = npv2021.apply(lambda x: split21(x['gb_offload'], x['max_cap'], x['morph_code']), axis=1)
    npv2021['debit'] = npv2021.apply(lambda x: capex_21(x['gb_offload'], x['max_cap'], x['morph_code']), axis=1) + \
                       npv2021.apply(lambda x: opex_21(x['gb_offload'], x['max_cap'], x['morph_code']), axis=1)
    npv2021['npv'] = npv2021['npv'] - npv2021['debit']
    extra_capacity_21 = npv2021.apply(lambda x: extra_offload21(x['gb_offload'], x['morph_code'], x['max_cap']), axis=1).values.tolist()
    temp_21 = np.hstack(extra_capacity_21).T
    npv2021 = pd.concat([npv2021, temp_21], axis=1)

if len(npv2022) > 0:
    npv2022['npv'] = npv2022.apply(lambda x: npv22(x['gb_offload'], x['morph_code'], x['max_cap']),
                                   axis=1).astype(int)
    npv2022['split_yr'] = npv2022.apply(lambda x: split22(x['gb_offload'], x['max_cap'], x['morph_code']), axis=1)
    npv2022['debit'] = npv2022.apply(lambda x: capex_22(x['gb_offload'], x['max_cap'], x['morph_code']), axis=1) + \
                       npv2022.apply(lambda x: opex_22(x['gb_offload'], x['max_cap'], x['morph_code']), axis=1)
    npv2022['npv'] = npv2022['npv'] - npv2022['debit']
    extra_capacity_22 = npv2022.apply(lambda x: extra_offload22(x['gb_offload'], x['morph_code'], x['max_cap']), axis=1).values.tolist()
    temp_22 = np.hstack(extra_capacity_22).T
    np_temp_22 = np.zeros([len(npv2022), 1])
    temp_22 = pd.DataFrame(np.concatenate((np_temp_22, temp_22), axis=1))
    npv2022 = pd.concat([npv2022, temp_22], axis=1)

if len(npv2023) > 0:
    npv2023['npv'] = npv2023.apply(lambda x: npv23(x['gb_offload'], x['morph_code'], x['max_cap']),
                                   axis=1).astype(int)
    npv2023['split_yr'] = npv2023.apply(lambda x: split23(x['gb_offload'], x['max_cap'], x['morph_code']), axis=1)
    npv2023['debit'] = npv2023.apply(lambda x: capex_23(x['gb_offload'], x['max_cap'], x['morph_code']), axis=1) + \
                       npv2023.apply(lambda x: opex_23(x['gb_offload'], x['max_cap'], x['morph_code']), axis=1)
    npv2023['npv'] = npv2023['npv'] - npv2023['debit']
    extra_capacity_23 = npv2023.apply(lambda x: extra_offload23(x['gb_offload'], x['morph_code'], x['max_cap']), axis=1).values.tolist()
    temp_23 = np.hstack(extra_capacity_23).T
    np_temp_23 = np.zeros([len(npv2023), 2])
    temp_23 = pd.DataFrame(np.concatenate((np_temp_23, temp_23), axis=1))
    npv2023 = pd.concat([npv2023, temp_23], axis=1)

if len(npv2024) > 0:
    npv2024['npv'] = npv2024.apply(lambda x: npv24(x['gb_offload'], x['morph_code'], x['max_cap']),
                                   axis=1).astype(int)
    npv2024['split_yr'] = npv2024.apply(lambda x: split24(x['gb_offload'], x['max_cap'], x['morph_code']), axis=1)
    npv2024['debit'] = npv2024.apply(lambda x: capex_24(x['gb_offload'], x['max_cap'], x['morph_code']), axis=1) + \
                       npv2024.apply(lambda x: opex_24(x['gb_offload'], x['max_cap'], x['morph_code']), axis=1)
    npv2024['npv'] = npv2024['npv'] - npv2024['debit']
    extra_capacity_24 = npv2024.apply(lambda x: extra_offload24(x['gb_offload'], x['morph_code'], x['max_cap']), axis=1).values.tolist()
    temp_24 = np.hstack(extra_capacity_24).T
    np_temp_24 = np.zeros([len(npv2024), 3])
    temp_24 = pd.DataFrame(np.concatenate((np_temp_24, temp_24), axis=1))
    npv2024 = pd.concat([npv2024, temp_24], axis=1)

if len(npv2025) > 0:
    npv2025['npv'] = npv2025.apply(lambda x: npv25(x['gb_offload'], x['morph_code'], x['max_cap']),
                                   axis=1).astype(int)
    npv2025['split_yr'] = npv2025.apply(lambda x: split25(x['gb_offload'], x['max_cap'], x['morph_code']), axis=1)
    npv2025['debit'] = npv2025.apply(lambda x: capex_25(x['gb_offload'], x['max_cap'], x['morph_code']), axis=1) + \
                       npv2025.apply(lambda x: opex_25(x['gb_offload'], x['max_cap'], x['morph_code']), axis=1)
    npv2025['npv'] = npv2025['npv'] - npv2025['debit']
    extra_capacity_25 = npv2025.apply(lambda x: extra_offload25(x['gb_offload'], x['morph_code'], x['max_cap']), axis=1).values.tolist()
    temp_25 = np.hstack(extra_capacity_25).T
    np_temp_25 = np.zeros([len(npv2025), 4])
    temp_25 = pd.DataFrame(np.concatenate((np_temp_25, temp_25), axis=1))
    npv2025 = pd.concat([npv2025, temp_25], axis=1)

if len(npv2026) > 0:
    npv2026['npv'] = npv2026.apply(lambda x: npv26(x['gb_offload'], x['morph_code'], x['max_cap']),
                                   axis=1).astype(int)
    npv2026['split_yr'] = npv2026.apply(lambda x: split26(x['gb_offload'], x['max_cap'], x['morph_code']), axis=1)
    npv2026['debit'] = npv2026.apply(lambda x: capex_26(x['gb_offload'], x['max_cap'], x['morph_code']), axis=1) + \
                       npv2026.apply(lambda x: opex_26(x['gb_offload'], x['max_cap'], x['morph_code']), axis=1)
    npv2026['npv'] = npv2026['npv'] - npv2026['debit']
    extra_capacity_26 = npv2026.apply(lambda x: extra_offload26(x['gb_offload'], x['morph_code'], x['max_cap']), axis=1).values.tolist()
    temp_26 = np.hstack(extra_capacity_26).T
    np_temp_26 = np.zeros([len(npv2026), 5])
    temp_26 = pd.DataFrame(np.concatenate((np_temp_26, temp_26), axis=1))
    npv2026 = pd.concat([npv2026, temp_26], axis=1)

if len(npv2027) > 0:
    npv2027['npv'] = npv2027.apply(lambda x: npv27(x['gb_offload'], x['morph_code'], x['max_cap']),
                                   axis=1).astype(int)
    npv2027['split_yr'] = npv2027.apply(lambda x: split27(x['gb_offload'], x['max_cap'], x['morph_code']), axis=1)
    npv2027['debit'] = npv2027.apply(lambda x: capex_27(x['gb_offload'], x['max_cap'], x['morph_code']), axis=1) + \
                       npv2027.apply(lambda x: opex_27(x['gb_offload'], x['max_cap'], x['morph_code']), axis=1)
    npv2027['npv'] = npv2027['npv'] - npv2027['debit']
    extra_capacity_27 = npv2027.apply(lambda x: extra_offload27(x['gb_offload'], x['morph_code'], x['max_cap']), axis=1).values.tolist()
    temp_27 = np.hstack(extra_capacity_27).T
    np_temp_27 = np.zeros([len(npv2027), 6])
    temp_27 = pd.DataFrame(np.concatenate((np_temp_27, temp_27), axis=1))
    npv2027 = pd.concat([npv2027, temp_27], axis=1)

if len(npv2028) > 0:
    npv2028['npv'] = npv2028.apply(lambda x: npv28(x['gb_offload'], x['morph_code'], x['max_cap']),
                                   axis=1).astype(int)
    npv2028['split_yr'] = npv2028.apply(lambda x: split28(x['gb_offload'], x['max_cap'], x['morph_code']), axis=1)
    npv2028['debit'] = npv2028.apply(lambda x: capex_28(x['gb_offload'], x['max_cap'], x['morph_code']), axis=1) + \
                       npv2028.apply(lambda x: opex_28(x['gb_offload'], x['max_cap'], x['morph_code']), axis=1)
    npv2028['npv'] = npv2028['npv'] - npv2028['debit']
    extra_capacity_28 = npv2028.apply(lambda x: extra_offload28(x['gb_offload'], x['morph_code'], x['max_cap']), axis=1).values.tolist()
    temp_28 = np.hstack(extra_capacity_28).T
    np_temp_28 = np.zeros([len(npv2028), 7])
    temp_28 = pd.DataFrame(np.concatenate((np_temp_28, temp_28), axis=1))
    npv2028 = pd.concat([npv2028, temp_28], axis=1)

if len(npv2029) > 0:
    npv2029['npv'] = npv2029.apply(lambda x: npv29(x['gb_offload'], x['morph_code'], x['max_cap']),
                                   axis=1).astype(int)
    npv2029['split_yr'] = npv2029.apply(lambda x: split29(x['gb_offload'], x['max_cap'], x['morph_code']), axis=1)
    npv2029['debit'] = npv2029.apply(lambda x: capex_29(x['gb_offload'], x['max_cap'], x['morph_code']), axis=1) + \
                       npv2029.apply(lambda x: opex_29(x['gb_offload'], x['max_cap'], x['morph_code']), axis=1)
    npv2029['npv'] = npv2029['npv'] - npv2029['debit']
    extra_capacity_29 = npv2029.apply(lambda x: extra_offload29(x['gb_offload'], x['morph_code'], x['max_cap']), axis=1).values.tolist()
    temp_29 = np.hstack(extra_capacity_29).T
    np_temp_29 = np.zeros([len(npv2029), 8])
    temp_29 = pd.DataFrame(np.concatenate((np_temp_29, temp_29), axis=1))
    npv2029 = pd.concat([npv2029, temp_29], axis=1)

if len(npv2030) > 0:
    npv2030['npv'] = npv2030.apply(lambda x: npv30(x['gb_offload'], x['morph_code'], x['max_cap']),
                                   axis=1).astype(int)
    npv2030['split_yr'] = npv2030.apply(lambda x: split30(x['gb_offload'], x['max_cap'], x['morph_code']), axis=1)
    npv2030['debit'] = npv2030.apply(lambda x: capex_30(x['gb_offload'], x['max_cap'], x['morph_code']), axis=1) + \
                       npv2030.apply(lambda x: opex_30(x['gb_offload'], x['max_cap'], x['morph_code']), axis=1)
    npv2030['npv'] = npv2030['npv'] - npv2030['debit']
    extra_capacity_30 = npv2030.apply(lambda x: extra_offload30(x['gb_offload'], x['morph_code'], x['max_cap']), axis=1).values.tolist()
    temp_30 = np.hstack(extra_capacity_30).T
    np_temp_30 = np.zeros([len(npv2030), 9])
    temp_30 = pd.DataFrame(np.concatenate((np_temp_30, temp_30), axis=1))
    npv2030 = pd.concat([npv2030, temp_30], axis=1)

final = pd.concat([npv2024, npv2025, npv2026, npv2027, npv2028, npv2029, npv2030, npv2021, npv2022,
                   npv2023], sort=True, ignore_index=True)
final = final.rename(columns={0: 'year_1_excess', 1: 'year_2_excess', 2: 'year_3_excess', 3: 'year_4_excess',
                              4: 'year_5_excess', 5: 'year_6_excess', 6: 'year_7_excess', 7: 'year_8_excess',
                              8: 'year_9_excess', 9: 'year_10_excess'})

final = final[['fict_site', 'npv', 'fict_site_count', 'opt_build_year', 'gb_offload', 'morph_code', 'debit',
               'year_1_excess', 'year_2_excess', 'year_3_excess', 'year_4_excess', 'year_5_excess', 'year_6_excess',
               'year_7_excess', 'year_8_excess', 'year_9_excess', 'year_10_excess']]
final = final.sort_values(by=['fict_site'], ascending=True)
final = final.loc[final['npv'] > 0]

# calculate quantiles for information

temp_final_npv = final[['npv']]
quant05 = temp_final_npv.quantile(.05).iloc[0]
quant10 = temp_final_npv.quantile(.1).iloc[0]
quant15 = temp_final_npv.quantile(.15).iloc[0]
quant20 = temp_final_npv.quantile(.2).iloc[0]
quant25 = temp_final_npv.quantile(.25).iloc[0]
quant30 = temp_final_npv.quantile(.3).iloc[0]
quant35 = temp_final_npv.quantile(.35).iloc[0]

print(final['npv'].sum())
print(len(final))

final_05 = final.loc[final['npv'] > quant05]
print('quant05', end=' ')
print(final_05['npv'].sum())
print(len(final_05))

final_10 = final.loc[final['npv'] > quant10]
print('quant10', end=' ')
print(final_10['npv'].sum())
print(len(final_10))

final_15 = final.loc[final['npv'] > quant15]
print('quant15', end=' ')
print(final_15['npv'].sum())
print(len(final_15))

final_20 = final.loc[final['npv'] > quant20]
print('quant20', end=' ')
print(final_20['npv'].sum())
print(len(final_20))

final_25 = final.loc[final['npv'] > quant25]
print('quant25', end=' ')
print(final_25['npv'].sum())
print(len(final_25))

final_30 = final.loc[final['npv'] > quant30]
print('quant30', end=' ')
print(final_30['npv'].sum())
print(len(final_30))

final_35 = final.loc[final['npv'] > quant35]
print('quant35', end=' ')
print(final_35['npv'].sum())
print(len(final_35))

final.to_csv('final.csv')