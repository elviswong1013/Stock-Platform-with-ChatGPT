import sys
import json
import os
import base64
import re
from datetime import date
from dotenv import load_dotenv
from openai import OpenAI
from openai import APITimeoutError
import httpx
import time
from pydantic import BaseModel, Field, field_validator
from tqdm.auto import tqdm

# 取得腳本所在目錄作為基準路徑
BASE_DIR = os.path.dirname(__file__)
os.chdir(BASE_DIR)
# 載入環境變數（llm_settings.env），允許覆蓋既有變數
load_dotenv(os.path.join(BASE_DIR, 'llm_settings.env'), override=True)

def load_llm():
    """
    讀取 LLM 相關設定
    回傳: api_base, model, api_key
    """
    api_base = os.getenv('LLM_API_BASE', 'https://api.openai.com/v1')
    model = os.getenv('LLM_MODEL', 'gpt-4o-mini')
    api_key = os.getenv('OPENAI_API_KEY') or os.getenv('LLM_API_KEY', '')
    return api_base, model, api_key

class StockAnalysis(BaseModel):
    decision: str = Field(..., pattern="^(buy|sell|hold)$")
    confidence: int = Field(..., ge=0, le=100)
    summary: str = Field(..., min_length=1)
    target_price_range: str = Field(..., min_length=1)
    target_price_range_reason: str = Field(..., min_length=1)
    target_holding_time: str = Field(..., min_length=1)
    target_holding_time_reason: str = Field(..., min_length=1)

    @field_validator("decision")
    def validate_decision(cls, v):
        if v not in {"buy", "sell", "hold"}:
            raise ValueError("decision 必須為 buy、sell 或 hold")
        return v

    @field_validator("confidence")
    def validate_confidence(cls, v):
        if not 0 <= v <= 100:
            raise ValueError("confidence 必須在 0 到 100 之間")
        return v


# 初始化 LLM 連線參數
API_BASE, MODEL, API_KEY = load_llm()
client = OpenAI(base_url=API_BASE, api_key=API_KEY)

def file_to_data_uri(path):
    """
    將圖片檔案轉換為 data URI (base64)
    參數:
        path: 圖片檔案路徑
    回傳:
        data URI 字串
    """
    with open(path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('ascii')
    return f"data:image/png;base64,{b64}"

def analyze_image(code, img_path, retries=3, timeout=60):
    """
    呼叫 OpenAI API 針對股票技術圖進行分析
    參數:
        code: 股票代碼
        img_path: 圖片路徑
    回傳:
        API 回應內容 (字串)
    """


    uri = file_to_data_uri(img_path)
    prompt = (
        "根據所附K線與MACD/均線等圖，請回答：\n"
        "1) 明日是否應該買入、賣出或觀望，並給出理由與信心度(0-100)。\n"
        "2) 接下來10-30天的趨勢與價格變動方向的摘要。\n"
        "3) 建議的目標（买入或卖出）價位上看或下看的區間。\n"
        "4) 建議的目標價位上看或下看的區間的理由。\n"
        "5) 如果建议买入或卖出的时间，以及建议持有的时间长度，提供理由。\n"
        "6) 以JSON輸出符合以下JSON Schema：\n"
        f"{StockAnalysis.model_json_schema()}"
    )
    last_err = None
    for attempt in range(retries):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role":"system","content":"你是資深量化分析師，專注於技術圖形解讀。"},
                    {"role":"user","content":[
                        {"type":"text","text":f"股票代碼：{code}\n{prompt}"},
                        {"type":"image_url","image_url":{"url":uri}}
                    ]}
                ],
                timeout=timeout
            )
            content = resp.choices[0].message.content
            usage = resp.usage
            print(f"[Token Usage] 股票 {code}: prompt={usage.prompt_tokens}, completion={usage.completion_tokens}, total={usage.total_tokens}")
            return content, usage
        except (APITimeoutError, httpx.ConnectTimeout, httpx.ReadTimeout) as e:
            last_err = e
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
        except Exception as e:
            last_err = e
            break
    return json.dumps({"error": "request_failed", "detail": str(last_err)}), None

