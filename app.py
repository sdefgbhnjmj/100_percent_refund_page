from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# 액세스 토큰 가져오기
def get_access_token():
    url = "https://auth.tracker.delivery/oauth2/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": "5e2otcj9jb2fv76cmk27oqd6gf",  # 실제 client_id
        "client_secret": "1e2vube7o7iqmrjur6nea65oged4ds4eu33fi2jtmqb0aa1a4tfl"  # 실제 client_secret
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    try:
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()  # 오류 발생 시 예외 처리
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
        "carrierId": "kr.hanjin",  # 한진택배 carrierId
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
        response.raise_for_status()  # 오류 발생 시 예외 처리
        data = response.json()
        
        # 데이터 파싱
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

# 송장번호 입력 페이지
@app.route('/')
def index():
    return render_template('unknown_delivery.html')

# 송장번호 조회 처리
@app.route('/track', methods=['POST'])
def track_package():
    tracking_number = request.form.get('tracking_number')
    tracking_info = get_tracking_info(tracking_number)
    return render_template('tracking_result.html', tracking_info=tracking_info)

if __name__ == '__main__':
    app.run(debug=True)
