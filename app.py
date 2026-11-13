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
div.stDownloadButton > button:first-child { background-color: #3e2723; color: #f9f8f4 !important; border: 2px solid #1b0000; border-radius: 4px; }
.stTextInput>div>div>input { background-color: #fdfdfc; border: 1px solid #d7ccc8; }
.story-box { background-color: #fffdf9; padding: 30px; border: 1px solid #d7ccc8; border-radius: 8px; line-height: 2.0; font-size: 1.1rem; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
.explanation-box { background-color: #f0ebe1; padding: 25px; border-left: 5px solid #5d4037; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- ⚙️ API 설정 ---
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error("API 키가 설정되지 않았습니다. 관리자(서버) 설정을 확인해주세요.")

if 'step' not in st.session_state:
    st.session_state.step = 1

def reset_app():
    st.session_state.step = 1
    st.rerun()

def call_gemini(prompt, system_instruction, temperature, max_tokens=3000):
    # 구글 안내에 따른 최신 모델명 적용
    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
    )
    return response.text

RULES = {
    "KR": {
        "system": "당신은 일본 고전문학을 조선시대 한국 고전소설 문법(적강, 권선징악, 해학과 풍자)으로 재창조하는 전문가입니다.",
        "step2": "- 적강 모티프, 외부 사회적 갈등, 익살스러운 조력자, 완벽한 권선징악과 해피엔딩 적용",
        "step3": "- 전지적 작가 시점, 판소리계 예스러운 산문체(~하였더라), 작가 개입, 해학적 분위기"
    },
    "JP": {
        "system": "당신은 한국 고전문학을 일본 헤이안 시대 귀족 문학 문법(모노 노 아와레, 수동적 인물, 무상관)으로 재창조하는 전문가입니다.",
        "step2": "- 내면적 고뇌, 운명 순응, 비극적 여운, 정서적 교류 중심으로 서사 개조",
        "step3": "- 정적인 분위기, 계절과 자연물 묘사, 감정이 고조될 때 '와카(전통 시)' 삽입, 쓸쓸한 결말"
    }
}

def create_download_text():
    return f"【 원작: {st.session_state.title} | {st.session_state.mode} 】\n\n=== ✨ 새롭게 엮은 이야기 ===\n\n{st.session_state.final_story}\n\n\n=== 💡 작품 해설 ===\n\n{st.session_state.explanation}\n"

if st.session_state.step == 1:
    st.title("📜 한일 고전문학 스토리 변환기")
    st.markdown("어느 나라의 문법으로 이야기를 다시 지어볼까요? 변환할 방향과 원작 제목을 입력해 주십시오.")
    
    st.write("---")
    mode = st.radio("🔄 변환 방향 선택", ("일본 고전 ➡️ 한국 고전", "한국 고전 ➡️ 일본 고전"))
    title_input = st.text_input("📖 원작 제목 입력 (예: 우라시마 타로, 춘향전 등)")
    
    if st.button("이야기 변환 시작하기 ➡️", use_container_width=True):
        if not title_input:
            st.warning("작품 제목을 입력해 주세요.")
        else:
            target_lang = "KR" if "한국 고전" in mode else "JP"
            current_rule = RULES[target_lang]
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                status_text.write("⏳ 원작 줄거리를 떠올리는 중입니다...")
                summary = call_gemini(f"고전 '{title_input}'의 전체 줄거리 요약", "문학 백과사전", 0.2, 1000)
                progress_bar.progress(20)

                status_text.write("⏳ 원작의 특징을 해체하는 중입니다...")
                analysis = call_gemini(f"다음 줄거리에서 주인공 성향, 갈등, 결말, 상징을 추출하세요.\n{summary}", current_rule["system"], 0.1, 1000)
                progress_bar.progress(40)

                status_text.write("⏳ 새로운 문화의 서사로 플롯을 엮는 중입니다...")
                plot = call_gemini(f"다음 규칙으로 플롯 개요를 짜주세요.\n[규칙]: {current_rule['step2']}\n[데이터]: {analysis}", current_rule["system"], 0.7, 1500)
                progress_bar.progress(60)

                status_text.write("⏳ 새로운 문체로 소설을 집필하는 중입니다...")
                final_story = call_gemini(f"플롯을 바탕으로 소설을 쓰세요.\n[규칙]: {current_rule['step3']}\n[플롯]: {plot}", current_rule["system"], 0.9, 4000)
                progress_bar.progress(80)
                
                status_text.write("⏳ 작품 해설을 정리하는 중입니다...")
                explain_prompt = f"당신은 문학 평론가입니다. 앞서 변환한 작업을 바탕으로 해설을 작성해주세요.\n원작이 가졌던 문화적 특징(성향, 갈등, 결말)이 무엇이었고, 그것을 대상 문화의 어떤 특징으로 어떻게 바꾸었는지 구체적으로 비교 설명해주세요.\n[원본 분석]: {analysis}\n[변환 플롯]: {plot}"
                explanation = call_gemini(explain_prompt, "문학 평론가", 0.7, 2000)
                progress_bar.progress(100)
                status_text.write("✨ 집필이 완료되었습니다!")
                
                st.session_state.title = title_input
                st.session_state.mode = mode
                st.session_state.final_story = final_story
                st.session_state.explanation = explanation
                
                st.session_state.step = 2
                st.rerun()

            except Exception as e:
                st.error(f"이야기를 변환하는 중에 오류가 발생했습니다. 상세 에러: {e}")

elif st.session_state.step == 2:
    st.title(f"✨ 새롭게 엮은 이야기")
    st.markdown(f"**원작:** {st.session_state.title} | **방향:** {st.session_state.mode}")
    
    st.markdown(f"<div class='story-box'>{st.session_state.final_story}</div>", unsafe_allow_html=True)
    
    st.write("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("작품 해설 보기 ➡️", use_container_width=True):
            st.session_state.step = 3
            st.rerun()
    with col2:
        st.download_button("텍스트 파일로 저장 💾", create_download_text(), f"{st.session_state.title}_변환결과.txt", "text/plain", use_container_width=True)
    with col3:
        if st.button("처음으로 돌아가기 🔄", use_container_width=True):
            reset_app()

elif st.session_state.step == 3:
    st.title("💡 두 문화의 교차점: 작품 해설")
    st.markdown("AI 평론가가 분석한 원작과 변환된 작품의 서사적/문화적 차이입니다.")
    
    st.markdown(f"<div class='explanation-box'>{st.session_state.explanation}</div>", unsafe_allow_html=True)
    
    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("텍스트 파일로 저장 💾", create_download_text(), f"{st.session_state.title}_변환결과.txt", "text/plain", use_container_width=True)
    with col2:
        if st.button("처음으로 돌아가기 🔄", use_container_width=True):
            reset_app()
