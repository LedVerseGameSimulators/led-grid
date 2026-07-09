# Source Generated with Decompyle++
# File: position_convert.pyc (Python 3.7)

'''
问题：
如果有一个灯时坏的，或者少连一个灯好像就会错乱。就是没有构成方形

'''

def left_top_right():
    rst_array = []
    src_array = []
    i_record = 0
    j_record = 0
    for x in range(len(rst_array)):
        len_array_x = len(rst_array[x])
        idx = 0
        for i in range(i_record, len(src_array)):
            if i % 2 == 0:
                for j in range(j_record, len(src_array[i])):
                    rst_array[x][idx] = src_array[i][j]
                    idx += 1
                    if idx == len_array_x:
                        j_record = j + 1
                        break
            for j in range(j_record, 0, -1):
                rst_array[x][idx] = src_array[i][j]
                idx += 1
                if idx == len_array_x:
                    j_record = j + 1
                    break
            if idx == len_array_x:
                i_record = i + 1
                break
    


def right_top_left():
    rst_array = []
    src_array = []
    i_record = 0
    j_record = len(src_array[0]) - 1
    for x in range(len(rst_array)):
        len_array_x = len(rst_array[x])
        idx = 0
        for i in range(i_record, len(src_array)):
            if i % 2 == 1:
                for j in range(j_record, len(src_array[i])):
                    rst_array[x][idx] = src_array[i][j]
                    idx += 1
                    if idx == len_array_x:
                        j_record = j + 1
                        break
            for j in range(j_record, 0, -1):
                rst_array[x][idx] = src_array[i][j]
                idx += 1
                if idx == len_array_x:
                    j_record = j - 1
                    break
            if idx == len_array_x:
                i_record = i + 1
                break
    


def left_top_down():
    rst_array = []
    src_array = []
    i_record = 0
    j_record = 0
    for x in range(len(rst_array)):
        len_array_x = len(rst_array[x])
        idx = 0
        for j in range(j_record, len(src_array[i])):
            if j % 2 == 0:
                for i in range(i_record, len(src_array)):
                    rst_array[x][idx] = src_array[i][j]
                    idx += 1
                    if idx == len_array_x:
                        i_record = i + 1
                        break
            for i in range(i_record, -1, -1):
                rst_array[x][idx] = src_array[i][j]
                idx += 1
                if idx == len_array_x:
                    i_record = i - 1
                    break
            if idx == len_array_x:
                j_record = j + 1
                break
    


def right_top_down():
    rst_array = []
    src_array = []
    i_record = 0
    j_record = len(src_array[0]) - 1
    for x in range(len(rst_array)):
        len_array_x = len(rst_array[x])
        idx = 0
        for j in range(j_record, -1, -1):
            if j % 2 == 0:
                for i in range(i_record, len(src_array)):
                    rst_array[x][idx] = src_array[i][j]
                    idx += 1
                    if idx == len_array_x:
                        i_record = i + 1
                        break
            for i in range(i_record, -1, -1):
                rst_array[x][idx] = src_array[i][j]
                idx += 1
                if idx == len_array_x:
                    i_record = i - 1
                    break
            if idx == len_array_x:
                j_record = j - 1
                break
    

LEFT_TOP_RIGHT = 0
LEFT_TOP_DOWN = 1
RIGHT_TOP_LEFT = 2
RIGHT_TOP_DOWN = 3
LEFT_DOWN_RIGHT = 4
LEFT_DOWN_UP = 5
RIGHT_DOWN_LEFT = 6
RIGHT_DOWN_UP = 7
INC = 1
DEC = -1
ROW = 0
COL = 1

