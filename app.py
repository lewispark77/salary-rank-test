import streamlit as st
import requests
import urllib.parse
import os

# ==========================================
# 0. 페이지 설정
# ==========================================
st.set_page_config(page_title="억만장자 계급 테스트", page_icon="🕹️", layout="wide")

# 🌟 레트로 오락실 테마 CSS 주입 (복사 박스 버그 픽스 완료!)
st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/gh/neodgm/neodgm-web-font@1.530/neodgm/style.css');

html, body, [class*="css"]  {
    font-family: 'NeoDunggeunmo', sans-serif !important;
}

.stApp {
    background-color: #1a1a2e;
}

h1, h2, h3, p, span, label, div {
    color: #e0e0e0 !important;
}

div[data-baseweb="input"] > div {
    background-color: #16213e !important;
    border: 2px solid #0f3460 !important;
    border-radius: 0px !important;
}
input {
    color: #00ffcc !important;
    font-family: 'NeoDunggeunmo', sans-serif !important;
}

div.stButton > button {
    background-color: #e94560 !important;
    color: white !important;
    border: 4px solid #fff !important;
    border-radius: 0px !important;
    box-shadow: 4px 4px 0px #0f3460 !important;
    font-size: 1.2rem !important;
    padding: 10px 0px !important;
    transition: all 0.1s !important;
}
div.stButton > button:active {
    transform: translate(4px, 4px) !important;
    box-shadow: 0px 0px 0px #0f3460 !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
}
.stTabs [data-baseweb="tab"] {
    background-color: #16213e !important;
    border-radius: 0px !important;
    border: 2px solid #0f3460 !important;
}
.stTabs [aria-selected="true"] {
    background-color: #e94560 !important;
    border-color: #fff !important;
}

.stAlert {
    background-color: #16213e !important;
    border: 2px solid #e94560 !important;
}

/* 🌟 긴 기업명 줄바꿈 처리 */
[data-testid="stMetricValue"] > div {
    white-space: normal !important;
    word-break: keep-all !important;
    overflow-wrap: break-word !important;
    font-size: 1.4rem !important;
    line-height: 1.3 !important;
}

