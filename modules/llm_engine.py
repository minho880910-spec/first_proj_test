import os
from openai import OpenAI
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# OpenAI 클라이언트 인스턴스 생성 (API 키는 .env 파일에서 자동으로 읽어옵니다)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_content(category: str, title: str, tone: str) -> dict:
    """
    사용자의 입력을 받아 OpenAI API를 통해 각 플랫폼별 포스팅 문구를 생성합니다.
    결과는 딕셔너리 형태로 반환됩니다.
    """
    
    # 1. 시스템 페르소나 및 지시사항 설정
    system_prompt = f"""
    당신은 10년 차 베테랑 디지털 마케터입니다. 
    가장 중요한 것은 사용자가 요구한 톤앤매너인 '{tone}' 스타일을 글 전체에 200% 반영하는 것입니다. 
    단순한 마케팅 문구가 아니라, 선택된 톤에 맞춰 어투와 단어 선택을 완벽하게 바꾸세요.
    
    [톤앤매너 집중 가이드]
    - '전문적인': 격식 있고 신뢰감 있는 어조. 정확한 정보와 장점을 논리적으로 설명. (예: ~입니다, ~을 권장합니다)
    - '친근한': 친밀하고 다정한 어조. 편안하게 대화하듯 작성. (예: ~했어요!, ~어때요? ㅎㅎ)
    - '유머러스한': 요즘 유행어, 재치 있는 비유, 오버스러운 표현을 적극 활용해 빵 터지는 어조. (예: ~안 사면 유죄, 폼 미쳤다)
    - '감성적인': 시적이고 감각적인 단어, 분위기를 자극하는 부드럽고 여운이 남는 어조.
    
    현재 요구된 톤앤매너는 '{tone}'입니다. 다른 톤은 무시하고 오직 '{tone}'에만 완벽하게 몰입하십시오.
    
    [플랫폼별 작성 가이드]
    - Instagram: 이모지 활용, 줄바꿈을 적극적으로 사용하여 가독성 높이기, 시각적 상상력 자극, 해시태그 포함.
    - Threads: 텍스트 중심, 여러 줄로 나누어(줄바꿈 활용) 짧은 호흡으로 가볍게 소통하듯 작성.
    - X (Twitter): 280자 이내로 빠르고 간결하게 핵심 키워드 전달, 줄바꿈으로 깔끔하게 정리.
    
    *주의*: 모든 문구를 한 줄로 뭉쳐 쓰지 말고, 문단이나 문장이 넘어갈 때마다 반드시 엔터(줄바꿈)를 넣어 읽기 편하게 만드세요.
    
    각 플랫폼별 결과물을 명확하게 구분하여 출력해 주십시오. (예: Instagram: \n ...)
    """

    user_prompt = f"카테고리: {category}\n제품 및 제목: {title}\n요구 톤앤매너: {tone}\n\n위 조건에 맞춰서, 반드시 '{tone}' 느낌이 확실하게 드러나도록 3가지 플랫폼의 포스팅 문구를 작성해 주세요."

    # 2. OpenAI API 호출
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # 필요에 따라 gpt-4o 등으로 변경 가능
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7 # 적절한 창의성을 위한 수치 설정
    )

    full_text = response.choices[0].message.content

    # 3. 텍스트 분리 로직 (임시 파싱)
    # 실제 실무에서는 JSON 구조화(Function Calling 등)를 사용하지만, 
    # 직관적인 이해를 위해 텍스트 스플릿 방식을 우선 적용합니다.
    # LLM이 "Instagram:", "Threads:", "X:" 등의 키워드를 포함하여 답변한다는 전제가 필요합니다.
    
    ig_content = ""
    th_content = ""
    x_content = ""

    # 모델의 출력 패턴에 따라 유동적으로 작동하는 기본 파싱 로직입니다.
    sections = full_text.split('\n\n')
    current_platform = "instagram"
    
    for section in sections:
        section_lower = section.lower()
        if "instagram" in section_lower:
            current_platform = "instagram"
            ig_content += section + "\n\n"
        elif "threads" in section_lower:
            current_platform = "threads"
            th_content += section + "\n\n"
        elif "x" in section_lower or "twitter" in section_lower:
            current_platform = "x"
            x_content += section + "\n\n"
        else:
            # 플랫폼 키워드가 명시되지 않은 단락은 현재 활성화된 플랫폼에 추가합니다.
            if current_platform == "instagram": ig_content += section + "\n\n"
            elif current_platform == "threads": th_content += section + "\n\n"
            elif current_platform == "x": x_content += section + "\n\n"

    # 만약 파싱이 완벽하지 않아 텍스트가 한 곳으로 쏠릴 경우를 대비한 최소한의 에러 핸들링입니다.
    if not th_content and not x_content:
        ig_content = full_text # 분리에 실패하면 인스타그램 탭에 전체 텍스트를 모두 밀어 넣습니다.

    return {
        "instagram": ig_content.strip(),
        "threads": th_content.strip(),
        "x": x_content.strip()
    }