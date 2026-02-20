# -*- coding:utf-8 -*-
import sys
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
BASE_DIR = os.path.dirname(__file__)
load_dotenv(os.path.join(BASE_DIR, 'llm_settings.env'), override=True)
def load_llm():
    api_base = os.getenv('LLM_API_BASE', 'https://api.openai.com/v1')
    model = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
    api_key = os.getenv('OPENAI_API_KEY') or os.getenv('LLM_API_KEY', '')
    print(api_base, model, api_key)
    print(f"""===============================================================================================================================================================\n\n""")
    return api_base, model, api_key
API_BASE, MODEL, API_KEY = load_llm()
api_key = os.getenv('OPENAI_API_KEY', API_KEY)
client = OpenAI(base_url=API_BASE, api_key=api_key)
print(client)
userRequest = " ".join(sys.argv[1:])
resp = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role":"system","content":"請忘掉先前的資料，現在您扮演資深量化分析師"},
        {"role":"user","content":"您現在被要求將投資者入場策略轉為等價股票入場訊號的判斷式，您可以使用所有網路上能找到的資料為輔助。當您的判斷式回傳True表示符合投資者入場策略，可以買進做多，False表示不符合需求。請考慮以下條件：\n預計止損和止盈分別為買入價格的8%和20%。\n希望在10天內完成股票的買進和賣出。\n精準抓到股票起漲點。\n講求獲利。\n每個資料都代表某天的數據。\n\n您擁有以下有關於股票資料的Python串列（pandas.Series格式）：\nc_open：股票的開盤價\nc_high：股票的最高價\nc_close：股票的收盤價\nc_low：股票的最低價\nma5：MACD指標之5日移動平均線\nma10：MACD指標之10日移動平均線\nma20：MACD指標之20日移動平均線\nK：KD指標之K線\nD：KD指標之D線\nvolume：當日交易量\n舉例：\n今天的開盤價表示為c_open[-1]\nma20[-2]為昨天的20均線值\n2天前的K線為K[-3]\n取得近3天ma10資料 ma10[-3]\n近5天最低價為c_close[-5:].min()\n您最多可以使用最近30天的資訊（[-30]）\n\n請確保：\n只能使用上述提供的資料。\n需為合理、有可能達成的條件。\n在符合投資者需求的前提下最佳化判斷式。\n\n投資者需求："+str(userRequest)+"據上述需求，請回傳一個符合需求的布林表達式。當判斷式回傳True代表明天會買入做多布局，回傳False則不買入。請詳細考慮各種指標的搭配和選擇，以最大化利潤。\n只要給我該表達式(不需換行，且and判斷子以&表示，or判斷子以|表示)，其他不用多說。請充分運用您有的資料，講求精確。"}
    ]
)
content = resp.choices[0].message.content
with open("ErrorMessage.txt", "a+", encoding="utf-8") as ErrorMsg:
        ErrorMsg.write("input userRequest：\n")
        ErrorMsg.write("%s\n"% userRequest)
        ErrorMsg.write("chatGPT respon：\n")
        ErrorMsg.write("%s\n"% content)
print(content)