/* 🌟 픽스: 복사하기 박스(코드 블록) 바탕색 및 글자색 강제 수정 */
[data-testid="stCodeBlock"] {
    background-color: #0f3460 !important;
    border: 2px solid #00ffcc !important;
}
[data-testid="stCodeBlock"] * {
    color: #00ffcc !important;
    background-color: transparent !important;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 백엔드 로직
# ==========================================
def safe_int(value):
    if value is None: return 0
    try: return int(value)
    except (ValueError, TypeError): return 0

def get_billionaire_rank(my_salary, company_avg):
    ratio = my_salary / company_avg
    if ratio >= 3.0: return {"상위": "0.1%", "계급": 1, "칭호": "일론머스크"}
    elif ratio >= 2.0: return {"상위": "1.0%", "계급": 2, "칭호": "만수르"}
    elif ratio >= 1.5: return {"상위": "5.0%", "계급": 3, "칭호": "젠슨 황"}
    elif ratio >= 1.2: return {"상위": "10.0%", "계급": 4, "칭호": "피터 틸"}
    elif ratio >= 1.0: return {"상위": "20.0%", "계급": 5, "칭호": "워렌 버핏"}
    elif ratio >= 0.8: return {"상위": "40.0%", "계급": 6, "칭호": "기숙사 시절 마크 져커버그"}
    elif ratio >= 0.6: return {"상위": "60.0%", "계급": 7, "칭호": "창고시절 제프 베이조스"}
    elif ratio >= 0.5: return {"상위": "75.0%", "계급": 8, "칭호": "차고시절 스티브 잡스"}
    elif ratio >= 0.3: return {"상위": "90.0%", "계급": 9, "칭호": "거절만 당하는 커널 센더스"}
    else: return {"상위": "99.0%", "계급": 10, "칭호": "신문 돌리던 워렌버핏"}

def fetch_company_data(company_name):
    company_name = company_name.upper().strip()
    
    # 🌟 SK 본사 및 텔레콤 등 굵직한 곳 추가!
    vip_mapping = {
        "SK": "에스케이 주식회사",
        "SK텔레콤": "에스케이텔레콤(주)",
        "SK이노베이션": "에스케이이노베이션 주식회사",
        "삼전": "삼성전자(주)",
        "삼성전자": "삼성전자(주)",
        "현대차": "현대자동차(주)",
        "현대자동차": "현대자동차(주)",
        "SK하이닉스": "에스케이하이닉스 주식회사",
        "에스케이하이닉스": "에스케이하이닉스 주식회사",
        "LG전자": "엘지전자(주)",
        "엘지전자": "엘지전자(주)",
        "기아": "기아 주식회사",
        "기아차": "기아 주식회사",
        "카카오": "(주)카카오",
        "네이버": "네이버 주식회사",
        "NAVER": "네이버 주식회사",
        "KT": "주식회사 케이티"
    }
    
    if company_name in vip_mapping:
        company_name = vip_mapping[company_name]
    else:
        eng_to_kor = {"SK": "에스케이", "LG": "엘지", "CJ": "씨제이", "HD": "에이치디", "GS": "지에스", "LS": "엘에스"}
        for eng, kor in eng_to_kor.items():
            company_name = company_name.replace(eng, kor)
            
    api_key = "09e67c3b8c4fd0cf1fdc33661536cfb4a6ba3153269dde7c08e5a4043e7224b3"
    decoded_key = urllib.parse.unquote(api_key)
    bass_url = "https://apis.data.go.kr/B552015/NpsBplcInfoInqireServiceV2/getBassInfoSearchV2"
    detail_url = "https://apis.data.go.kr/B552015/NpsBplcInfoInqireServiceV2/getDetailInfoSearchV2"
    
    all_items = []
    for page in range(1, 6):
        try:
            res1 = requests.get(bass_url, params={"serviceKey": decoded_key, "wkplNm": company_name, "pageNo": str(page), "numOfRows": "20", "dataType": "json"})
            items = res1.json().get('response', {}).get('body', {}).get('items', {}).get('item', [])
            if not items: break
            if type(items) is dict: items = [items]
            all_items.extend(items)
        except: break

    valid_items = [i for i in all_items if not any(w in i.get('wkplNm', '') for w in ["/", "일용", "공사", "현장", "건설"])]
    valid_items.sort(key=lambda x: len(x.get('wkplNm', '')))
    
    best_company = None
    max_emp = 0
    for item in valid_items[:15]: 
        try:
            res2 = requests.get(detail_url, params={"serviceKey": decoded_key, "seq": item.get('seq'), "dataType": "json"})
            detail = res2.json().get('response', {}).get('body', {}).get('items', {}).get('item', [])
            if type(detail) is list and len(detail) > 0: detail = detail[0]
            elif type(detail) is list: continue
            
            emp = safe_int(detail.get('jnngpCnt'))
            amt = safe_int(detail.get('crrmmNtcAmt'))
            if emp > max_emp and amt > 0:
                max_emp = emp
                est_salary = (amt / emp / 0.09) * 12
                best_company = {"기업명": item.get('wkplNm'), "직원수": emp, "평균연봉": est_salary}
        except: continue
    return best_company

def compare_my_salary(company: str, total_salary: int):
    NATIONAL_AVERAGE = 42000000 
    comp_data = fetch_company_data(company)
    
    if not comp_data:
        return {"에러": f"'{company}' 데이터를 찾을 수 없습니다. 오타가 없는지 확인해 주세요."}
        
    company_rank = get_billionaire_rank(total_salary, comp_data["평균연봉"])
    national_rank = get_billionaire_rank(total_salary, NATIONAL_AVERAGE)
    
    app_link = "https://salary-rank-test-8sdapymoyastkizhxfaiy6.streamlit.app"
    
    viral_message = (
        f"💸 [영끌 연봉 억만장자 랭킹전]\n"
        f"나의 원천징수 랭킹은?!\n\n"
        f"🏢 {comp_data['기업명']} 기준: 상위 {company_rank['상위']} ({company_rank['칭호']} 계급)\n"
        f"🇰🇷 전국 직장인 기준: 상위 {national_rank['상위']} ({national_rank['칭호']} 계급)\n\n"
        f"👇 나도 내 랭킹 확인해보기 (상한가 사냥꾼 헤리)\n"
        f"{app_link}"
    )
    
    return {
        "총_연봉": f"{total_salary:,}원",
        "비교_기업명": comp_data["기업명"],
        "기업_평균연봉": f"{int(comp_data['평균연봉']):,}원",
        "전국_평균연봉": f"{NATIONAL_AVERAGE:,}원",
        "회사_결과": company_rank,
        "전국_결과": national_rank,
        "공유_메시지": viral_message
    }

# ==========================================
# 2. 프론트엔드 로직
# ==========================================
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

st.markdown("<h1 style='text-align: center; color: #ffeb3b !important;'>👾 영끌 연봉 억만장자 랭킹전 👾</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>연말정산 원천징수영수증 기준으로 나의 진짜 랭킹을 확인하세요!</p>", unsafe_allow_html=True)
st.divider()

col1, col2 = st.columns(2)
with col1:
    company_input = st.text_input("🏢 기업명 (정확한 법인명)", placeholder="예: 삼전, 현대차, SK")
with col2:
    total_salary_input = st.number_input("💰 원천징수영수증 총액 (원 단위)", min_value=0, step=1000000, value=80000000, format="%d")

st.caption(f"✨ 입력된 나의 영끌 총 연봉: **{total_salary_input:,}원**")

if st.button("🕹️ INSERT COIN : 내 랭킹 확인하기 🕹️", use_container_width=True):
    if not company_input:
        st.warning("기업명을 입력해 주세요!")
    else:
        with st.spinner('국민연금 서버와 통신 중... (데이터 로딩 5~10초)'):
            result = compare_my_salary(company_input, total_salary_input)
            
            if "에러" in result: 
                st.error(result["에러"])
            else: 
                st.success("🎉 스테이지 클리어! 데이터 분석 완료!")
                tab1, tab2 = st.tabs(["🏢 사내 랭킹", "🇰🇷 전국 랭킹"])
                
                with tab1:
                    st.subheader(f"사내에서 당신은 **[{result['회사_결과']['칭호']}]** 계급 (총 10계급 중 {result['회사_결과']['계급']}계급)입니다!")
                    
                    img_path = RANK_IMAGES.get(result['회사_결과']['칭호'])
                    if img_path and os.path.exists(img_path):
                        st.image(img_path, use_container_width=True) 
                    else:
                        st.error(f"⚠️ 이미지를 찾을 수 없습니다: {img_path}")
                        
                    m_col1, m_col2, m_col3 = st.columns(3)
                    m_col1.metric("비교 기업", result['비교_기업명'])
                    m_col2.metric("기업 평균 연봉", result['기업_평균연봉'])
                    m_col3.metric("나의 위치", f"상위 {result['회사_결과']['상위']}")

                with tab2:
                    st.subheader(f"전국 직장인 중 당신은 **[{result['전국_결과']['칭호']}]** 계급 (총 10계급 중 {result['전국_결과']['계급']}계급)입니다!")
                    
                    img_path = RANK_IMAGES.get(result['전국_결과']['칭호'])
                    if img_path and os.path.exists(img_path):
                        st.image(img_path, use_container_width=True)
                    else:
                        st.error(f"⚠️ 이미지를 찾을 수 없습니다: {img_path}")
                        
                    m_col1, m_col2, m_col3 = st.columns(3)
                    m_col1.metric("비교 집단", "전국 직장인")
                    m_col2.metric("전국 평균 연봉", result['전국_평균연봉'])
                    m_col3.metric("나의 위치", f"상위 {result['전국_결과']['상위']}")
                
                st.divider()
                st.markdown("<h3 style='color: #ffeb3b !important;'>💌 친구에게 도전장 보내기 (결과 복사)</h3>", unsafe_allow_html=True)
                st.caption("👇 아래 네모 박스 오른쪽 위에 마우스를 올리면 생기는 **'복사 아이콘(📋)'**을 누르고 카톡에 붙여넣어 보세요!")
                
                # 🌟 보호색 버그 픽스된 코드 블록
                st.code(result['공유_메시지'], language="plaintext")
                st.balloons()
