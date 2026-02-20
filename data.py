import mplfinance as mpf
import pandas as pd
import os
import requests as request
import akshare as ak
# 取得資料
def getData(prod, st, ed):
    try:
        df = ak.stock_zh_a_hist(symbol=str(prod), period="daily", start_date=st.replace("-", ""), end_date=ed.replace("-", ""), adjust="")
        if "日期" in df.columns:
            df["date"] = pd.to_datetime(df["日期"])
        else:
            df["date"] = pd.to_datetime(df["date"])
        df = df.set_index(df["date"])
        if all(col in df.columns for col in ["开盘","最高","最低","收盘","成交量"]):
            df = df[["开盘","最高","最低","收盘","成交量"]].copy()
            df.columns = ["open","high","low","close","volume"]
        else:
            df = df[["open","high","low","close","volume"]].copy()
        return df
    except Exception:
        return pd.DataFrame(columns=["open","high","low","close","volume"])



# 回測邏輯
def backTest(data, prod, boolExpression):
    position = 0
    strategy = 0
    trade = pd.DataFrame()
    for i in range(40,data.shape[0]-1):
        # 基本運算變數取得
        # 近三日基本數據
        if i <30:
            c_time = data.index[:i]
        else:
            c_time = data.index[i-20:i]
        volume = data.loc[c_time, 'volume']
        c_low = data.loc[c_time, 'low']
        c_high = data.loc[c_time, 'high']
        c_close = data.loc[c_time, 'close']
        c_open = data.loc[c_time, 'open']
        ma5 = data.loc[c_time, '5ma']
        ma10 = data.loc[c_time, '10ma']
        ma20 = data.loc[c_time, '20ma']
        ceil = data.loc[c_time, 'ceil']
        floor = data.loc[c_time, 'floor']
        K = data.loc[c_time,"K"]
        D = data.loc[c_time, "D"]
        D5mean = data.loc[c_time, "D5mean"]
        #明日
        n_time = data.index[i+1]
        n_open = data.loc[n_time, 'open']
        
        if position == 0: #未持有，進場邏輯
            if eval(boolExpression):
                # 策略一-非下跌排列KD黃金交叉，止損4%止盈7%，勝率46.7%期望值1.137% OK
                position = 1
                strategy = 1
                order_i = i+1
                order_time = n_time
                order_price = n_open
                order_unit = 1
        elif position == 1: #持有，出場邏輯
            if strategy ==1:
                # 策略1賣出條件
                if(c_low[-1]) < (order_price*0.92):
                    position = 0
                    cover_time = c_time[-1]
                    cover_price = order_price*0.92
                    #買賣完成，建立交易紀錄
                    trade = trade.append(pd.Series([
                        prod, 'Buy', order_time, order_price, order_time, cover_price, cover_time
                    ]),ignore_index=True)
                elif(c_high[-1]>(order_price*1.2)):
                    position = 0
                    cover_time = c_time[-1]
                    cover_price = order_price*1.2
                    #買賣完成，建立交易紀錄
                    trade = trade.append(pd.Series([
                        prod, 'Buy', order_time, order_price, order_time, cover_price, cover_time
                    ]),ignore_index=True)
                elif (c_close[-1] < (order_price*0.92)) or c_close[-1] > (order_price*1.2):
                    position = 0
                    cover_time = n_time
                    cover_price = n_open
                    #買賣完成，建立交易紀錄
                    trade = trade.append(pd.Series([
                        prod, 'Buy', order_time, order_price, order_time, cover_price, cover_time
                    ]),ignore_index=True)
    return trade

# 爬蟲取得股票清單
def getStockList():
    bakfile = "StockList.csv"
    if(os.path.exists(bakfile)):
        df = pd.read_csv(bakfile)
    else:
        try:
            df = ak.stock_tw_stock_info()
        except Exception:
            df = ak.stock_info_a_code_name()
        df.to_csv(bakfile)
    return df

# goodInfo篩選直接抓csv股票清單
def getReadStockList():
    # 資料來源
    # https://goodinfo.tw/tw2/StockList.asp?MARKET_CAT=%E8%87%AA%E8%A8%82%E7%AF%A9%E9%81%B8&INDUSTRY_CAT=%E6%88%91%E7%9A%84%E6%A2%9D%E4%BB%B6&FL_ITEM0=%E5%96%AE%E6%97%A5%E6%88%90%E4%BA%A4%E9%87%8F%28%E5%BC%B5%29%E2%80%93%E7%95%B6%E6%97%A5&FL_VAL_S0=1000&FL_VAL_E0=&FL_ITEM1=%E6%98%A8%E6%97%A5%E6%88%90%E4%BA%A4%E5%BC%B5%E6%95%B8+%28%E5%BC%B5%29&FL_VAL_S1=1000&FL_VAL_E1=&FL_ITEM2=&FL_VAL_S2=&FL_VAL_E2=&FL_ITEM3=&FL_VAL_S3=&FL_VAL_E3=&FL_ITEM4=&FL_VAL_S4=&FL_VAL_E4=&FL_ITEM5=&FL_VAL_S5=&FL_VAL_E5=&FL_ITEM6=&FL_VAL_S6=&FL_VAL_E6=&FL_ITEM7=&FL_VAL_S7=&FL_VAL_E7=&FL_ITEM8=&FL_VAL_S8=&FL_VAL_E8=&FL_ITEM9=&FL_VAL_S9=&FL_VAL_E9=&FL_ITEM10=&FL_VAL_S10=&FL_VAL_E10=&FL_ITEM11=&FL_VAL_S11=&FL_VAL_E11=&FL_RULE0=&FL_RULE1=&FL_RULE2=&FL_RULE3=&FL_RULE4=&FL_RULE5=&FL_RANK0=&FL_RANK1=&FL_RANK2=&FL_RANK3=&FL_RANK4=&FL_RANK5=&FL_FD0=&FL_FD1=&FL_FD2=&FL_FD3=&FL_FD4=&FL_FD5=&FL_SHEET=%E4%BA%A4%E6%98%93%E7%8B%80%E6%B3%81&FL_SHEET2=%E6%97%A5&FL_MARKET=%E5%8F%AA%E6%9C%89%E4%B8%8A%E5%B8%82&FL_QRY=%E6%9F%A5++%E8%A9%A2
    bakfile = "readStockList.csv"
    if(os.path.exists(bakfile)):
        df = pd.read_csv(bakfile, encoding="utf-8")
        df = df[["代號", "名稱"]]
        for n in range(df.shape[0]):
            df.loc[n,"代號"] = str(df.loc[n,"代號"]).replace("=", "").replace("\"", "")
        return df
    else:
        print("無法讀取")
        return False
