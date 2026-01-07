from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta

import os, json
from oauth2client.service_account import ServiceAccountCredentials
import gspread

scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

# Render 환경변수에서 JSON 불러오기
google_creds = json.loads(os.environ["GOOGLE_CREDENTIALS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(google_creds, scope)
client = gspread.authorize(creds)

# 스프레드시트 ID로 열기
spreadsheet = client.open_by_key("1t7Oa-rKPY2aYgphNugE5K5gMCP7Hn3joaJYp-bbh7Jw")
sheet = spreadsheet.get_worksheet_by_id(866695027)


import requests

app = Flask(__name__)
app.secret_key = "random-secret-key"

@app.route('/', methods=['GET', 'POST'])
def select_brand():
    if request.method == 'POST':
        brand = request.form.get('brand')

        # brand 값이 있으면 기존처럼 처리
        if brand == "슬룸":
            return redirect(url_for('home'))
        elif brand == "셀올로지":
            return redirect(url_for('cellology_home'))

        # brand 값이 없으면 → "100% 환불 이벤트 확인" 버튼
        return redirect(url_for('input_phonenumber'))

    # GET 요청이면 기본 페이지 렌더링
    return render_template('select_brand.html')


@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/question_site', methods=['GET', 'POST'])
def select_purchase_site():
    if request.method == 'POST':
        purchase_site = request.form.get('purchase_site')
        if purchase_site == "슬룸 공식 홈페이지":
            return redirect(url_for('event_experience'))
        else:
            return render_template('external_purchase_restriction.html')
    return render_template('question_site.html')

@app.route('/question_event', methods=['GET', 'POST'])
def event_experience():
    if request.method == 'POST':
        event_participation = request.form.get('event_participation')
        if event_participation == "아니오":
            return redirect(url_for('refund_product_selection'))
        else:
            return render_template('refund_not_eligible.html')
    return render_template('question_event.html')

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

@app.route('/refund_set_product_info', methods=['GET', 'POST'])
def refund_set_product_info():
    if request.method == 'POST':
        return redirect(url_for('know_delivery_date'))
    return render_template('refund_set_product_info.html')

@app.route('/refund_multiple_product_info', methods=['GET', 'POST'])
def refund_multiple_product_info():
    if request.method == 'POST':
        return redirect(url_for('know_delivery_date'))
    return render_template('refund_multiple_product_info.html')

@app.route('/refund_single_product_info', methods=['GET', 'POST'])
def refund_single_product_info():
    if request.method == 'POST':
        return redirect(url_for('know_delivery_date'))
    return render_template('refund_single_product_info.html')

@app.route('/question3', methods=['GET', 'POST'])
def know_delivery_date():
    if request.method == 'POST':
        know_delivery_date = request.form.get('know_delivery_date')
        if know_delivery_date == "예":
            return redirect(url_for('enter_delivery_date'))
        else:
            return render_template('unknown_delivery.html')
    return render_template('question3.html')

@app.route('/input_delivery_date', methods=['GET', 'POST'])
def enter_delivery_date():
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

@app.route('/eligible_next', methods=['GET', 'POST'])
def eligible_next():
    if request.method == 'POST':
        return redirect(url_for('refund_product_selection'))
    return render_template('eligible_next.html')

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

@app.route('/result', methods=['GET'])
def refund_event_info():
    return render_template('result.html')

@app.route('/cellology/home')
def cellology_home():
    return render_template('cellology/cellology_home.html')

@app.route('/cellology/question_site', methods=['GET', 'POST'])
def cellology_question_site():
    if request.method == 'POST':
        purchase_site = request.form.get('purchase_site')
        if purchase_site == "셀올로지 공식 홈페이지":
            return redirect(url_for('cellology_question_event'))
        else:
            return render_template('cellology/cellology_external_purchase_restriction.html')
    return render_template('cellology/cellology_question_site.html')

@app.route('/cellology/question_event', methods=['GET', 'POST'])
def cellology_question_event():
    if request.method == 'POST':
        event_participation = request.form.get('event_participation')
        if event_participation == "아니오":
            return redirect(url_for('cellology_refund_product_selection'))
        else:
            return render_template('cellology/cellology_refund_not_eligible.html')
    return render_template('cellology/cellology_question_event.html')

@app.route('/cellology/refund_product_selection', methods=['GET', 'POST'])
def cellology_refund_product_selection():
    if request.method == 'POST':
        refund_option = request.form.get('refund_option')
        if refund_option == "set":
            return redirect(url_for('cellology_refund_set_product_info'))
        elif refund_option == "multiple":
            return redirect(url_for('cellology_refund_multiple_product_info'))
        elif refund_option == "single":
            return redirect(url_for('cellology_refund_single_product_info'))
    return render_template('cellology/cellology_refund_product_selection.html')

@app.route('/cellology/refund_set_product_info', methods=['GET', 'POST'])
def cellology_refund_set_product_info():
    if request.method == 'POST':
        return redirect(url_for('cellology_know_delivery_date'))
    return render_template('cellology/cellology_refund_set_product_info.html')

@app.route('/cellology/refund_multiple_product_info', methods=['GET', 'POST'])
def cellology_refund_multiple_product_info():
    if request.method == 'POST':
        return redirect(url_for('cellology_know_delivery_date'))
    return render_template('cellology/cellology_refund_multiple_product_info.html')

@app.route('/cellology/refund_single_product_info', methods=['GET', 'POST'])
def cellology_refund_single_product_info():
    if request.method == 'POST':
        return redirect(url_for('cellology_know_delivery_date'))
    return render_template('cellology/cellology_refund_single_product_info.html')

@app.route('/cellology/question3', methods=['GET', 'POST'])
def cellology_know_delivery_date():
    if request.method == 'POST':
        know_delivery_date = request.form.get('know_delivery_date')
        if know_delivery_date == "예":
            return redirect(url_for('cellology_enter_delivery_date'))
        else:
            return render_template('cellology/cellology_unknown_delivery.html')
    return render_template('cellology/cellology_question3.html')

@app.route('/cellology/input_delivery_date', methods=['GET', 'POST'])
def cellology_enter_delivery_date():
    if request.method == 'POST':
        delivery_date_str = request.form.get('delivery_date')
        try:
            delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d')
            today = datetime.now()
            if today - timedelta(days=40) <= delivery_date <= today - timedelta(days=30):
                return redirect(url_for('cellology_result'))
            elif delivery_date > today - timedelta(days=30):
                start_date = (delivery_date + timedelta(days=30)).strftime('%Y-%m-%d')
                end_date = (delivery_date + timedelta(days=40)).strftime('%Y-%m-%d')
                return render_template('cellology/cellology_event_period_restriction.html', start_date=start_date, end_date=end_date)
            else:
                start_date = (delivery_date + timedelta(days=30)).strftime('%Y-%m-%d')
                end_date = (delivery_date + timedelta(days=40)).strftime('%Y-%m-%d')
                return render_template('cellology/cellology_event_expired_restriction.html', start_date=start_date, end_date=end_date)
        except ValueError:
            return render_template('cellology/cellology_input_delivery_date.html', error="올바른 날짜 형식을 입력해주세요.")
    return render_template('cellology/cellology_input_delivery_date.html')

@app.route('/cellology/result', methods=['GET'])
def cellology_result():
    return render_template('cellology/cellology_result.html')

@app.route('/cellology/track', methods=['POST'])
def cellology_track():
    tracking_number = request.form.get('tracking_number')
    if tracking_number:
        tracking_info = get_tracking_info(tracking_number)
        if "status" in tracking_info:
            tracking_info["status"] = translate_status(tracking_info["status"])
        return render_template('cellology/cellology_tracking_result.html', tracking_info=tracking_info)
    else:
        return render_template('cellology/cellology_tracking_result.html', tracking_info={"error": "송장번호를 입력해주세요."})

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
    return None

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
    variables = {'carrierId': 'kr.hanjin', 'trackingNumber': tracking_number}
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}
    response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data.get('data') and data['data']['track'] and data['data']['track']['lastEvent']:
            last_event = data['data']['track']['lastEvent']
            return {"status": last_event['status']['code'], "time": last_event['time']}
        else:
            return {"error": "배송 정보를 찾을 수 없습니다."}
    return {"error": "API 호출 중 오류가 발생했습니다."}

def translate_status(status_code):
    status_mapping = {
        "DELIVERED": "배송 완료",
        "IN_TRANSIT": "배송 중",
        "OUT_FOR_DELIVERY": "배송 준비 중",
        "PENDING": "배송 대기 중",
        "UNKNOWN": "알 수 없음"
    }
    return status_mapping.get(status_code, "상태 정보 없음")

@app.route('/eligible.html')
def eligible_page():
    return render_template('eligible.html')

@app.route('/not_eligible.html')
def not_eligible_page():
    return render_template('not_eligible.html')

@app.route('/check_refund_event', methods=['GET', 'POST'])
def check_refund_event():
    if request.method == 'POST':
        phone = request.form.get('phone')
        if not phone:
            return render_template('check_refund_event.html', message="휴대폰 번호를 입력해주세요.")

        try:
            api_url = f"https://script.google.com/a/macros/olit.co.kr/s/AKfycbymWedW4mNsnd7bmUvlVid2xjokXzFXgakDkawQbcMmQuSWIe3E1czzAQx_EU9A7jt6/exec?phone={phone}"
            response = requests.get(api_url)
            result = response.json()

            if result.get("found"):
                return redirect(url_for('not_eligible_page'))
            else:
                return redirect(url_for('eligible_page'))

        except Exception as e:
            print("API 오류:", e)
            return render_template('check_refund_event.html', message="조회 중 오류가 발생했습니다.")
    
    return render_template('check_refund_event.html')

@app.route('/input_phonenumber', methods=['GET', 'POST'])
def input_phonenumber():
    if request.method == 'POST':
        phone = request.form.get('phone')
        if not phone:
            return render_template('input_phonenumber.html', message="휴대폰 번호를 입력해주세요.")

        try:
            api_url = f"https://script.google.com/a/macros/olit.co.kr/s/AKfycbymWedW4mNsnd7bmUvlVid2xjokXzFXgakDkawQbcMmQuSWIe3E1czzAQx_EU9A7jt6/exec?phone={phone}"
            response = requests.get(api_url)
            result = response.json()

            if result.get("found"):
                return redirect(url_for('not_eligible_phonenumber'))
            else:
                return redirect(url_for('eligible_phonenumber'))

        except Exception as e:
            print("API 오류:", e)
            return render_template('input_phonenumber.html', message="조회 중 오류가 발생했습니다.")
    
    return render_template('input_phonenumber.html')


@app.route('/eligible_phonenumber.html')
def eligible_phonenumber():
    return render_template('eligible_phonenumber.html')


@app.route('/not_eligible_phonenumber.html')
def not_eligible_phonenumber():
    return render_template('not_eligible_phonenumber.html')

# ------------------------------
# 실행
# ------------------------------
if __name__ == '__main__':
    app.run(debug=True)