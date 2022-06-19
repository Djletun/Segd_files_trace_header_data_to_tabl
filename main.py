#!/usr/bin/env python3
import os


def BCDto(b):
    a = int(b // 16) * 10
    a = a + b % 16
    return a


def read_byte(p, f):
    f.seek(p)
    byte1 = f.read(1)
    return int.from_bytes(byte1, 'little')


def read_4byte(p, f):
    f.seek(p)
    byte4 = f.read(4)
    return int.from_bytes(byte4, 'big')


def read_ExtdHPos(f):
    ChannelSet = BCDto(read_byte(28, f))
    ExtdHPos = 32 * 3 + 32 * ChannelSet
    return ExtdHPos


def read_NbofSamplesInTrace(f):
    NbofSamplesInTrace = read_4byte(read_ExtdHPos(f) + 32, f)
    return NbofSamplesInTrace


def read_Total_trace(f):
    pos = read_ExtdHPos(f)
    Total_trace = read_4byte(pos + 8, f)
    Total_aux = read_4byte(pos + 12, f)
    Total_live_trace = read_4byte(pos + 24, f)
    return Total_trace, Total_aux, Total_live_trace


def posTrace(f, TraceNb):
    ExndHLength = 32 * BCDto(read_byte(30, f))
    k1 = read_byte(31, f)
    if k1 != 0xff:
        ExnlHLength = 32 * BCDto(k1)
    else:
        k1 = read_byte(39, f)
        k2 = read_byte(40, f)
        ExnlHLength = int(k2) + int(k1) * 256
        ExnlHLength *= 32
    posTrace = read_ExtdHPos(f) + ExndHLength + ExnlHLength
    pos = posTrace + 244 + (244 + read_NbofSamplesInTrace(f) * 4) * TraceNb
    return pos


# ________read LineNb & PointNb
def read_LineNb(segd_file, TraceNb):
    pos_Ext_Tr_Header_1 = posTrace(segd_file, TraceNb) + 20 - 244
    # print('pos', pos_Ext_Tr_Header_1)
    segd_file.seek(pos_Ext_Tr_Header_1)
    byte3 = segd_file.read(3)
    LineNb = int.from_bytes(byte3, 'big')
    byte3 = segd_file.read(3)
    PointNb = int.from_bytes(byte3, 'big')

    pos = pos_Ext_Tr_Header_1 + 161
    # print('pos', pos)
    segd_file.seek(pos)
    byte3 = segd_file.read(3)
    UnitSerialNb = int.from_bytes(byte3, 'big')

    return LineNb, PointNb, UnitSerialNb


def read_numfile(f):
    f.seek(0)
    k1 = read_byte(0, f)
    k2 = read_byte(1, f)
    if (k1 == k2) & (k2 == 0xff):
        pos = 32
        f.seek(pos)
        byte3 = f.read(3)
        numfile = int.from_bytes(byte3, 'big')
    else:
        numfile = BCDto(k2) + BCDto(k1) * 100
    return numfile


# процедура: создать список с данными из файла segd
def list_of_data_segd(segd_file):
    result = list()
    numfile = read_numfile(segd_file)
    Total_trace, Total_aux, Total_live_trace = read_Total_trace(segd_file)
    for trace_nb in range(Total_trace):
        LineNb, PointNb, UnitSerialNb = read_LineNb(segd_file, trace_nb)
        # процедура переформатирования данных из списка в выходной формат
        result_str = '%12i' % (numfile)
        result_str += '%12i' % (trace_nb)
        result_str += '%18i' % (LineNb)
        result_str += '%18i' % (PointNb)
        result_str += '%18i' % (UnitSerialNb)
        result_str += '\n'
        result.append(result_str)
    return result


############################ получение символа разрыва от версии ОС
if os.name == 'nt':
    symbol = '\\'
if os.name == 'posix':
    symbol = '/'

#print(os.environ)
dir_path = os.path.dirname(os.path.abspath(__file__)) + symbol
print(dir_path)

# dir_path = '/media/me/win10/MY/segd/grp/'  # тестовая папка потом закоментить

dir_files = os.listdir(dir_path)  # всё содержимое папки dir_path
# print(dir_files)
# print(dir_files[0][dir_files[0].rfind('.'):])
segd_files = tuple(filter(lambda s: s[s.rfind('.'):] == '.segd', dir_files))  # только файлы segd
if len(segd_files) == 0:
    print('no segd files in dir')
    exit()
# print('segd_files ', segd_files)
# создаем папку result
if not os.path.isdir(dir_path + 'result'):
    os.mkdir(dir_path + 'result')

# цикл по списку файлов с записью списка в файл

with open(dir_path + 'result' + symbol + 'result.txt', 'w') as result_file:
    for file_path in segd_files:
        with open(dir_path + file_path, 'rb') as segd_file:
            result_file.writelines(list_of_data_segd(segd_file))
            segd_file.close()
    result_file.close()
