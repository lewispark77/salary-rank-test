from fastapi import FastAPI
import requests
import urllib.parse

app = FastAPI()

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
    company_name = company_name.upper() 
    
    # 🌟 하드코딩 치트키: 공사현장 스팸을 뚫고 진짜 본사로 직행!
    name_mapping = {
        "SK하이닉스": "에스케이하이닉스 주식회사",
        "SK": "에스케이",
        "LG": "엘지",
        "KT": "케이티",
        "CJ": "씨제이",
        "HD": "에이치디",
        "GS": "지에스",
        "LS": "엘에스"
    }
    
    for eng, kor in name_mapping.items():
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
        except Exception:
            break

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
        except Exception:
            continue
            
    return best_company

@app.get("/api/rank")
def compare_my_salary(company: str, salary: int, bonus: int = 0):
    NATIONAL_AVERAGE = 42000000 
    
    total_salary = salary + bonus 
    
    comp_data = fetch_company_data(company)
    
    if not comp_data:
        return {"메시지": f"'{company}' 데이터를 찾을 수 없습니다. 정확한 법인명(예: 삼성전자(주))을 입력해 주세요."}
        
    company_rank = get_billionaire_rank(total_salary, comp_data["평균연봉"])
    national_rank = get_billionaire_rank(total_salary, NATIONAL_AVERAGE)
    
    return {
        "기본급": f"{salary:,}원",
        "성과금": f"{bonus:,}원",
        "총_연봉": f"{total_salary:,}원",
        "비교_기업명": comp_data["기업명"],
        "기업_평균연봉": f"{int(comp_data['평균연봉']):,}원",
        "전국_평균연봉": f"{NATIONAL_AVERAGE:,}원",
        "회사_결과": company_rank,
        "전국_결과": national_rank,
        "공유_메시지": f"나의 영끌 연봉은 {total_salary:,}원! {comp_data['기업명']} 기준 상위 {company_rank['상위']}! 전국 직장인 중에서는 상위 {national_rank['상위']}입니다."
    }