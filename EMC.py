# -*- coding: utf-8 -*-


import lxml.html
from io import StringIO
import pandas as pd
import time
# from bs4 import BeautifulSoup as bs

#stock ranges for the three market

sh_start = 600000
sh_max = 603999
#sh_max = 600010
sz_start = 1;
sz_max = 2861;
#sz_max = 10;
gem_start = 300001
gem_max = 300639
#gem_max = 300010


__url = "http://f10.eastmoney.com/f10_v2/OperationsRequired.aspx?code=%s"

__url2 = "http://quote.eastmoney.com/%s.html"

__stock_basic_cols = ["股票代码", "股票名称", "所属行业", "PE(动)", "总市值"]
__cols_latest_indicator = ['股票代码', '基本每股收益(元)', '每股净资产(元)', '每股经营现金流(元)', '每股公积金(元)', '总股本(万股)', '每股未分配利润(元)',
                           '加权净资产收益率(%)', '毛利率(%)', '资产负债率(%)', '营业总收入同比增长(%)', '归属净利润同比增长(%)', '扣非净利润同比增长(%)']
__tr_format = "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"

"""
Get latest indicator by stock code

:param code should be like sh600012
"""
def __getLatestIndicatorByCode(code):
    print("getting code:", code[-6:])
    html = lxml.html.parse(__url % code)
    res = html.xpath("//div[@class=\"content\"]")
    tables = res[0].xpath("//table")
    t1 = tables[0]  # etree object , can be treat as an array
    t2 = tables[1]

    tr = __tr_format % (
    code[-6:], t1[1][1][0].text, t1[1][3][0].text, t1[1][5][0].text, t1[2][3][0].text, t1[2][5][0].text,
    t1[3][3][0].text, t2[1][1][0].text, t2[1][4][0].text, t2[1][7][0].text, t2[2][7][0].text, t2[3][7][0].text,
    t2[4][7][0].text)

    tr = tr.replace('--', '0')
    return tr

    """
    #print(tr)
    print(t1[1][0][0].text,':',t1[1][1][0].text)
    print(t1[1][2][0].text, ':', t1[1][3][0].text)
    print(t1[1][4][0].text, ':', t1[1][5][0].text)

    print(t1[2][2][0].text, ':', t1[2][3][0].text)
    print(t1[2][4][0].text, ':', t1[2][5][0].text)

    print(t1[3][2][0].text, ':', t1[3][3][0].text)

    ##########

    print(t2[1][0][0].text, ':', t2[1][1][0].text)
    print(t2[1][3][0].text, ':', t2[1][4][0].text)
    print(t2[1][6][0].text, ':', t2[1][7][0].text)
    print(t2[2][6][0].text, ':', t2[2][7][0].text)
    print(t2[3][6][0].text, ':', t2[3][7][0].text)
    print(t2[4][6][0].text, ':', t2[4][7][0].text)

   # print(lxml.html.tostring(tables[0],encoding='utf-8').decode('utf-8'))
    #print(lxml.html.tostring(tables[1], encoding='utf-8').decode('utf-8'))
    """


def getStockLatestIndicator(basic_file=""):
    dateStr = time.strftime("%Y%m%d", time.localtime())
    if not basic_file.strip():
        basic_file = 'stock_basic_' + dateStr + '.csv'
    basic_data = pd.read_csv(basic_file)
    code = basic_data["股票代码"]
    cl = list(code)
    trs = []
    for c in cl:

        try:
            if c >= 600000:
                tr = __getLatestIndicatorByCode("sh" + str(c))

            elif c < 100000:
                cs = __fullSzCodeStr(c)
                tr = __getLatestIndicatorByCode("sz" + cs)
            else:
                tr = __getLatestIndicatorByCode("sz" + str(c))
            trs.append(tr)
        except Exception as e:
            print(e, ", For Stock Code:", str(c))
            continue

    table = "<table>%s</table>" % trs
    al = pd.read_html(table)[0]
    al.columns = __cols_latest_indicator

    dateStr = time.strftime("%Y%m%d", time.localtime())
    fname = 'stock_latest_indicator_' + dateStr + ".csv"
    al.to_csv(fname, encoding='utf-8', index=False)
    return al


"""
Fullfill shenzhen code from 4 to 000004
:param code is integer type
"""


def __fullSzCodeStr(code):
    z = 6 - len(str(code))
    a = z * ['0']
    return ''.join(a) + str(code)


"""
Get the basic info :code , name and sector by stock code
:param code is a string type and should be like 'sh600022'
"""


def __getBasicInfoTr(code):
    try:
        html = lxml.html.parse(__url2 % code)
        if __isValidPage(html):
            ns = html.xpath("//h2[@id=\"name\"]")
            cs = html.xpath("//b[@id=\"code\"]")
            sector = html.xpath("//div[@class=\"aide nb\"]")  # 所属行业
            PE = html.xpath("//span[@id=\"gt6_2\"]")  # PE
            total_value = html.xpath("//span[@id=\"gt7_2\"]")  # 总市值

            pe = PE[0].text.replace("-", "0")

            t_value = total_value[0].text[:-1]
            t_value = "0" if not t_value.strip() else t_value

            print(cs[0].text, ":", ns[0].text, sector[0][0][2].text, pe, t_value)
            return "<tr><td>" + cs[0].text + "</td><td>" + ns[0].text + "</td><td>" + sector[0][0][
                2].text + "</td><td>" + \
                   pe + "</td><td>" + t_value + "</td></tr>"
        else:
            print("page is 404")
    except:
        print("fail to load this page. Probably because this is a wrong stock code: " + code)
        return ""


"""
check if the page is valid. as stocks maybe suspended due to some reason.
"""


def __isValidPage(html):
    ts = html.xpath("//title")
    title = ts[0].text
    return title.find("404 -") < 0


"""
save basic info (code , name and sector) of all stocks to cvs file. 
and this file can be read into a pandas dataframe and merges with other dataframes
"""


def saveStockBasic(fname=""):

    code = sh_start
    trs = []
    while 1:
        tr = __getBasicInfoTr("sh" + str(code))
        if tr.strip() == '':
            if code > sh_max:
                break
            else:
                code = code + 1
                continue

        trs.append(tr)
        print("Get code " + str(code) + " successfully...")
        code = code + 1

    code = sz_start
    while 1:
        c = __fullSzCodeStr(code)
        tr = __getBasicInfoTr("sz" + c)
        if tr.strip() == '':
            if code > sz_max:
                break
            else:
                code = code + 1
                continue

        trs.append(tr)
        print("Get code " + str(code) + " successfully...")
        code = code + 1

    code = gem_start
    while 1:
        tr = __getBasicInfoTr("sz" + str(code))
        if tr.strip() == '':
            if code > gem_max:
                break
            else:
                code = code + 1
                continue

        trs.append(tr)
        print("Get code " + str(code) + " successfully...")
        code = code + 1

    table = "<table>%s</table>" % trs
    res = pd.read_html(StringIO(table))[0]
    res.columns = __stock_basic_cols
    if not fname.strip():
        dateStr = time.strftime("%Y%m%d", time.localtime())
        fname = 'stock_basic_' + dateStr + ".csv"
    res.to_csv(fname, encoding='utf-8', index=False)
    return res

# saveStockBasic()

# scrawLatestIndicator()
