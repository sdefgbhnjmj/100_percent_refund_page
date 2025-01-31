from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta
import requests

app = Flask(__name__, static_folder="C:/Users/apf_temp_admin/Desktop/python/100% 환불 페이지/static", static_url_path="/static")

# Access Token 가져오는 함수
def get_access_token():
    url = 'https://auth.tracker.delivery/oauth2/token'
    payload = {
        'grant_type': 'client_credentials',
        'client_id': '5e2otcj9jb2fv76cmk27oqd6gf',
        'client_secret': '1e2vube7o7iqmrjur6nea65oged4ds4eu33fi2jtmqb0aa1a4tfl'
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        return None

# 송장 정보 조회 함수
def get_tracking_info(tracking_number):
    access_token = get_access_token()
    if not access_token:
        return {"error": "액세스 토큰을 가져올 수 없습니다."}

    url = 'https://apis.tracker.delivery/graphql'
    query = """
        query Track($carrierId: ID!, $trackingNumber: String!) {
          track(carrierId: $carrierId, trackingNumber: $trackingNumber) {
            lastEvent {
              time
              status {
                code
              }
            }
          }
        }
    """
    variables = {
        'carrierId': 'kr.hanjin',
        'trackingNumber': tracking_number
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data.get('data') and data['data']['track'] and data['data']['track']['lastEvent']:
            last_event = data['data']['track']['lastEvent']
            return {
                "status": last_event['status']['code'],
                "time": last_event['time']
            }
        else:
            return {"error": "배송 정보를 찾을 수 없습니다."}
    else:
        return {"error": "API 호출 중 오류가 발생했습니다."}

# 배송 상태 한국어 변환 함수
def translate_status(status_code):
    status_mapping = {
        "DELIVERED": "배송 완료",
        "IN_TRANSIT": "배송 중",
        "OUT_FOR_DELIVERY": "배송 준비 중",
        "PENDING": "배송 대기 중",
        "UNKNOWN": "알 수 없음"
    }
    return status_mapping.get(status_code, "상태 정보 없음")

# 루트 경로 정의 (홈 페이지)
@app.route('/')
def home():
    return render_template('home.html')

# 첫 번째 페이지: 구매처 선택
@app.route('/question_site', methods=['GET', 'POST'])
def select_purchase_site():
    if request.method == 'POST':
        purchase_site = request.form.get('purchase_site')
        if purchase_site == "슬룸 공식 홈페이지":
            return redirect(url_for('event_experience'))  # 이벤트 참여 질문으로 이동
        else:  # "그 외 온라인사이트"를 선택한 경우
            return render_template('external_purchase_restriction.html')  # 새로운 제한 페이지 렌더링
    return render_template('question_site.html')

# 두 번째 페이지: 이벤트 참여 경험 확인
@app.route('/question_event', methods=['GET', 'POST'])
def event_experience():
    if request.method == 'POST':
        event_participation = request.form.get('event_participation')
        if event_participation == "아니오":
            return redirect(url_for('know_delivery_date'))  # 배송 완료일 확인으로 이동
        else:
            return render_template('refund_not_eligible.html')  # 환불 불가 페이지로 이동
    return render_template('question_event.html')

# 세 번째 페이지: 배송 완료일 확인 여부
@app.route('/question3', methods=['GET', 'POST'])
def know_delivery_date():
    if request.method == 'POST':
        know_delivery_date = request.form.get('know_delivery_date')
        if know_delivery_date == "예":
            return redirect(url_for('enter_delivery_date'))  # 배송 완료일 입력으로 이동
        else:  # "아니오"를 선택한 경우
            return render_template('unknown_delivery.html')  # 송장번호 입력 페이지로 이동
    return render_template('question3.html')

# 네 번째 페이지: 배송 완료일 입력
@app.route('/input_delivery_date', methods=['GET', 'POST'])
def enter_delivery_date():
    if request.method == 'POST':
        delivery_date_str = request.form.get('delivery_date')
        try:
            # 배송 완료일을 datetime 객체로 변환
            delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d')
            today = datetime.now()

            # 배송 완료일이 오늘 기준 30일 이상, 40일 이하
            if today - timedelta(days=40) <= delivery_date <= today - timedelta(days=30):
                return redirect(url_for('refund_event_info'))

            # 배송 완료일이 오늘 기준 30일 미만
            elif delivery_date > today - timedelta(days=30):
                start_date = (delivery_date + timedelta(days=30)).strftime('%Y-%m-%d')
                end_date = (delivery_date + timedelta(days=40)).strftime('%Y-%m-%d')
                return render_template('event_period_restriction.html', start_date=start_date, end_date=end_date)

            # 배송 완료일이 오늘 기준 40일 초과
            else:
                start_date = (delivery_date + timedelta(days=30)).strftime('%Y-%m-%d')
                end_date = (delivery_date + timedelta(days=40)).strftime('%Y-%m-%d')
                return render_template('event_expired_restriction.html', start_date=start_date, end_date=end_date)

        except ValueError:
            return render_template('input_delivery_date.html', error="올바른 날짜 형식을 입력해주세요.")
    
    return render_template('input_delivery_date.html')

# 송장 번호 조회 라우트
@app.route('/track', methods=['POST'])
def track():
    tracking_number = request.form.get('tracking_number')
    if tracking_number:
        tracking_info = get_tracking_info(tracking_number)
        if "status" in tracking_info:
            tracking_info["status"] = translate_status(tracking_info["status"])
        return render_template('tracking_result.html', tracking_info=tracking_info)
    else:
        return render_template('tracking_result.html', tracking_info={"error": "송장번호를 입력해주세요."})

# 결과 페이지
@app.route('/result', methods=['GET'])
def refund_event_info():
    return render_template('result.html')

if __name__ == '__main__':
    app.run(debug=True)