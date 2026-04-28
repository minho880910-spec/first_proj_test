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
    system_prompt = """
    당신은 10년 차 베테랑 디지털 마케터입니다. 
    제시된 카테고리와 제품(제목), 그리고 요구하는 톤앤매너에 맞추어 
    인스타그램(Instagram), 스레드(Threads), 엑스(X, 구 트위터) 각각의 플랫폼 특성에 완벽하게 최적화된 마케팅 포스팅 문구를 작성해야 합니다.
    
    [플랫폼별 작성 가이드]
    - Instagram: 시각적인 상상을 자극하는 감성적인 문구와 이모지 적극 활용, 해시태그 포함.
    - Threads: 텍스트 중심의 소통, 트렌디하고 가벼운 구어체 사용.
    - X (Twitter): 280자 이내의 빠르고 간결한 정보 전달, 핵심 키워드 강조.
    
    각 플랫폼별 결과물을 명확하게 구분하여 출력해 주십시오.
    """

    user_prompt = f"카테고리: {category}\n제품 및 제목: {title}\n요구 톤앤매너: {tone}\n\n위 조건에 맞는 3가지 플랫폼의 포스팅 문구를 작성해 주세요."

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