# -*- coding: utf-8 -*-
import tushare as ts

forcast_cols = ['股票代码', '预告类型', '预告日期', '变动范围']

fd = ts.forecast_data(2017, 1)
del fd['name']
del fd['pre_eps']
fd.columns = forcast_cols;

print(fd)