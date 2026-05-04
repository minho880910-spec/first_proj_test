import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_ai_json(prompt):
    """OpenAI API를 통해 구조화된 JSON 데이터를 생성하는 공통 유틸리티"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"AI JSON Generation Error: {e}")
        return None

def get_google_tab_ai_data(keyword):
    """Google 탭 전용: 전국 지역별 관심도와 FAQ 생성"""
    prompt = f"""
    키워드 '{keyword}'에 대한 한국 트렌드 분석 JSON을 생성해줘. 
    {{
      "region_ranking": [
        {{"region": "서울", "score": 100}},
        {{"region": "경기", "score": 85}},
        {{"region": "부산", "score": 70}},
        {{"region": "인천", "score": 60}},
        {{"region": "대구", "score": 50}}
      ],
      "faqs": ["질문1", "질문2", "질문3", "질문4", "질문5"]
    }}
    """
    data = generate_ai_json(prompt)
    if data and "region_ranking" in data and "faqs" in data:
        return data
    return {
        "region_ranking": [{"region": "서울", "score": 100}], 
        "faqs": [f"{keyword}의 주요 특징은?", f"{keyword} 관련 가장 인기 있는 정보는?"]
    }

def get_naver_tab_ai_data(keyword, category_name):
    """Naver 탭 전용: 기기/성별/연령별 인구통계 비중 생성"""
    prompt = f"""
    키워드 '{keyword}'와 카테고리 '{category_name}'의 한국 내 검색 사용자 비중 JSON 생성.
    {{
      "demographics": {{
        "device": {{"mo": 75, "pc": 25}},
        "gender": {{"f": 55, "m": 45}},
        "age": {{"10": 10, "20": 25, "30": 30, "40": 20, "50": 10, "60": 5}}
      }}
    }}
    """
    data = generate_ai_json(prompt)
    # demographics 키가 있고 그 안에 필수 하위 키들이 있는지 확인
    if data and "demographics" in data:
        demo = data["demographics"]
        if all(k in demo for k in ["device", "gender", "age"]):
            return data
    return {
        "demographics": {
            "device": {"mo": 70, "pc": 30}, 
            "gender": {"f": 50, "m": 50}, 
            "age": {"20": 40, "30": 60}
        }
    }

def get_instagram_tab_ai_data(keyword, category_name):
    """Instagram 탭 전용: 해시태그를 제외한 미디어/성별/연령 비중 데이터만 생성"""
    prompt = f"""
    키워드 '{keyword}'와 인스타그램 카테고리 '{category_name}' 분석 JSON 생성.
    해시태그 데이터는 제외하고, 오직 아래의 인구통계 비중만 생성할 것:
    {{
      "demographics": {{
        "media_type": {{"image": 40, "video": 50, "carousel": 10}},
        "gender": {{"f": 60, "m": 40}},
        "age": {{"10": 15, "20": 35, "30": 25, "40": 15, "50": 10}}
      }}
    }}
    """
    data = generate_ai_json(prompt)
    if data and "demographics" in data:
        demo = data["demographics"]
        if all(k in demo for k in ["media_type", "gender", "age"]):
            return data
    return {
        "demographics": {
            "media_type": {"image": 40, "video": 40, "carousel": 20},
            "gender": {"f": 50, "m": 50},
            "age": {"20": 50, "30": 50}
        }
    }

def get_threads_tab_ai_data(keyword):
    """Threads 탭 전용: 텍스트 중심의 대화 및 인플루언서 분석"""
    prompt = f"""
    키워드 '{keyword}'에 대한 Threads(스레드) 반응 분석 JSON 생성.
    {{
      "hot_discussions": [
        {{"title": "핫토픽", "replies": 100, "quotes": 50, "handle": "@user", "author": "이름", "content": "내용"}}
      ],
      "top_influencers": [
        {{"rank": 1, "handle": "@id", "name": "이름", "mentions": 100, "followers": "10K"}}
      ]
    }}
    """
    data = generate_ai_json(prompt)
    if data and "hot_discussions" in data and "top_influencers" in data:
        return data
    return {"hot_discussions": [], "top_influencers": []}

def get_x_tab_ai_data(keyword):
    """X(Twitter) 탭 전용: 실시간성 분석 및 감성/꿀팁 데이터 생성"""
    prompt = f"""
    키워드 '{keyword}'에 대한 X(트위터) 실시간 반응 분석 JSON을 생성해줘.
    
    [중요 지시사항]
    1. 'emotional_words' 배열에는 '{keyword}'의 실제 유저 반응(장단점, 특징, 감정)을 10개 채울 것.
    2. 'tips' 배열에는 키워드가 제품이든, 생물이든, 장소든 상관없이 해당 키워드 성격에 맞는 '유저들의 꿀팁/노하우/관련 정보'를 무조건 3개 이상 생성할 것. (예: 강아지 -> 양육/훈련 팁, 장소 -> 방문 꿀팁 등)

    {{
      "hot_discussions": [
        {{
          "title": "실시간 트렌드 토픽",
          "replies": 150,
          "quotes": 80,
          "handle": "@trend_searcher",
          "author": "트렌드분석가",
          "content": "실제 트위터에서 논의되는 '{keyword}' 관련 내용을 요약해서 작성"
        }}
      ],
      "x_sentiment": {{
        "sentiment_stats": [60, 20, 15, 5],
        "emotional_words": ["단어1", "단어2", "단어3", "단어4", "단어5", "단어6", "단어7", "단어8", "단어9", "단어10"],
        "satisfaction_score": 85,
        "tips": [
          {{
            "title": "키워드 맞춤 노하우 1",
            "highlight": "핵심 한 줄 요약",
            "desc": "구체적인 팁 설명"
          }},
          {{
            "title": "키워드 맞춤 노하우 2",
            "highlight": "놓치기 쉬운 포인트",
            "desc": "유저들이 자주 공유하는 정보"
          }}
        ]
      }}
    }}
    """
    
    data = generate_ai_json(prompt)
    
    # 데이터 검증: tips가 아예 비어있는 리스트([])로 올 경우까지 완벽 차단
    if not data or "x_sentiment" not in data or not data["x_sentiment"].get("tips"):
        return {
            "hot_discussions": [],
            "x_sentiment": {
                "sentiment_stats": [40, 30, 20, 10],
                "emotional_words": [f"{keyword}리뷰", "정보", "꿀팁", "이슈", "반응", "특징", "추천", "공유", "실시간", "트렌드"],
                "satisfaction_score": 80,
                "tips": [
                    {
                        "title": "데이터 분석 지연", 
                        "highlight": f"'{keyword}' 정보 수집 중", 
                        "desc": "실시간 트렌드 데이터를 처리하고 있습니다. 잠시만 기다려주세요."
                    }
                ]
            }
        }
    return data