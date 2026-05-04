import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_ai_json(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except:
        return None

def get_comprehensive_analysis(keyword, category_name):
    """구글 지역, FAQ, SNS 반응 및 인구통계 비중을 한 번에 생성"""
    prompt = f"""
    키워드 '{keyword}'와 카테고리 '{category_name}' 분석 JSON 생성.
    형식:
    {{
      "region_ranking": [{{"region": "서울", "score": 100}}],
      "faqs": ["질문1", "질문2"],
      "hot_discussions": [{{"title": "제목", "replies": 10}}],
      "top_influencers": [{{"name": "이름", "handle": "@id"}}],
      "x_sentiment": {{"sentiment_stats": [60, 20, 15, 5], "emotional_words": ["기대"], "satisfaction_score": 80, "tips": []}},
      "demographics": {{"device": {{"mo": 70, "pc": 30}}, "gender": {{"f": 50, "m": 50}}, "age": {{"10": 10, "20": 20, "30": 30, "40": 20, "50": 15, "60": 5}}}}
    }}
    """
    return generate_ai_json(prompt)