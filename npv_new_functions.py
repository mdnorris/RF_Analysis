def morph(type, morph):
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

# create npv arrays
# slice 0 is opex, 1 is opx, 2 is growth, 3 is mvno, 4 is penet_rate
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
value = np.empty([11, 1])
