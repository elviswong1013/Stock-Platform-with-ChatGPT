# -*- coding:utf-8 -*-
import requests
import sys
import json
import traceback
import os
from dotenv import load_dotenv
load_dotenv()
def load_llm():
    base_dir = os.path.dirname(__file__)
    path = os.path.join(base_dir, 'llm_config.json')
    with open(path, 'r', encoding='utf-8') as f:
        conf = json.load(f)
    provider = os.getenv('LLM_PROVIDER', conf.get('default_provider'))
    p = conf.get('providers', {}).get(provider, {})
    api_base = os.getenv('LLM_API_BASE', p.get('api_base', 'https://api.openai.com/v1/chat/completions'))
    model = os.getenv('LLM_MODEL', p.get('model', 'gpt-3.5-turbo'))
    auth_header = os.getenv('LLM_AUTH_HEADER', p.get('auth_header', 'Authorization'))
    auth_scheme = os.getenv('LLM_AUTH_SCHEME', p.get('auth_scheme', 'Bearer'))
    api_key = os.getenv('LLM_API_KEY', p.get('api_key', ''))
    return api_base, model, auth_header, auth_scheme, api_key
API_BASE, MODEL, AUTH_HEADER, AUTH_SCHEME, API_KEY = load_llm()
token_value = f'{AUTH_SCHEME} {API_KEY}' if AUTH_SCHEME else API_KEY
Strategy = " ".join(sys.argv[1:])
response = requests.post(
    API_BASE,
    headers={
        'Content-Type': 'application/json',
        AUTH_HEADER: token_value
    },
    json={
        'model': MODEL,
        'messages': [{
            "role":"system", "content":"""請忘掉先前的資料，現在您扮演資深量化分析師""",
            "role": "user", "content": """您擁有以下有關於股票資料的Python串列（pandas.Series格式），每個資料都代表某天的數據。：
c_open：股票的開盤價
c_high：股票的最高價
c_close：股票的收盤價
c_low：股票的最低價
ma5：MACD指標之5日移動平均線
ma10：MACD指標之10日移動平均線
ma20：MACD指標之20日移動平均線
K：KD指標之K線
D：KD指標之D線
volume：當日交易量
舉例：
今天的開盤價表示為c_open[-1]
ma20[-2]為昨天的20均線值
2天前的K線為K[-3]
取得近3天ma10資料 ma10[-3]
近5天最低價為c_close[-5:].min()
您最多可以使用最近30天的資訊（[-30]）

您現在需要將您的股票進場策略轉為為自然語言和客戶報告，以下是您的進場策略："""+str(Strategy)+"""
請以"以..."開頭，用最多100字解釋這個入場策略的含意、使用哪些指標、如何使用，以繁體中文表達，直接說明不用起頭句"""}],
    }
)
jsonr = response.json()
with open("Strategy.txt", "w", encoding="utf-8") as ErrorMsg:
        ErrorMsg.write("%s\n"% jsonr["choices"][0]["message"]["content"])
with open("ErrorMessage.txt", "a+") as ErrorMsg:
        ErrorMsg.write("input userRequest：\n")
        ErrorMsg.write("%s\n"% Strategy)
        ErrorMsg.write("chatGPT respon：\n")
        ErrorMsg.write("%s\n"% jsonr["choices"][0]["message"]["content"])
        ErrorMsg.write("--"*30+"\n")
print(jsonr["choices"][0]["message"]["content"])
