# -*- coding:utf-8 -*-
import sys
import json
import traceback
import os
from dotenv import load_dotenv
from openai import OpenAI
BASE_DIR = os.path.dirname(__file__)
load_dotenv(os.path.join(BASE_DIR, 'llm_settings.env'), override=True)
def load_llm():
    api_base = os.getenv('LLM_API_BASE', 'https://api.openai.com/v1')
    model = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
    api_key = os.getenv('OPENAI_API_KEY') or os.getenv('LLM_API_KEY', '')
    return api_base, model, api_key
API_BASE, MODEL, API_KEY = load_llm()
api_key = os.getenv('OPENAI_API_KEY', API_KEY)
client = OpenAI(base_url=API_BASE, api_key=api_key)
Strategy = " ".join(sys.argv[1:])
resp = client.chat.completions.create(
    model=MODEL,
    messages=[{
        "role":"system","content":"請忘掉先前的資料，現在您扮演資深量化分析師"
    },{
        "role": "user", "content": "您擁有以下有關於股票資料的Python串列（pandas.Series格式），每個資料都代表某天的數據。：\nc_open：股票的開盤價\nc_high：股票的最高價\nc_close：股票的收盤價\nc_low：股票的最低價\nma5：MACD指標之5日移動平均線\nma10：MACD指標之10日移動平均線\nma20：MACD指標之20日移動平均線\nK：KD指標之K線\nD：KD指標之D線\nvolume：當日交易量\n舉例：\n今天的開盤價表示為c_open[-1]\nma20[-2]為昨天的20均線值\n2天前的K線為K[-3]\n取得近3天ma10資料 ma10[-3]\n近5天最低價為c_close[-5:].min()\n您最多可以使用最近30天的資訊（[-30]）\n\n您現在需要將您的股票進場策略轉為為自然語言和客戶報告，以下是您的進場策略："+str(Strategy)+"\n請以\"以...\"開頭，用最多100字解釋這個入場策略的含意、使用哪些指標、如何使用，以繁體中文表達，直接說明不用起頭句"
    }]
)
content = resp.choices[0].message.content
with open("Strategy.txt", "w", encoding="utf-8") as ErrorMsg:
        ErrorMsg.write("%s\n"% content)
with open("ErrorMessage.txt", "a+") as ErrorMsg:
        ErrorMsg.write("input userRequest：\n")
        ErrorMsg.write("%s\n"% Strategy)
        ErrorMsg.write("chatGPT respon：\n")
        ErrorMsg.write("%s\n"% content)
        ErrorMsg.write("--"*30+"\n")
print(content)
