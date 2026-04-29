import os
from openai import OpenAI
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# OpenAI 클라이언트 인스턴스 생성
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_keyword(prompt_text: str) -> str:
    """
    사용자의 전체 프롬프트 입력에서 트렌드 분석용 핵심 키워드만 추출합니다.
    """
    if not prompt_text or not prompt_text.strip():
        return ""
        
    system_prompt = (
        "당신은 소상공인이 작성한 홍보/안내 문구에서 '메인 판매 상품 및 서비스'의 핵심 키워드를 추출하는 전문가입니다.\n"
        "사용자의 입력 문장에서 소상공인이 주로 팔려고 하거나 홍보하려는 핵심 제품명, 메뉴명, 또는 서비스명만 추출하세요.\n"
        "마케팅 수식어(신선한, 맛있는, 예쁜 등)나 부가적인 설명은 모두 제거하고 오직 '무엇을 파는가'에 해당하는 본질적인 명사형 키워드만 반환해야 합니다.\n"
        "예시 1) 사용자: 오늘 잡은 광어와 연어로 만든 신선한 회덮밥 드시러 오세요 -> 답변: 회덮밥\n"
        "예시 2) 사용자: 봄에 입기 좋은 화사한 파스텔톤 린넨 셔츠 신상 입고되었습니다! -> 답변: 린넨 셔츠\n"
        "예시 3) 사용자: 우리 동네 최고 가성비 헬스장, PT 10회권 할인 이벤트 중! -> 답변: 헬스장 PT\n"
        "예시 4) 사용자: 100% 유기농 밀가루로 구운 담백한 소금빵이 갓 나왔어요 -> 답변: 소금빵\n"
        "반드시 키워드 하나(또는 2~3어절 짧은 명사구)만 출력하며, 마침표나 추가 설명은 절대 붙이지 마세요."
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_text}
            ],
            temperature=0.1
        )
        keyword = response.choices[0].message.content.strip()
        # 혹시 모를 따옴표나 마침표 제거
        keyword = keyword.replace('"', '').replace("'", "").rstrip('.')
        return keyword
    except Exception as e:
        print(f"Keyword extraction error: {e}")
        # 오류 발생 시 원본 텍스트가 너무 길면 잘라서 반환
        return prompt_text[:15].strip()
