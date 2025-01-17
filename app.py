from flask import Flask, request, render_template, redirect, url_for
import requests

app = Flask(__name__)

# 사용자 입력 데이터를 저장할 딕셔너리
data = {}

# 액세스 토큰을 가져오는 함수
def get_access_token():
    url = "https://auth.tracker.delivery/oauth2/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": "5e2otcj9jb2fv76cmk27oqd6gf",  # 실제 client_id 입력
        "client_secret": "1e2vube7o7iqmrjur6nea65oged4ds4eu33fi2jtmqb0aa1a4tfl",  # 실제 client_secret 입력
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    try:
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
        json_response = response.json()
        return json_response.get("access_token")
    except Exception as e:
        print(f"액세스 토큰 오류: {e}")
        return None

# 배송 정보를 가져오는 함수
def get_tracking_info(tracking_number):
    access_token = get_access_token()
    if not access_token:
        return "액세스 토큰 오류"

    url = "https://apis.tracker.delivery/graphql"
    query = """
    query Track($carrierId: ID!, $trackingNumber: String!) {
      track(carrierId: $carrierId, trackingNumber: $trackingNumber) {
        lastEvent {
          time
        }
      }
    }
    """
    variables = {
        "carrierId": "kr.hanjin",  # 한진택배의 carrierId
        "trackingNumber": tracking_number
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    try:
        response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
        response.raise_for_status()
        json_response = response.json()

        if json_response.get("data") and json_response["data"]["track"]["lastEvent"]:
            last_event = json_response["data"]["track"]["lastEvent"]
            delivery_time = last_event["time"]
            return delivery_time  # 배송 완료 시간만 반환
        else:
            return "배송 정보 없음"
    except Exception as e:
        print(f"API 호출 오류: {e}")
        return "API 호출 오류"

# 기본 경로: 첫 번째 질문 페이지로 리디렉션
@app.route('/')
def index():
    return redirect(url_for('question_site'))

# 1번 질문: 슬룸 제품을 어느 사이트에서 구매하셨나요?
@app.route('/question_site', methods=['GET', 'POST'])
def question_site():
    if request.method == 'POST':
        data['purchase_site'] = request.form.get('purchase_site')
        if data['purchase_site'] == '슬룸 공식 홈페이지':
            return redirect(url_for('question_event'))  # 2번 질문으로 이동
        else:
            return redirect(url_for('external_purchase_restriction'))  # 외부몰 안내 페이지로 이동
    return render_template('question_site.html')

# 외부몰 안내 페이지
@app.route('/external_purchase_restriction')
def external_purchase_restriction():
    return render_template('external_purchase_restriction.html')

# 2번 질문: 100% 환불 이벤트 참여 경험
@app.route('/question_event', methods=['GET', 'POST'])
def question_event():
    if request.method == 'POST':
        data['event_participation'] = request.form.get('event_participation')
        if data['event_participation'] == '예':
            return redirect(url_for('refund_not_eligible'))  # "예" 선택 시 별도 페이지로 이동
        return redirect(url_for('question3'))  # "아니오" 선택 시 3번 질문으로 이동
    return render_template('question_event.html')

# 환불 서비스 제한 안내 페이지
@app.route('/refund_not_eligible')
def refund_not_eligible():
    return render_template('refund_not_eligible.html')

# 3번 질문: 슬룸 제품 수령 후 40일 이내 여부
@app.route('/question3', methods=['GET', 'POST'])
def question3():
    if request.method == 'POST':
        # 선택 저장
        data['within_40_days'] = request.form.get('within_40_days')

        if data['within_40_days'] == '예':
            return redirect(url_for('question4'))  # 다음 질문 페이지로 이동
        elif data['within_40_days'] == '아니오':
            return redirect(url_for('info_page'))  # 안내 페이지로 이동
        elif data['within_40_days'] == '모름':
            return redirect(url_for('unknown_delivery'))  # 송장번호 입력 페이지로 이동

    return render_template('question3.html', data=data)

# 송장번호 입력 페이지
@app.route('/unknown_delivery', methods=['GET', 'POST'])
def unknown_delivery():
    if request.method == 'POST':
        data['tracking_number'] = request.form.get('tracking_number')
        if data['tracking_number']:
            tracking_info = get_tracking_info(data['tracking_number'])
            data['tracking_info'] = tracking_info
            return redirect(url_for('tracking_result'))  # 송장번호 결과 페이지로 이동
    return render_template('unknown_delivery.html')

# 송장번호 결과 페이지
@app.route('/tracking_result')
def tracking_result():
    return render_template('tracking_result.html', data=data)

# 안내 페이지
@app.route('/info_page')
def info_page():
    return render_template('info_page.html')

# 4번째 질문 페이지
@app.route('/question4', methods=['GET', 'POST'])
def question4():
    if request.method == 'POST':
        choice = request.form.get('choice')
        if choice == 'yes':
            return redirect(url_for('result'))
        elif choice == 'no':
            return redirect(url_for('refund_not_eligible'))
    return render_template('question4.html')