from pathlib import Path
import srt
import json
import pandas as pd
import time
import re
import openai

# --- API 키 및 설정 ---
openai.api_key = "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"
openai.api_base = "https://api.groq.com/openai/v1"

# --- 감정 점수 (Azure 기준) ---
emotion_valence = {
    "happiness": 1.00,
    "surprise": 0.70,
    "neutral": 0.50,
    "contempt": 0.45,
    "disgust": 0.40,
    "sadness": 0.30,
    "anger": 0.25,
    "fear": 0.10
}

# --- 자막 파싱 함수 ---
def parse_srt_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        srt_text = f.read()
    subtitles = list(srt.parse(srt_text))
    return [
        {
            "id": i + 1,
            "start": sub.start.total_seconds(),
            "end": sub.end.total_seconds(),
            "text": sub.content.strip()
        }
        for i, sub in enumerate(subtitles)
    ]

# --- LLM 분석 함수 ---
def analyze_subtitle(text, emotion_valence, model="llama3-70b-8192"):
    emotion_labels = list(emotion_valence.keys())
    prompt = f"""You are a JSON-only tagging assistant for movie subtitle analysis.

You will be given one subtitle line. Your task is to return exactly one JSON object with the following structure.

**JSON Structure:**
{{
  "emotions": [list of up to 2 emotions, ordered by relevance],
  "situation": "1–5 word phrase summarizing the scene",
  "situation_type": "brief category of situation"
}}

**Rules:**
1.  Choose up to two emotions from the allowed list below. The most relevant emotion comes first.
2.  The output MUST be a single, valid JSON object. Do not add explanations or any text outside the JSON structure.
3.  Ensure all keys and string values are in double quotes. Ensure commas are correctly placed.

**Allowed Emotions:**
{emotion_labels}

**Example:**
Subtitle: "Get away from me! It's going to explode!"
{{
  "emotions": ["fear", "surprise"],
  "situation": "escaping an explosion",
  "situation_type": "action"
}}

---
**Subtitle to Analyze:**
"{text}"
"""
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=250,
    )
    match = re.search(r"\{.*\}", response.choices[0].message.content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception as e:
            print(f"[!] JSON 파싱 실패: {e} | 원본 응답: {response.choices[0].message.content}")
    return {"emotions": [], "situation": "unknown", "situation_type": "unknown"}

# --- 감정 점수 계산 ---
def calc_valence(emotions):
    if not emotions:
        return 0.5
    scores = [emotion_valence.get(e.lower(), 0.5) for e in emotions]
    return sum(scores) / len(scores)

# --- 전체 파이프라인 실행 ---
def run_pipeline(srt_path, start_sec, end_sec, out_json, out_csv):
    subs = parse_srt_file(srt_path)
    subs = [sub for sub in subs if start_sec <= sub["start"] <= end_sec]

    labeled = []
    for sub in subs:
        res = analyze_subtitle(sub["text"], emotion_valence)
        sub.update(res)
        labeled.append(sub)
        time.sleep(2.1)  # API rate 제한

    df = pd.DataFrame(labeled)
    df["valence"] = df["emotions"].apply(calc_valence)

    # 출력 디렉토리가 없는 경우 생성
    Path(out_json).parent.mkdir(parents=True, exist_ok=True)

    Path(out_json).write_text(df.to_json(force_ascii=False, indent=2), encoding='utf-8')
    df.to_csv(out_csv, index=False)
    print(f"[완료] 감정 분석 결과 저장 →\n  JSON: {out_json}\n  CSV:  {out_csv}")
    return df

# 경로 및 실행
srt_path = "/Users/kimdonghyuk/Documents/cinema_analysis_3/new_project/data/raw/Cure_1997_en.srt"
start_time = 109  # 1분 49초
end_time = 349    # 5분 49초
out_json_path = "data/processed/cure_llm_labeled_sample.json"
out_csv_path = "data/processed/cure_llm_labeled_sample.csv"

run_pipeline(srt_path, start_time, end_time, out_json_path, out_csv_path)
