# -*- coding: utf-8 -*


import EMC as emc
import time
import tushare as ts
import pandas as pd

# maybe you want to change year and season
cur_year = 2017
cur_season = 1

forcast_year = 2017
forcast_season = 2


###############################################################################################################

# 循环迭代判断每一个值，执行score = score + x, 如第一个值：毛利>=20%时，score +=2
gross_profit_dict = {'20': 2, '30': 1, '40': 1, '60': 1, '70': 1, '80': 1}

# 净利润同比增长
net_profit_growth_dict = {'30': 1, '50': 2, '80': 1, '100': 1, '140': 1, '160': 1, '180': 1, '200': 1, '240': 1,
                          '280': 1}
# 营业收入同比增长
rev_profit_growth_dict = {'10': 1, '20': 1, '30': 1, '40':2, '50': 1, '80': 1, '100': 1, '140': 1, '160': 1, '180': 1,
                          '200': 1, '240': 1, '280': 1}

# reservedPerShare
reservedPerShare_dict = {'0.5': 2, '1': 1, '1.5': 1, '2': 1, '3': 1}

# roe
roe_dict = {'10': 1, '15': 1, '20': 1, '30': 1}

# 每股未分配利润
perundp_dict = {'0.5': 2, '1': 1, '1.5': 1, '2': 1, '3': 1}

# 行业评分字典
industry_dict = {'区域地产': -5, '房地产': -5, '通信行业': 3, '互联网': 3, '半导体': 1, '电信运营': 3, '软件服务': 2, '环境保护': 4}

# type 业绩预告
forcast_dict = {'预盈': 5, '预增': 5, '预升': 5, '预降': -5, '预亏': -5, '预减': -5}


####################################################################################

dateStr = time.strftime("%Y%m%d", time.localtime())

def save_forecast_data():
    forecast_cols = ['股票代码', '预告类型', '预告日期', '变动范围']
    fd = ts.forecast_data(forcast_year, forcast_season)
    del fd['name']
    del fd['pre_eps']
    fd.columns = forecast_cols;
    fd.to_csv("forecast_%s.csv"%dateStr, encoding="utf-8", index=False)


def do_filter():

    #p1 = pd.read_csv("stock_basic_%s.csv"%dateStr)
    p1 = pd.read_csv("stock_basic_20170328.csv")
    p2 = pd.read_csv("stock_latest_indicator_%s.csv"%dateStr)

    tt = p1.merge(p2, on="股票代码", how="right")

    ff = pd.read_csv("forecast_%s.csv"%dateStr)
    t = tt.merge(ff, on="股票代码", how="left")

    # add score column
    t['score'] = 0

    for d in gross_profit_dict.keys():
        t.ix[t['毛利率(%)'] >= float(d), 'score'] = t.score + gross_profit_dict[d]

    for d in roe_dict.keys():
        t.ix[t['加权净资产收益率(%)'] >= float(d), 'score'] = t.score + roe_dict[d]

    for d in net_profit_growth_dict.keys():
        t.ix[t['归属净利润同比增长(%)'] >= float(d), 'score'] = t.score + net_profit_growth_dict[d]

    for d in rev_profit_growth_dict.keys():
        t.ix[t['营业总收入同比增长(%)'] >= float(d), 'score'] = t.score + rev_profit_growth_dict[d]

    for d in reservedPerShare_dict.keys():
        t.ix[t['每股公积金(元)'] >= float(d), 'score'] = t.score + reservedPerShare_dict[d]

    for d in perundp_dict.keys():
        t.ix[t['每股未分配利润(元)'] >= float(d), 'score'] = t.score + perundp_dict[d]

    for d in forcast_dict.keys():
        t.ix[t['预告类型'] == d, 'score'] = t.score + forcast_dict[d]

    for d in industry_dict.keys():
        t.ix[t['所属行业'] == d, 'score'] = t.score + industry_dict[d]
    res = t.sort_values(by='score', ascending=False)
    res.to_csv("result_%s.csv"%dateStr, encoding="utf-8", index=False)
    # return res


emc.saveStockBasic()
emc.getStockLatestIndicator("")
#emc.getStockLatestIndicator("stock_basic_20170328.csv")
save_forecast_data()

do_filter()
