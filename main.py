import os
import glob
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Union, List

base_dir = "/Users/bernoulli_hermes/.qlib/qlib_data/cn_data/"

# 读取日期文件
dates = pd.read_csv(f'{base_dir}calendars/day.txt', header=None, names=['date'], parse_dates=['date'], index_col=['date'])

# 读取instruments文件
instruments = {}
for file in glob.glob(f'{base_dir}instruments/*.txt'):
    name = os.path.splitext(os.path.basename(file))[0]
    instruments[name] = pd.read_csv(file, header=None, sep='\t')
    instruments[name].columns = ['code', 'start_date', 'end_date']
    instruments[name]['start_date'] = pd.to_datetime(instruments[name]['start_date'])
    instruments[name]['end_date'] = pd.to_datetime(instruments[name]['end_date'])

def read_bin(file_path: Union[str, Path], start_index, end_index):
    file_path = Path(file_path).expanduser().resolve()
    with file_path.open("rb") as f:
        # read start_index
        ref_start_index = int(np.frombuffer(f.read(4), dtype="<f")[0])
        si = max(ref_start_index, start_index)
        if si > end_index:
            return pd.Series(dtype=np.float32)
        # calculate offset
        f.seek(4 * (si - ref_start_index) + 4)
        # read nbytes
        count = end_index - si + 1
        data = np.frombuffer(f.read(4 * count), dtype="<f")
        series = pd.Series(data, index=dates.index[si:si+len(data)])
    return series

# 读取各个bin文件
features = {}
for _, row in instruments['all'].iterrows():
    code = row['code']
    features[code] = {}
    for fname in ['open', 'close', 'high', 'low', 'volume', 'change', 'factor']:
        fpath = f'{base_dir}features/{code}/{fname}.day.bin'
        if os.path.exists(fpath):
            start_date = row['start_date']
            end_date = row['end_date']
            if start_date not in dates.index:
                start_date = dates.index[dates.index.get_loc(start_date, method='nearest')]
            if end_date not in dates.index:
                end_date = dates.index[dates.index.get_loc(end_date, method='nearest')]
            start_index = dates.index.get_loc(start_date)
            end_index = dates.index.get_loc(end_date)
            features[code][fname] = read_bin(fpath, start_index, end_index)
        else:
            print(f"File not found: {fpath}")

# 合并数据        
data = {}        
for code, df_dict in features.items():
    df = pd.concat(df_dict, axis=1)
    data[code] = df
    
# 访问数据    
print(data['SH600000'].head())