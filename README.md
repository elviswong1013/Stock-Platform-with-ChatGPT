# AI智能選股助⼿：結合Chat GPT的投資信號偵測技術

## 簡介

本作品結合大數據分析及生成式AI，打造客製化股票分析系統，協助股市投資者快速找出適合進場的股票標的。過去面臨的挑戰是，投資者多以自然語言方式思考進場策略，但對於程式系統來說，無法直接理解投資者的進場策略，自然無法馬上找出符合策略的標的。

**為此本作品：**

1. 引入Chat GPT 協助投資者將進場策略轉譯為程式讀取的條件判斷式 
2. 建立股票預測系統，利用開源預測模型「Prophet」進行股價預測 
3. 建立歷史回測系統，提供回測數據計算

##  系統介面

![image](https://github.com/Heng1222/Stock-Platform-with-ChatGPT/blob/main/Readme_img/%E5%88%86%E6%9E%90%E7%B5%90%E6%9E%9C1.png)

![image](https://github.com/Heng1222/Stock-Platform-with-ChatGPT/blob/main/Readme_img/%E7%94%9F%E6%88%902.png)

![image](https://github.com/Heng1222/Stock-Platform-with-ChatGPT/blob/main/Readme_img/%E5%88%86%E6%9E%90%E7%B5%90%E6%9E%9C3.png)


## 環境
```
XAMPP v3.3.0
Apache & MYSQL
Python 3.7.9
```
## 技術

+ PHP Server
+ HTML/CSS
+ JavaScript、Ajax
+ Python
  + Pandas
  + Chat GPT API
  + Prophet

## Python 套件
```
stastic
pandas
datetime
mplfinance
json
sys
traceback
os
requests
akshare
```

## 股價資料來源

本專案使用 Akshare 介面取得股票資料（如股票清單、歷史行情等），包含開盤、最高、最低、收盤價及交易量等欄位
[Akshare](https://akshare.akfamily.xyz/)

## ChatGPT API

使用者以自然語言輸入選股策略，並由ChatGPT協助將其轉為等價的條件判斷式，並從股票清單(所有有興趣的股票標的)中篩選出當下符合使用者策略的標的

[Open API](https://platform.openai.com/docs/api-reference/introduction)

## 回測數據

根據該次篩選出的股票標的進行回測計算，依照當前使用者的選股策略作為進場策略，計算其投資結果並儲存為Json格式檔案，儲存範例如下：

```
標的代號 : "2867"
公司名稱 : 三商壽
分析日期 : "2024-05-17"
最後收盤價 : 5.72
最後開盤價 : 5.8
總報酬率 : 10.83%
交易次數 : 2
平均報酬 : 5.42%
平均勝率 : 50%
平均獲利 : 19.42%
平均虧損 : -8.59%
期望值 : 0.6304
平均獲利持有天數 : 59
平均虧損持有天數 : 253
```


## Prophet模型

除了歷史回測外，本專案亦採用Prophet模型預測未來股價變化，提供更客觀、更完整的分析需求

[prophet](https://facebook.github.io/prophet/)

## 前端操作介面

簡易前端介面提供使用者操作及查看分析結果
