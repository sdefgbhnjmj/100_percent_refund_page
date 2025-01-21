from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

# 액세스 토큰 가져오기
def get_access_token():
    url = "https://auth.tracker.delivery/oauth2/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": "5e2otcj9jb2fv76cmk27oqd6gf",
        "client_secret": "1e2vube7o7iqmrjur6nea65oged4ds4eu33fi2jtmqb0aa1a4tfl"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    try:
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
        token_data = response.json()
        return token_data.get("access_token")
    except requests.exceptions.RequestException as e:
        print(f"오류 발생: {e}")
        return None

# 배송 정보 가져오기
def get_tracking_info(tracking_number):
    access_token = get_access_token()
    if not access_token:
        return {"error": "액세스 토큰 오류"}

    url = "https://apis.tracker.delivery/graphql"
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
        "carrierId": "kr.hanjin",
        "trackingNumber": tracking_number
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    try:
        response = requests.post(
            url, 
            json={"query": query, "variables": variables}, 
            headers=headers
        )
        response.raise_for_status()
        data = response.json()
        
        last_event = data.get("data", {}).get("track", {}).get("lastEvent")
        if last_event:
            status = last_event.get("status", {}).get("code")
            time = last_event.get("time")
            return {"status": status, "time": time}
        else:
            return {"error": "배송 정보 없음"}
    except requests.exceptions.RequestException as e:
        print(f"API 호출 오류: {e}")
        return {"error": "API 호출 오류"}

# 첫 번째 페이지: 구매처 선택
@app.route('/', methods=['GET', 'POST'])
def select_purchase_site():
    if request.method == 'POST':
        purchase_site = request.form.get('purchase_site')
        if not purchase_site:
            error = "구매처를 선택하세요."
            return render_template('purchase_site.html', error=error)
        return redirect(url_for('event_experience'))  # 다음 페이지로 이동

    return render_template('purchase_site.html')

# 두 번째 페이지: 이벤트 참여 경험 확인
@app.route('/event_experience', methods=['GET', 'POST'])
def event_experience():
    if request.method == 'POST':
        event_participation = request.form.get('event_participation')
        if not event_participation:
            error = "참여 경험 여부를 선택하세요."
            return render_template('event_experience.html', error=error)
        return redirect(url_for('know_delivery_date'))  # 다음 단계로 이동

    return render_template('event_experience.html')

# 세 번째 페이지: 배송 완료일 확인 여부
@app.route('/know_delivery_date', methods=['GET', 'POST'])
def know_delivery_date():
    if request.method == 'POST':
        know_delivery = request.form.get('know_delivery_date')
        if not know_delivery:
            error = "배송 완료일 확인 여부를 선택하세요."
            return render_template('know_delivery_date.html', error=error)
        return redirect(url_for('enter_delivery_date'))  # 다음 단계로 이동

    return render_template('know_delivery_date.html')

# 네 번째 페이지: 배송 완료일 입력
@app.route('/enter_delivery_date', methods=['GET', 'POST'])
def enter_delivery_date():
    if request.method == 'POST':
        delivery_date = request.form.get('delivery_date')
        if not delivery_date:
            error = "배송 완료일을 입력해주세요."
            return render_template('enter_delivery_date.html', error=error)
        return redirect(url_for('refund_event_info'))  # 다음 단계로 이동

    return render_template('enter_delivery_date.html')

# 다섯 번째 페이지: 100% 환불 이벤트 정보
@app.route('/refund_event_info', methods=['GET'])
def refund_event_info():
    return render_template('refund_event_info.html')

# 여섯 번째 페이지: 송장번호 입력
@app.route('/unknown_delivery', methods=['GET'])
def index():
    return render_template('unknown_delivery.html')

# 일곱 번째 페이지: 송장번호 조회
@app.route('/track', methods=['POST'])
def track_package():
    tracking_number = request.form.get('tracking_number')
    tracking_info = get_tracking_info(tracking_number)
    return render_template('tracking_result.html', tracking_info=tracking_info)

if __name__ == '__main__':
    app.run(debug=True)