def position_convert_2arr_to_1arr_old(type, src_array, rst_array = ([], [])):
    i_record = 0
    j_record = 0
    col_max = len(src_array[0]) - 1
    row_max = len(src_array) - 1
    i_min = 0
    j_min = 0
    row_min = 0
    col_min = 0
    i_inc_or_dec = DEC
    j0_inc_or_dec = INC
    j1_inc_or_dec = DEC
    if type == LEFT_TOP_RIGHT:
        i_record = i_min
        j_record = j_min
        i_inc_or_dec = DEC
        j0_inc_or_dec = INC
        j1_inc_or_dec = DEC
        j_first_variation0_end = col_max + 1
        j_first_variation1_end = -1
        first_variation = COL
    elif type == LEFT_TOP_DOWN:
        i_record = i_min
        j_record = j_min
        i_inc_or_dec = INC
        j0_inc_or_dec = INC
        j1_inc_or_dec = DEC
        j_first_variation0_end = row_max + 1
        j_first_variation1_end = -1
        first_variation = ROW
    elif type == RIGHT_TOP_LEFT:
        i_record = i_min
        j_record = col_max
        i_inc_or_dec = INC
        j0_inc_or_dec = DEC
        j1_inc_or_dec = INC
        j_first_variation0_end = -1
        j_first_variation1_end = col_max + 1
        first_variation = COL
    elif type == RIGHT_TOP_DOWN:
        i_record = col_max
        j_record = row_min
        i_inc_or_dec = DEC
        j0_inc_or_dec = INC
        j1_inc_or_dec = DEC
        j_first_variation0_end = row_max + 1
        j_first_variation1_end = -1
        first_variation = ROW
    elif type == LEFT_DOWN_RIGHT:
        i_record = row_max
        j_record = col_min
        i_inc_or_dec = DEC
        j0_inc_or_dec = INC
        j1_inc_or_dec = DEC
        j_first_variation0_end = col_max + 1
        j_first_variation1_end = -1
        first_variation = COL
    elif type == LEFT_DOWN_UP:
        i_record = col_min
        j_record = row_max
        i_inc_or_dec = INC
        j0_inc_or_dec = DEC
        j1_inc_or_dec = INC
        j_first_variation0_end = -1
        j_first_variation1_end = row_max + 1
        first_variation = ROW
    elif type == RIGHT_DOWN_LEFT:
        i_record = row_max
        j_record = col_max
        i_inc_or_dec = DEC
        j0_inc_or_dec = DEC
        j1_inc_or_dec = INC
        j_first_variation0_end = -1
        j_first_variation1_end = col_max + 1
        first_variation = COL
    elif type == RIGHT_DOWN_UP:
        i_record = col_max
        j_record = row_max
        i_inc_or_dec = DEC
        j0_inc_or_dec = DEC
        j1_inc_or_dec = INC
        j_first_variation0_end = -1
        j_first_variation1_end = row_max + 1
        first_variation = ROW
    if first_variation == COL:
        for x in range(len(rst_array)):
            len_array_x = len(rst_array[x])
            idx = 0
            for i in range(i_record, j_first_variation1_end, i_inc_or_dec):
                if i % 2 == 0:
                    for j in range(j_record, j_first_variation0_end, j0_inc_or_dec):
                        rst_array[x][idx] = src_array[i][j]
                        idx += 1
                        j_record = j
                        if idx == len_array_x:
                            j_record = j + j0_inc_or_dec
                            if j_record > col_max:
                                j_record = col_max
                                i_record = i + i_inc_or_dec
                            elif j_record < col_min:
                                j_record = col_min
                                i_record = i + i_inc_or_dec
                    
                else:
                    for j in range(j_record, j_first_variation1_end, j1_inc_or_dec):
                        rst_array[x][idx] = src_array[i][j]
                        idx += 1
                        j_record = j
                        if idx == len_array_x:
                            j_record = j + j1_inc_or_dec
                            if j_record > col_max:
                                j_record = col_max
                                i_record = i + i_inc_or_dec
                            elif j_record < col_min:
                                j_record = col_min
                                i_record = i + i_inc_or_dec
                    
                if idx == len_array_x:
                    break
        
    else:
        for x in range(len(rst_array)):
            len_array_x = len(rst_array[x])
            idx = 0
            for i in range(i_record, j_first_variation1_end, i_inc_or_dec):
                if i % 2 == 0:
                    for j in range(j_record, j_first_variation0_end, j0_inc_or_dec):
                        rst_array[x][idx] = src_array[j][i]
                        idx += 1
                        j_record = j
                        if idx == len_array_x:
                            j_record = j + j0_inc_or_dec
                            if j_record > row_max:
                                j_record = row_max
                                i_record = i + i_inc_or_dec
                            elif j_record < row_min:
                                j_record = row_min
                                i_record = i + i_inc_or_dec
                    
                else:
                    for j in range(j_record, j_first_variation1_end, j1_inc_or_dec):
                        rst_array[x][idx] = src_array[j][i]
                        idx += 1
                        j_record = j
                        if idx == len_array_x:
                            j_record = j + j1_inc_or_dec
                            if j_record > row_max:
                                j_record = row_max
                                i_record = i + i_inc_or_dec
                            elif j_record < row_min:
                                j_record = row_min
                                i_record = i + i_inc_or_dec
                    
                if idx == len_array_x:
                    break
        


