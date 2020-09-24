# new xnpv function


def xnpv(gbs, mo_cap, code):
    # slice 0 is cpx, 1 is opx, 2 is growth, 3 is mvno,
    array = morph_array(code)
    flag = 0
    a = 0
    for i in range(11):
        flag = 0
        a = 0
        if (gbs * (array[i][2]) * 12) < (cell_split * mo_cap * 12):
            if (gbs * (array[i][2]) * 12) < (mo_cap * 12):
                value[i] = gbs * 12 * array[i][3] * array[i][2] - array[i][1]
            else:
                value[i] = gbs * 12 * array[i][3] * array[i][2] - (2 * array[i][1])
                if flag == 0:
                    a = i
                    flag = 1
        else:
            value[i] = gbs * 12 * array[i][3] * array[i][2] - (2 * array[i][1])
    date_0 = st_date[0]
    value[a] = value[a] - array[a][0]
    return int(sum([value_i / ((1.0 + disc_rt) ** (((date_i - date_0).days - day_diff) / 12.0))
                    for value_i, date_i in zip(value, st_date)]))