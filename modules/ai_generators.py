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
    prompt = f"""
    키워드 '{keyword}'와 카테고리 '{category_name}' 분석 JSON 생성.
    반드시 아래의 키 명칭을 엄수할 것:
    {{
      "region_ranking": [{{"region": "서울", "score": 100}}],
      "faqs": ["질문1", "질문2"],
      "hot_discussions": [
        {{"title": "제목", "replies": 10, "quotes": 5}} 
      ],
      "top_influencers": [
        {{"name": "이름", "handle": "@아이디"}} 
      ],
      "x_sentiment": {{ ... }},
      "demographics": {{ ... }}
    }}
    """
    return generate_ai_json(prompt)