def position_convert_1arr_to_2arr_old(type, rst_array, src_array = ([], [])):
    i_record = 0
    j_record = 0
    col_max = len(src_array[0]) - 1
    row_max = len(src_array) - 1
    i_min = 0
    j_min = 0
    row_min = 0
    col_min = 0
    i_inc_or_dec = DEC
    j0_inc_or_dec = INC
    j1_inc_or_dec = DEC
    if type == LEFT_TOP_RIGHT:
        i_record = i_min
        j_record = j_min
        i_inc_or_dec = DEC
        j0_inc_or_dec = INC
        j1_inc_or_dec = DEC
        j_first_variation0_end = col_max + 1
        j_first_variation1_end = -1
        first_variation = COL
    elif type == LEFT_TOP_DOWN:
        i_record = i_min
        j_record = j_min
        i_inc_or_dec = INC
        j0_inc_or_dec = INC
        j1_inc_or_dec = DEC
        j_first_variation0_end = row_max + 1
        j_first_variation1_end = -1
        first_variation = ROW
    elif type == RIGHT_TOP_LEFT:
        i_record = i_min
        j_record = col_max
        i_inc_or_dec = INC
        j0_inc_or_dec = DEC
        j1_inc_or_dec = INC
        j_first_variation0_end = -1
        j_first_variation1_end = col_max + 1
        first_variation = COL
    elif type == RIGHT_TOP_DOWN:
        i_record = col_max
        j_record = row_min
        i_inc_or_dec = DEC
        j0_inc_or_dec = INC
        j1_inc_or_dec = DEC
        j_first_variation0_end = row_max + 1
        j_first_variation1_end = -1
        first_variation = ROW
    elif type == LEFT_DOWN_RIGHT:
        i_record = row_max
        j_record = col_min
        i_inc_or_dec = DEC
        j0_inc_or_dec = INC
        j1_inc_or_dec = DEC
        j_first_variation0_end = col_max + 1
        j_first_variation1_end = -1
        first_variation = COL
    elif type == LEFT_DOWN_UP:
        i_record = col_min
        j_record = row_max
        i_inc_or_dec = INC
        j0_inc_or_dec = DEC
        j1_inc_or_dec = INC
        j_first_variation0_end = -1
        j_first_variation1_end = row_max + 1
        first_variation = ROW
    elif type == RIGHT_DOWN_LEFT:
        i_record = row_max
        j_record = col_max
        i_inc_or_dec = DEC
        j0_inc_or_dec = DEC
        j1_inc_or_dec = INC
        j_first_variation0_end = -1
        j_first_variation1_end = col_max + 1
        first_variation = COL
    elif type == RIGHT_DOWN_UP:
        i_record = col_max
        j_record = row_max
        i_inc_or_dec = DEC
        j0_inc_or_dec = DEC
        j1_inc_or_dec = INC
        j_first_variation0_end = -1
        j_first_variation1_end = row_max + 1
        first_variation = ROW
    if first_variation == COL:
        for x in range(len(rst_array)):
            len_array_x = len(rst_array[x])
            idx = 0
            for i in range(i_record, j_first_variation1_end, i_inc_or_dec):
                if i % 2 == 0:
                    for j in range(j_record, j_first_variation0_end, j0_inc_or_dec):
                        src_array[i][j] = rst_array[x][idx]
                        idx += 1
                        j_record = j
                        if idx == len_array_x:
                            j_record = j + j0_inc_or_dec
                            if j_record > col_max:
                                j_record = col_max
                                i_record = i + i_inc_or_dec
                            elif j_record < col_min:
                                j_record = col_min
                                i_record = i + i_inc_or_dec
                    
                else:
                    for j in range(j_record, j_first_variation1_end, j1_inc_or_dec):
                        src_array[i][j] = rst_array[x][idx]
                        idx += 1
                        j_record = j
                        if idx == len_array_x:
                            j_record = j + j1_inc_or_dec
                            if j_record > col_max:
                                j_record = col_max
                                i_record = i + i_inc_or_dec
                            elif j_record < col_min:
                                j_record = col_min
                                i_record = i + i_inc_or_dec
                    
                if idx == len_array_x:
                    break
        
    else:
        for x in range(len(rst_array)):
            len_array_x = len(rst_array[x])
            idx = 0
            for i in range(i_record, j_first_variation1_end, i_inc_or_dec):
                if i % 2 == 0:
                    for j in range(j_record, j_first_variation0_end, j0_inc_or_dec):
                        src_array[j][i] = rst_array[x][idx]
                        idx += 1
                        j_record = j
                        if idx == len_array_x:
                            j_record = j + j0_inc_or_dec
                            if j_record > row_max:
                                j_record = row_max
                                i_record = i + i_inc_or_dec
                            elif j_record < row_min:
                                j_record = row_min
                                i_record = i + i_inc_or_dec
                    
                else:
                    for j in range(j_record, j_first_variation1_end, j1_inc_or_dec):
                        src_array[j][i] = rst_array[x][idx]
                        idx += 1
                        j_record = j
                        if idx == len_array_x:
                            j_record = j + j1_inc_or_dec
                            if j_record > row_max:
                                j_record = row_max
                                i_record = i + i_inc_or_dec
                            elif j_record < row_min:
                                j_record = row_min
                                i_record = i + i_inc_or_dec
                    
                if idx == len_array_x:
                    break
        


