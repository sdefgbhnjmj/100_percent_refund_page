from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta
import requests

app = Flask(__name__)

# 홈페이지
@app.route('/')
def home():
    return render_template('home.html')

# 구매처 선택
@app.route('/question_site', methods=['GET', 'POST'])
def question_site():
    if request.method == 'POST':
        purchase_site = request.form.get('purchase_site')
        if purchase_site == "슬룸 공식 홈페이지":
            return redirect(url_for('question_event'))
        else:
            return render_template('external_purchase_restriction.html')
    return render_template('question_site.html')

# 100% 환불 이벤트 참여 여부
@app.route('/question_event', methods=['GET', 'POST'])
def question_event():
    if request.method == 'POST':
        event_participation = request.form.get('event_participation')
        if event_participation == "예":
            return render_template('refund_not_eligible.html')
        else:
            return redirect(url_for('refund_product_selection'))
    return render_template('question_event.html')

# 환불 상품 구성 선택
@app.route('/refund_product_selection', methods=['GET', 'POST'])
def refund_product_selection():
    if request.method == 'POST':
        refund_option = request.form.get('refund_option')
        if refund_option == "set":
            return redirect(url_for('refund_set_product_info'))
        elif refund_option == "multiple":
            return redirect(url_for('refund_multiple_product_info'))
        elif refund_option == "single":
            return redirect(url_for('refund_single_product_info'))
    return render_template('refund_product_selection.html')

@app.route('/refund_set_product_info')
def refund_set_product_info():
    return render_template('refund_set_product_info.html')

@app.route('/refund_multiple_product_info')
def refund_multiple_product_info():
    return render_template('refund_multiple_product_info.html')

@app.route('/refund_single_product_info')
def refund_single_product_info():
    return render_template('refund_single_product_info.html')

# 배송 완료일 여부
@app.route('/question3', methods=['GET', 'POST'])
def question3():
    if request.method == 'POST':
        know_delivery_date = request.form.get('know_delivery_date')
        if know_delivery_date == "예":
            return redirect(url_for('input_delivery_date'))
        else:
            return redirect(url_for('track'))
    return render_template('question3.html')

# 송장번호 조회 API 연동
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

# 배송 완료일 입력
@app.route('/input_delivery_date', methods=['GET', 'POST'])
def input_delivery_date():
    if request.method == 'POST':
        delivery_date_str = request.form.get('delivery_date')
        try:
            delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d')
            today = datetime.now()

            if today - timedelta(days=40) <= delivery_date <= today - timedelta(days=30):
                return redirect(url_for('refund_event_info'))
            elif delivery_date > today - timedelta(days=30):
                start_date = (delivery_date + timedelta(days=30)).strftime('%Y-%m-%d')
                end_date = (delivery_date + timedelta(days=40)).strftime('%Y-%m-%d')
                return render_template('event_period_restriction.html', start_date=start_date, end_date=end_date)
            else:
                start_date = (delivery_date + timedelta(days=30)).strftime('%Y-%m-%d')
                end_date = (delivery_date + timedelta(days=40)).strftime('%Y-%m-%d')
                return render_template('event_expired_restriction.html', start_date=start_date, end_date=end_date)
        except ValueError:
            return render_template('input_delivery_date.html', error="올바른 날짜 형식을 입력해주세요.")
    return render_template('input_delivery_date.html')

# 환불 가능 여부 최종 안내
@app.route('/result', methods=['GET'])
def refund_event_info():
    return render_template('result.html')

# API 연동 함수
def get_access_token():
    url = 'https://auth.tracker.delivery/oauth2/token'
    payload = {
        'grant_type': 'client_credentials',
        'client_id': '5e2otcj9jb2fv76cmk27oqd6gf',
        'client_secret': '1e2vube7o7iqmrjur6nea65oged4ds4eu33fi2jtmqb0aa1a4tfl'
    }
    response = requests.post(url, data=payload)
    return response.json().get('access_token') if response.status_code == 200 else None

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
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}
    response = requests.post(url, json={'query': query, 'variables': {'carrierId': 'kr.hanjin', 'trackingNumber': tracking_number}}, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        last_event = data['data']['track']['lastEvent']
        return {"status": last_event['status']['code'], "time": last_event['time']} if last_event else {"error": "배송 정보를 찾을 수 없습니다."}
    return {"error": "API 호출 중 오류가 발생했습니다."}

if __name__ == '__main__':
    app.run(debug=True)