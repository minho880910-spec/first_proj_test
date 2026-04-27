# 프로젝트 첫 실행 법

### 1. 가상환경을 만든다
`python -m venv .venv`

### 2. 가상환경 진입 후 패키지를 설치한다.
`.venv\Scripts\activate`
`pip install streamlit python-dotenv openai pandas numpy`
- 추후에 설치 패키지는 수정하겠습니다.
- 아니면 requirements.txt를 만들겠습니다.

### 3. .env파일을 만든다
파일을 만든 후 
`OPENAI_API_KEY = "자신의 OPENAI API KEY"`
위 내용 작성