def position_convert_2arr_to_1arr(type, src_array, rst_array = ([], [])):
    i_record = 0
    j_record = 0
    col_max = len(src_array[0])
    row_max = len(src_array)
    i_min = 0
    j_min = 0
    row_min = 0
    col_min = 0
    i_inc_or_dec = DEC
    j0_inc_or_dec = INC
    j1_inc_or_dec = DEC
    if type == LEFT_TOP_RIGHT:
        i_record = i_min
        j_record = j_min
        i_inc_or_dec = INC
        j0_inc_or_dec = INC
        j1_inc_or_dec = DEC
        j_first_variation0_end = col_max + 1
        j_first_variation1_end = -1
        first_variation = COL
        i_start = 0
        i_end = row_max
        j0_start = 0
        j0_end = col_max
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    elif type == LEFT_TOP_DOWN:
        i_record = i_min
        j_record = j_min
        i_inc_or_dec = INC
        j0_inc_or_dec = INC
        j1_inc_or_dec = DEC
        j_first_variation0_end = row_max + 1
        j_first_variation1_end = -1
        first_variation = ROW
        i_start = 0
        i_end = col_max
        j0_start = 0
        j0_end = row_max
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    elif type == RIGHT_TOP_LEFT:
        i_record = i_min
        j_record = col_max
        i_inc_or_dec = INC
        j0_inc_or_dec = DEC
        j1_inc_or_dec = INC
        j_first_variation0_end = -1
        j_first_variation1_end = col_max + 1
        first_variation = COL
        i_start = 0
        i_end = row_max
        j0_start = col_max - 1
        j0_end = -1
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    elif type == RIGHT_TOP_DOWN:
        i_record = col_max
        j_record = row_min
        i_inc_or_dec = DEC
        j0_inc_or_dec = INC
        j1_inc_or_dec = DEC
        j_first_variation0_end = row_max + 1
        j_first_variation1_end = -1
        first_variation = ROW
        i_start = col_max - 1
        i_end = -1
        j0_start = 0
        j0_end = row_max
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    elif type == LEFT_DOWN_RIGHT:
        i_record = row_max
        j_record = col_min
        i_inc_or_dec = DEC
        j0_inc_or_dec = INC
        j1_inc_or_dec = DEC
        j_first_variation0_end = col_max + 1
        j_first_variation1_end = -1
        first_variation = COL
        i_start = row_max - 1
        i_end = -1
        j0_start = 0
        j0_end = col_max
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    elif type == LEFT_DOWN_UP:
        i_record = col_min
        j_record = row_max
        i_inc_or_dec = INC
        j0_inc_or_dec = DEC
        j1_inc_or_dec = INC
        j_first_variation0_end = -1
        j_first_variation1_end = row_max + 1
        first_variation = ROW
        i_start = 0
        i_end = col_max
        j0_start = row_max - 1
        j0_end = -1
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    elif type == RIGHT_DOWN_LEFT:
        i_record = row_max
        j_record = col_max
        i_inc_or_dec = DEC
        j0_inc_or_dec = DEC
        j1_inc_or_dec = INC
        j_first_variation0_end = -1
        j_first_variation1_end = col_max + 1
        first_variation = COL
        i_start = row_max - 1
        i_end = -1
        j0_start = col_max - 1
        j0_end = -1
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    elif type == RIGHT_DOWN_UP:
        i_record = col_max
        j_record = row_max
        i_inc_or_dec = DEC
        j0_inc_or_dec = DEC
        j1_inc_or_dec = INC
        j_first_variation0_end = -1
        j_first_variation1_end = row_max + 1
        first_variation = ROW
        i_start = col_max - 1
        i_end = -1
        j0_start = row_max - 1
        j0_end = -1
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    else:
        i_record = i_min
        j_record = j_min
        i_inc_or_dec = INC
        j0_inc_or_dec = INC
        j1_inc_or_dec = DEC
        j_first_variation0_end = col_max + 1
        j_first_variation1_end = -1
        first_variation = COL
        i_start = 0
        i_end = row_max
        j0_start = 0
        j0_end = col_max
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    if first_variation == COL:
        idx = 0
        alternate = False
        for i in range(i_start, i_end, i_inc_or_dec):
            alternate = not alternate
            if alternate:
                for j in range(j0_start, j0_end, j0_inc_or_dec):
                    rst_array[idx] = src_array[i][j]
                    idx += 1
                
            else:
                for j in range(j1_start, j1_end, j1_inc_or_dec):
                    rst_array[idx] = src_array[i][j]
                    idx += 1
                
        
    else:
        idx = 0
        alternate = False
        for i in range(i_start, i_end, i_inc_or_dec):
            alternate = not alternate
            if alternate:
                for j in range(j0_start, j0_end, j0_inc_or_dec):
                    rst_array[idx] = src_array[j][i]
                    idx += 1
                
            else:
                for j in range(j1_start, j1_end, j1_inc_or_dec):
                    rst_array[idx] = src_array[j][i]
                    idx += 1
                
        


