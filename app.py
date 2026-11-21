import streamlit as st
from google import genai
from google.genai import types

# --- 🎨 웹사이트 디자인 (CSS) 적용 ---
st.set_page_config(page_title="고전문학 유니버스", page_icon="📜", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;700&display=swap');
* { font-family: 'Noto Serif KR', serif !important; }
[data-testid="stAppViewContainer"], [data-testid="stHeader"] { background-color: #f4f1ea; }
.stMarkdown, .stText, h1, h2, h3, label, p { color: #3e3a35 !important; }
div.stButton > button:first-child { background-color: #5d4037; color: #f9f8f4 !important; border: 2px solid #3e2723; border-radius: 4px; }
div.stButton > button:first-child:hover { background-color: #3e2723; border: 2px solid #1b0000; }
.stTextInput>div>div>input { background-color: #fdfdfc; border: 1px solid #d7ccc8; }
</style>
""", unsafe_allow_html=True)

# --- ⚙️ API 설정 ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    else:
        api_key = "여기에_본인의_API_키를_직접_넣어도_됩니다"
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error("API 키가 설정되지 않았습니다. secrets.toml 파일을 확인해주세요.")

if "step" not in st.session_state:
    st.session_state.step = 1
if "summary_result" not in st.session_state:
    st.session_state.summary_result = ""

def reset_app():
    st.session_state.step = 1
    st.session_state.summary_result = ""
    st.session_state.title = ""
    st.session_state.mode = ""
    st.rerun()

if st.session_state.step == 1:
    st.title("📜 한일 고전문학 스토리 초고속 변환기")
    st.markdown("원작의 줄거리 틀은 유지하되, 결말만 선택한 문화의 문법으로 바꿉니다.")

    st.write("---")
    mode = st.radio("🔄 변환 방향 선택", ("일본 고전 ➡️ 한국 고전", "한국 고전 ➡️ 일본 고전"))
    title_input = st.text_input("📖 원작 제목 입력 (예: 우라시마 타로, 심청전 등)")

    if st.button("결말 각색 및 변환 시작하기 ➡️", use_container_width=True):
        if not title_input.strip():
            st.warning("작품 제목을 입력해 주세요.")
        else:
            clean_title = title_input.strip()
            is_to_jp = mode.endswith("일본 고전")

            with st.spinner(f"⏳ '{clean_title}'의 결말을 {'일본 고전' if is_to_jp else '한국 고전'} 문법으로 바꾸는 중입니다..."):
                try:
                    if is_to_jp:
                        sys_inst = (
                            "당신은 일본 고전문학 문법 전문가입니다. "
                            "반드시 일본 고전 미학(모노 노 아와레, 무상관, 덧없음, 체념과 쓸쓸한 여운)으로만 결말을 각색하세요. "
                            "권선징악이나 통쾌한 해피엔딩 같은 한국 고전소설식 결말은 절대 사용하지 마세요."
                        )
                        ending_guide = (
                            "결말은 권선징악이나 해피엔딩이 아니라, 덧없음과 무상함, "
                            "그리고 조용하고 쓸쓸한 여운이 남는 일본 고전 스타일로 바꾸세요."
                        )
                    else:
                        sys_inst = (
                            "당신은 한국 고전소설 문법 전문가입니다. "
                            "반드시 한국 고전소설 특징(권선징악, 인과응보, 뚜렷한 보상과 해피엔딩)으로만 결말을 각색하세요. "
                            "허무한 체념이나 쓸쓸한 비극적 여운만 남기는 결말은 피하세요."
                        )
                        ending_guide = (
                            "결말은 권선징악과 인과응보가 살아있는 한국 고전소설 스타일(명쾌한 해피엔딩 또는 교훈적 보상)로 바꾸세요."
                        )

                    prompt = f"""작품명: {clean_title}

1. 원작 '{clean_title}'의 초반~중반 줄거리 틀과 핵심 사건은 그대로 유지하세요.
2. {ending_guide}
3. 인사말이나 서론은 쓰지 말고, 바로 아래 두 소제목으로만 답하세요.

### 1. 결말 각색 핵심 줄거리
(도입·전개는 원작 흐름을 따르고, 바뀐 결말이 잘 드러나게 3~4문단으로 요약)

### 2. 결말 변화 비교 해설
(원래 결말과 바뀐 결말의 차이를 정서·인물 태도·결말 의미 중심으로 2~3문단 설명)"""

                    response = client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=sys_inst,
                            temperature=0.7,
                            max_output_tokens=3000,
                        ),
                    )

                    st.session_state.title = clean_title
                    st.session_state.mode = mode
                    st.session_state.summary_result = (response.text or "").strip()

                    st.session_state.step = 2
                    st.rerun()

                except Exception as e:
                    st.error(f"변환 중 오류가 발생했습니다. 상세 에러: {e}")

elif st.session_state.step == 2:
    st.title("✨ 결말이 각색된 고전 요약 및 해설")
    st.markdown(f"**원작:** {st.session_state.title} | **방향:** {st.session_state.mode}")

    st.write("---")
    if st.session_state.summary_result:
        st.markdown(st.session_state.summary_result)
    else:
        st.warning("생성된 본문이 비어 있습니다. 다시 시도해 주세요.")

    st.write("---")
    if st.button("처음으로 돌아가기 🔄", use_container_width=True):
        reset_app()