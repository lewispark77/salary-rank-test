import streamlit as st
import requests
import os

st.set_page_config(page_title="억만장자 계급 테스트", page_icon="💸", layout="wide") # 화면을 넓게 쓰도록 변경

IMAGE_DIR = "images"

RANK_IMAGES = {
    "일론머스크": f"{IMAGE_DIR}/1계급 일론머스크.jpg",
    "만수르": f"{IMAGE_DIR}/2계급 만수르.jpg",
    "젠슨 황": f"{IMAGE_DIR}/3계급 젠슨 황.jpg",
    "피터 틸": f"{IMAGE_DIR}/4계급 피터 틸.jpg",
    "워렌 버핏": f"{IMAGE_DIR}/5계급 워렌 버핏.jpg",
    "기숙사 시절 마크 져커버그": f"{IMAGE_DIR}/6계급 기숙사 시절 마크 져커버그.jpg",
    "창고시절 제프 베이조스": f"{IMAGE_DIR}/7계급 창고시절 제프 베이조스.jpg",
    "차고시절 스티브 잡스": f"{IMAGE_DIR}/8계급 차고시절 스티브 잡스.jpg",
    "거절만 당하는 커널 센더스": f"{IMAGE_DIR}/9계급 거절만 당하는 커널 센더스.jpg",
    "신문 돌리던 워렌버핏": f"{IMAGE_DIR}/10계급 신문 돌리던 워렌버핏.jpg"
}

st.title("💸 내 영끌 연봉은 억만장자 계급으로 몇 등급일까?")
st.markdown("기본급에 성과금까지 모두 합친 '영끌 연봉'으로 진짜 내 위치를 확인해 보세요!")
st.divider()

# 🌟 입력칸을 3개로 나누었습니다.
col1, col2, col3 = st.columns(3)
with col1:
    company_input = st.text_input("🏢 기업명 (정확한 법인명)", placeholder="예: 삼성전자(주)")
with col2:
    salary_input = st.number_input("💰 계약 기본급 (원 단위)", min_value=0, step=1000000, value=60000000, format="%d")
with col3:
    bonus_input = st.number_input("💵 영끌 성과금 (원 단위)", min_value=0, step=1000000, value=20000000, format="%d")

# 입력하자마자 총액이 보이게 팁 추가
st.caption(f"✨ 합산된 영끌 총 연봉: **{salary_input + bonus_input:,}원**")

# API 호출 시 bonus 값도 같이 넘겨줍니다!
if st.button("🚀 내 계급 확인하기", use_container_width=True):
    if not company_input:
        st.warning("기업명을 입력해 주세요!")
    else:
        with st.spinner('국민연금 빅데이터를 분석 중입니다... (약 5~10초 소요)'):
            api_url = f"http://127.0.0.1:8000/api/rank?company={company_input}&salary={salary_input}&bonus={bonus_input}"
            
            try:
                response = requests.get(api_url)
                result = response.json()
                
                if "메시지" in result: 
                    st.error(result["메시지"])
                else: 
                    st.success("🎉 분석 완료!")
                    
                    tab1, tab2 = st.tabs(["🏢 사내 연봉 계급", "🇰🇷 전국 직장인 계급"])
                    
                    with tab1:
                        st.subheader(f"사내에서 당신은 **[{result['회사_결과']['칭호']}]** 계급입니다!")
                        
                        img_path = RANK_IMAGES.get(result['회사_결과']['칭호'])
                        if img_path and os.path.exists(img_path):
                            st.image(img_path, use_container_width=True) 
                        else:
                            st.error(f"⚠️ 이미지를 찾을 수 없습니다: {img_path}")
                            
                        m_col1, m_col2, m_col3 = st.columns(3)
                        m_col1.metric("비교 기업", result['비교_기업명'])
                        m_col2.metric("기업 평균연봉", result['기업_평균연봉'])
                        m_col3.metric("사내 나의 위치", f"상위 {result['회사_결과']['상위']}")

                    with tab2:
                        st.subheader(f"전국 직장인 중 당신은 **[{result['전국_결과']['칭호']}]** 계급입니다!")
                        
                        img_path = RANK_IMAGES.get(result['전국_결과']['칭호'])
                        if img_path and os.path.exists(img_path):
                            st.image(img_path, use_container_width=True)
                        else:
                            st.error(f"⚠️ 이미지를 찾을 수 없습니다: {img_path}")
                            
                        m_col1, m_col2, m_col3 = st.columns(3)
                        m_col1.metric("비교 집단", "전국 직장인")
                        m_col2.metric("전국 평균연봉", result['전국_평균연봉'])
                        m_col3.metric("전국 나의 위치", f"상위 {result['전국_결과']['상위']}")
                    
                    st.divider()
                    st.info(f"💌 내 결과 공유하기: {result['공유_메시지']}")
                    st.balloons()
                    
            except Exception as e:
                st.error("서버와 연결할 수 없습니다. FastAPI 서버가 켜져 있는지 확인해 주세요!")