def position_convert_1arr_to_2arr(type, rst_array, src_array = ([], [])):
    i_record = 0
    j_record = 0
    col_max = len(src_array[0])
    row_max = len(src_array)
    i_min = 0
    j_min = 0
    row_min = 0
    col_min = 0
    i_inc_or_dec = DEC
    j0_inc_or_dec = INC
    j1_inc_or_dec = DEC
    if type == LEFT_TOP_RIGHT:
        i_record = i_min
        j_record = j_min
        i_inc_or_dec = INC
        j0_inc_or_dec = INC
        j1_inc_or_dec = DEC
        j_first_variation0_end = col_max + 1
        j_first_variation1_end = -1
        first_variation = COL
        i_start = 0
        i_end = row_max
        j0_start = 0
        j0_end = col_max
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    elif type == LEFT_TOP_DOWN:
        i_record = i_min
        j_record = j_min
        i_inc_or_dec = INC
        j0_inc_or_dec = INC
        j1_inc_or_dec = DEC
        j_first_variation0_end = row_max + 1
        j_first_variation1_end = -1
        first_variation = ROW
        i_start = 0
        i_end = col_max
        j0_start = 0
        j0_end = row_max
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    elif type == RIGHT_TOP_LEFT:
        i_record = i_min
        j_record = col_max
        i_inc_or_dec = INC
        j0_inc_or_dec = DEC
        j1_inc_or_dec = INC
        j_first_variation0_end = -1
        j_first_variation1_end = col_max + 1
        first_variation = COL
        i_start = 0
        i_end = row_max
        j0_start = col_max - 1
        j0_end = -1
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    elif type == RIGHT_TOP_DOWN:
        i_record = col_max
        j_record = row_min
        i_inc_or_dec = DEC
        j0_inc_or_dec = INC
        j1_inc_or_dec = DEC
        j_first_variation0_end = row_max + 1
        j_first_variation1_end = -1
        first_variation = ROW
        i_start = col_max - 1
        i_end = -1
        j0_start = 0
        j0_end = row_max
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    elif type == LEFT_DOWN_RIGHT:
        i_record = row_max
        j_record = col_min
        i_inc_or_dec = DEC
        j0_inc_or_dec = INC
        j1_inc_or_dec = DEC
        j_first_variation0_end = col_max + 1
        j_first_variation1_end = -1
        first_variation = COL
        i_start = row_max - 1
        i_end = -1
        j0_start = 0
        j0_end = col_max
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    elif type == LEFT_DOWN_UP:
        i_record = col_min
        j_record = row_max
        i_inc_or_dec = INC
        j0_inc_or_dec = DEC
        j1_inc_or_dec = INC
        j_first_variation0_end = -1
        j_first_variation1_end = row_max + 1
        first_variation = ROW
        i_start = 0
        i_end = col_max
        j0_start = row_max - 1
        j0_end = -1
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    elif type == RIGHT_DOWN_LEFT:
        i_record = row_max
        j_record = col_max
        i_inc_or_dec = DEC
        j0_inc_or_dec = DEC
        j1_inc_or_dec = INC
        j_first_variation0_end = -1
        j_first_variation1_end = col_max + 1
        first_variation = COL
        i_start = row_max - 1
        i_end = -1
        j0_start = col_max - 1
        j0_end = -1
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    elif type == RIGHT_DOWN_UP:
        i_record = col_max
        j_record = row_max
        i_inc_or_dec = DEC
        j0_inc_or_dec = DEC
        j1_inc_or_dec = INC
        j_first_variation0_end = -1
        j_first_variation1_end = row_max + 1
        first_variation = ROW
        i_start = col_max - 1
        i_end = -1
        j0_start = row_max - 1
        j0_end = -1
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    else:
        i_record = i_min
        j_record = j_min
        i_inc_or_dec = INC
        j0_inc_or_dec = INC
        j1_inc_or_dec = DEC
        j_first_variation0_end = col_max + 1
        j_first_variation1_end = -1
        first_variation = COL
        i_start = 0
        i_end = row_max
        j0_start = 0
        j0_end = col_max
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    if first_variation == COL:
        idx = 0
        alternate = False
        for i in range(i_start, i_end, i_inc_or_dec):
            alternate = not alternate
            if alternate:
                for j in range(j0_start, j0_end, j0_inc_or_dec):
                    src_array[i][j] = rst_array[idx]
                    idx += 1
                
            else:
                for j in range(j1_start, j1_end, j1_inc_or_dec):
                    src_array[i][j] = rst_array[idx]
                    idx += 1
                
        
    else:
        idx = 0
        alternate = False
        for i in range(i_start, i_end, i_inc_or_dec):
            alternate = not alternate
            if alternate:
                for j in range(j0_start, j0_end, j0_inc_or_dec):
                    src_array[j][i] = rst_array[idx]
                    idx += 1
                
            else:
                for j in range(j1_start, j1_end, j1_inc_or_dec):
                    src_array[j][i] = rst_array[idx]
                    idx += 1
                
        