def output_to_json(content, code, out_dir):
    """
    將分析結果輸出為 JSON 檔案
    參數:
        results: 分析結果字典，鍵為股票代碼，值為分析內容
        out_dir: 輸出目錄路徑
    """
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{code}.json")
    def parse_json_content(s):
        t = s.strip()
        if t.startswith("```"):
            t = re.sub(r"^```[a-zA-Z]*\s*", "", t)
            t = re.sub(r"\s*```$", "", t).strip()
        start = t.find("{")
        end = t.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = t[start:end+1]
            try:
                return json.loads(candidate)
            except Exception:
                pass
        return json.loads(t)
    with open(out_path, "w", encoding="utf-8") as f:
        try:
            data = parse_json_content(content)
        except Exception:
            data = {"raw": content}
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[Save] {code} 分析結果已保存至 {out_path}")

def safe_load_json_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        if not text.strip():
            return {}
        try:
            return json.loads(text)
        except Exception:
            return {"raw": text}
    except Exception:
        return {}

def main():
    """
    主程式入口
    支援單檔或批次分析
    執行方式:
        python script.py [股票代碼|all]
    """
    args = sys.argv[1:]
    today = date.today().isoformat()
    root = os.path.join(BASE_DIR, "notebooks/plots", today)
    out_dir = os.path.join(BASE_DIR, "analysis_results", today)
    os.makedirs(out_dir, exist_ok=True)

    print(f"""root: {root}""")
    results = {}
    total_tokens = 0
    total_output_tokens = 0
    total_input_tokens = 0
    counter = 0
    print(f"""len(args):{len(args)}""")
    print(f"""args[0]:{args[0]}""")

    # 若有指定單一股票代碼且非 "all"
    if len(args) >= 1 and args[0] != "all":
        print(f"""len(args) >= 1 and args[0] != "all":{len(args) >= 1 and args[0] != "all"}""")
        code = args[0]
        out_path = os.path.join(out_dir, f"{code}.json")
        # 如果已存在分析結果，直接讀取
        if os.path.exists(out_path):
            obj = safe_load_json_file(out_path)
            results[code] = json.dumps(obj, ensure_ascii=False)
            print(f"[Skip] {code} 已存在分析結果，略過重新生成")
        else:
            img_path = os.path.join(root, f"{code}.png")
            if os.path.exists(img_path):
                out, token_spent = analyze_image(code, img_path)
                
                output_to_json(content = out, code = code, out_dir = out_dir)
                # 將 JSON 字串轉回字典
                results[code] = safe_load_json_file(out_path)
                print(f"""out: {out}""")
                total_tokens += token_spent.total_tokens
                total_output_tokens += token_spent.completion_tokens
                total_input_tokens += token_spent.prompt_tokens
                counter += 1
    else:
        # 批次處理今日目錄下所有 PNG
        print(f"""root: {root}""")
        if os.path.isdir(root):
            pngs = [n for n in os.listdir(root) if n.lower().endswith(".png")]
            for name in tqdm(pngs, desc="Analyzing charts", unit="stock"):
                code = os.path.splitext(name)[0]
                out_path = os.path.join(out_dir, f"{code}.json")
                if os.path.exists(out_path):
                    obj = safe_load_json_file(out_path)
                    results[code] = json.dumps(obj, ensure_ascii=False)
                    print(f"[Skip] {code} 已存在分析結果，略過重新生成")
                    continue
                else:
                    img_path = os.path.join(root, name)
                out, token_spent = analyze_image(code, img_path)
                output_to_json(content = out, code = code, out_dir = out_dir)
                results[code] = safe_load_json_file(out_path)
                if token_spent:
                    total_tokens += token_spent.total_tokens
                    total_output_tokens += token_spent.completion_tokens
                    total_input_tokens += token_spent.prompt_tokens
                    counter += 1
                # if counter >= 2:
                #     break
    print(f"Total tokens: {total_tokens}")
    print(f"Total output tokens: {total_output_tokens}")
    print(f"Total input tokens: {total_input_tokens}")
    print(f"Total stocks processed: {counter}")
    
    print(results)
if __name__ == "__main__":
    main()
