import streamlit as st
import requests
import urllib.parse
import os

# ==========================================
# 0. 페이지 설정 (반드시 최상단에 위치)
# ==========================================
st.set_page_config(page_title="억만장자 계급 테스트", page_icon="🕹️", layout="wide")

# 🌟 레트로 오락실 테마 CSS 주입
st.markdown("""
<style>
/* 한국어 레트로 픽셀 폰트 (둥근모꼴) 불러오기 */
@import url('https://cdn.jsdelivr.net/gh/neodgm/neodgm-web-font@1.530/neodgm/style.css');

html, body, [class*="css"]  {
    font-family: 'NeoDunggeunmo', sans-serif !important;
}

/* 전체 배경을 어두운 오락실 느낌(다크 네이비)으로 */
.stApp {
    background-color: #1a1a2e;
}

/* 텍스트 색상을 레트로한 밝은 회색/흰색으로 강제 변경 */
h1, h2, h3, p, span, label, div {
    color: #e0e0e0 !important;
}

/* 입력창 디자인 (다크 톤 + 네온 민트 글씨) */
div[data-baseweb="input"] > div {
    background-color: #16213e !important;
    border: 2px solid #0f3460 !important;
    border-radius: 0px !important;
}
input {
    color: #00ffcc !important;
    font-family: 'NeoDunggeunmo', sans-serif !important;
}

/* 🚀 대망의 시작 버튼 (오락실 붉은색 버튼 디자인) */
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

/* 탭 디자인 수정 */
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

/* 성공/에러 알림창 색상 조정 */
.stAlert {
    background-color: #16213e !important;
    border: 2px solid #e94560 !important;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 백엔드 로직 (데이터 수집 및 계산)
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
    
    vip_mapping = {
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

def compare_my_salary(company: str, salary: int, bonus: int = 0):
    NATIONAL_AVERAGE = 42000000 
    total_salary = salary + bonus 
    comp_data = fetch_company_data(company)
    
    if not comp_data:
        return {"에러": f"