def wall_light_logic2real(logic_arr, start, direct = (1, 'right')):
    real_arr = []
    size = len(logic_arr)
    if direct == 'right':
        for x in range(size):
            x += 1
            y = (x + (start - 1)) % size
            if y == 0:
                y = size
            real_arr.append(logic_arr[y - 1])
        
    if direct == 'left':
        for x in range(size):
            x += 1
            y = ((size - x - 1) + start) % size
            if y == 0:
                y = size
            real_arr.append(logic_arr[y - 1])
        
    return real_arr


def wall_light_real2logic(real_arr, start, direct = (1, 'right')):
    logic_arr = []
    size = len(real_arr)
    if direct == 'right':
        for y in range(size):
            y += 1
            x = ((y - start - 1) + size) % size
            if x == 0:
                x = size
            logic_arr.append(real_arr(x))
        
    if direct == 'left':
        for y in range(size):
            y += 1
            x = ((size - y - start) + 1) % size
            if x == 0:
                x = size
            logic_arr.append(real_arr(x))
        
    return logic_arr


def record_rect_position_in_order_by_layout(type, layout_row, layout_col, rect_position_arr):
    i_record = 0
    j_record = 0
    col_max = layout_col
    row_max = layout_row
    i_min = 0
    j_min = 0
    row_min = 0
    col_min = 0
    i_inc_or_dec = DEC
    j0_inc_or_dec = INC
    j1_inc_or_dec = DEC
    if type == LEFT_TOP_RIGHT:
        i_record = i_min
        j_record = j_min
        i_inc_or_dec = INC
        j0_inc_or_dec = INC
        j1_inc_or_dec = DEC
        j_first_variation0_end = col_max + 1
        j_first_variation1_end = -1
        first_variation = COL
        i_start = 0
        i_end = row_max
        j0_start = 0
        j0_end = col_max
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    elif type == LEFT_TOP_DOWN:
        i_record = i_min
        j_record = j_min
        i_inc_or_dec = INC
        j0_inc_or_dec = INC
        j1_inc_or_dec = DEC
        j_first_variation0_end = row_max + 1
        j_first_variation1_end = -1
        first_variation = ROW
        i_start = 0
        i_end = col_max
        j0_start = 0
        j0_end = row_max
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    elif type == RIGHT_TOP_LEFT:
        i_record = i_min
        j_record = col_max
        i_inc_or_dec = INC
        j0_inc_or_dec = DEC
        j1_inc_or_dec = INC
        j_first_variation0_end = -1
        j_first_variation1_end = col_max + 1
        first_variation = COL
        i_start = 0
        i_end = row_max
        j0_start = col_max - 1
        j0_end = -1
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    elif type == RIGHT_TOP_DOWN:
        i_record = col_max
        j_record = row_min
        i_inc_or_dec = DEC
        j0_inc_or_dec = INC
        j1_inc_or_dec = DEC
        j_first_variation0_end = row_max + 1
        j_first_variation1_end = -1
        first_variation = ROW
        i_start = col_max - 1
        i_end = -1
        j0_start = 0
        j0_end = row_max
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    elif type == LEFT_DOWN_RIGHT:
        i_record = row_max
        j_record = col_min
        i_inc_or_dec = DEC
        j0_inc_or_dec = INC
        j1_inc_or_dec = DEC
        j_first_variation0_end = col_max + 1
        j_first_variation1_end = -1
        first_variation = COL
        i_start = row_max - 1
        i_end = -1
        j0_start = 0
        j0_end = col_max
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    elif type == LEFT_DOWN_UP:
        i_record = col_min
        j_record = row_max
        i_inc_or_dec = INC
        j0_inc_or_dec = DEC
        j1_inc_or_dec = INC
        j_first_variation0_end = -1
        j_first_variation1_end = row_max + 1
        first_variation = ROW
        i_start = 0
        i_end = col_max
        j0_start = row_max - 1
        j0_end = -1
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    elif type == RIGHT_DOWN_LEFT:
        i_record = row_max
        j_record = col_max
        i_inc_or_dec = DEC
        j0_inc_or_dec = DEC
        j1_inc_or_dec = INC
        j_first_variation0_end = -1
        j_first_variation1_end = col_max + 1
        first_variation = COL
        i_start = row_max - 1
        i_end = -1
        j0_start = col_max - 1
        j0_end = -1
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    elif type == RIGHT_DOWN_UP:
        i_record = col_max
        j_record = row_max
        i_inc_or_dec = DEC
        j0_inc_or_dec = DEC
        j1_inc_or_dec = INC
        j_first_variation0_end = -1
        j_first_variation1_end = row_max + 1
        first_variation = ROW
        i_start = col_max - 1
        i_end = -1
        j0_start = row_max - 1
        j0_end = -1
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    else:
        i_record = i_min
        j_record = j_min
        i_inc_or_dec = INC
        j0_inc_or_dec = INC
        j1_inc_or_dec = DEC
        j_first_variation0_end = col_max + 1
        j_first_variation1_end = -1
        first_variation = COL
        i_start = 0
        i_end = row_max
        j0_start = 0
        j0_end = col_max
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    if first_variation == COL:
        idx = 0
        alternate = False
        for i in range(i_start, i_end, i_inc_or_dec):
            alternate = not alternate
            if alternate:
                for j in range(j0_start, j0_end, j0_inc_or_dec):
                    rect_position_arr[idx] = (i, j)
                    idx += 1
                
            else:
                for j in range(j1_start, j1_end, j1_inc_or_dec):
                    rect_position_arr[idx] = (i, j)
                    idx += 1
                
        
    else:
        idx = 0
        alternate = False
        for i in range(i_start, i_end, i_inc_or_dec):
            alternate = not alternate
            if alternate:
                for j in range(j0_start, j0_end, j0_inc_or_dec):
                    rect_position_arr[idx] = (j, i)
                    idx += 1
                
            else:
                for j in range(j1_start, j1_end, j1_inc_or_dec):
                    rect_position_arr[idx] = (j, i)
                    idx += 1
                
        


def record_led_arr_position_to_rect(type, src_array = ([],)):
    i_record = 0
    j_record = 0
    col_max = len(src_array[0])
    row_max = len(src_array)
    i_min = 0
    j_min = 0
    row_min = 0
    col_min = 0
    i_inc_or_dec = DEC
    j0_inc_or_dec = INC
    j1_inc_or_dec = DEC
    if type == LEFT_TOP_RIGHT:
        i_record = i_min
        j_record = j_min
        i_inc_or_dec = INC
        j0_inc_or_dec = INC
        j1_inc_or_dec = DEC
        j_first_variation0_end = col_max + 1
        j_first_variation1_end = -1
        first_variation = COL
        i_start = 0
        i_end = row_max
        j0_start = 0
        j0_end = col_max
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    elif type == LEFT_TOP_DOWN:
        i_record = i_min
        j_record = j_min
        i_inc_or_dec = INC
        j0_inc_or_dec = INC
        j1_inc_or_dec = DEC
        j_first_variation0_end = row_max + 1
        j_first_variation1_end = -1
        first_variation = ROW
        i_start = 0
        i_end = col_max
        j0_start = 0
        j0_end = row_max
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    elif type == RIGHT_TOP_LEFT:
        i_record = i_min
        j_record = col_max
        i_inc_or_dec = INC
        j0_inc_or_dec = DEC
        j1_inc_or_dec = INC
        j_first_variation0_end = -1
        j_first_variation1_end = col_max + 1
        first_variation = COL
        i_start = 0
        i_end = row_max
        j0_start = col_max - 1
        j0_end = -1
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    elif type == RIGHT_TOP_DOWN:
        i_record = col_max
        j_record = row_min
        i_inc_or_dec = DEC
        j0_inc_or_dec = INC
        j1_inc_or_dec = DEC
        j_first_variation0_end = row_max + 1
        j_first_variation1_end = -1
        first_variation = ROW
        i_start = col_max - 1
        i_end = -1
        j0_start = 0
        j0_end = row_max
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    elif type == LEFT_DOWN_RIGHT:
        i_record = row_max
        j_record = col_min
        i_inc_or_dec = DEC
        j0_inc_or_dec = INC
        j1_inc_or_dec = DEC
        j_first_variation0_end = col_max + 1
        j_first_variation1_end = -1
        first_variation = COL
        i_start = row_max - 1
        i_end = -1
        j0_start = 0
        j0_end = col_max
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    elif type == LEFT_DOWN_UP:
        i_record = col_min
        j_record = row_max
        i_inc_or_dec = INC
        j0_inc_or_dec = DEC
        j1_inc_or_dec = INC
        j_first_variation0_end = -1
        j_first_variation1_end = row_max + 1
        first_variation = ROW
        i_start = 0
        i_end = col_max
        j0_start = row_max - 1
        j0_end = -1
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    elif type == RIGHT_DOWN_LEFT:
        i_record = row_max
        j_record = col_max
        i_inc_or_dec = DEC
        j0_inc_or_dec = DEC
        j1_inc_or_dec = INC
        j_first_variation0_end = -1
        j_first_variation1_end = col_max + 1
        first_variation = COL
        i_start = row_max - 1
        i_end = -1
        j0_start = col_max - 1
        j0_end = -1
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    elif type == RIGHT_DOWN_UP:
        i_record = col_max
        j_record = row_max
        i_inc_or_dec = DEC
        j0_inc_or_dec = DEC
        j1_inc_or_dec = INC
        j_first_variation0_end = -1
        j_first_variation1_end = row_max + 1
        first_variation = ROW
        i_start = col_max - 1
        i_end = -1
        j0_start = row_max - 1
        j0_end = -1
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    else:
        i_record = i_min
        j_record = j_min
        i_inc_or_dec = INC
        j0_inc_or_dec = INC
        j1_inc_or_dec = DEC
        j_first_variation0_end = col_max + 1
        j_first_variation1_end = -1
        first_variation = COL
        i_start = 0
        i_end = row_max
        j0_start = 0
        j0_end = col_max
        j1_start = j0_end + j1_inc_or_dec
        j1_end = j0_start + j1_inc_or_dec
    if first_variation == COL:
        idx = 0
        alternate = False
        for i in range(i_start, i_end, i_inc_or_dec):
            alternate = not alternate
            if alternate:
                for j in range(j0_start, j0_end, j0_inc_or_dec):
                    if src_array[i][j]:
                        src_array[i][j] = idx + 1
                        idx += 1
                    else:
                        src_array[i][j] = 0
                
            else:
                for j in range(j1_start, j1_end, j1_inc_or_dec):
                    if src_array[i][j]:
                        src_array[i][j] = idx + 1
                        idx += 1
                    else:
                        src_array[i][j] = 0
                
        
    else:
        idx = 0
        alternate = False
        for i in range(i_start, i_end, i_inc_or_dec):
            alternate = not alternate
            if alternate:
                for j in range(j0_start, j0_end, j0_inc_or_dec):
                    if src_array[j][i]:
                        src_array[j][i] = idx + 1
                        idx += 1
                    else:
                        src_array[j][i] = 0
                
            else:
                for j in range(j1_start, j1_end, j1_inc_or_dec):
                    if src_array[j][i]:
                        src_array[j][i] = idx + 1
                        idx += 1
                    else:
                        src_array[j][i] = 0
                
        

