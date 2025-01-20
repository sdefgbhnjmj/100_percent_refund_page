from flask import Flask, request, render_template, redirect, url_for
from datetime import datetime, timedelta

app = Flask(__name__)

# 사용자 입력 데이터를 저장할 딕셔너리
data = {}

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

# 3번 질문: 슬룸 제품 수령일 (배송 완료일)을 알고 계신가요?
@app.route('/question3', methods=['GET', 'POST'])
def question3():
    if request.method == 'POST':
        data['know_delivery_date'] = request.form.get('know_delivery_date')
        
        if data['know_delivery_date'] == '예':
            return redirect(url_for('input_delivery_date'))  # 새로운 페이지로 이동
        elif data['know_delivery_date'] == '아니오':
            return redirect(url_for('unknown_delivery'))  # 아니오를 선택 시 송장번호 입력 페이지로 이동

    return render_template('question3.html', data=data)

# 새로운 날짜 입력 페이지
@app.route('/input_delivery_date', methods=['GET', 'POST'])
def input_delivery_date():
    if request.method == 'POST':
        try:
            delivery_date = request.form.get('delivery_date')
            data['delivery_date'] = datetime.strptime(delivery_date, '%Y-%m-%d')

            today = datetime.now()
            after_30_days = data['delivery_date'] + timedelta(days=30)
            after_40_days = data['delivery_date'] + timedelta(days=40)

            # 로그 추가
            print(f"Today: {today}, After 30 days: {after_30_days}, After 40 days: {after_40_days}")

            if today >= after_30_days and today <= after_40_days:
                data['message'] = """
                <strong>아래 기준에 모두 충족하시어 100% 환불 이벤트 참여가 가능합니다.</strong><br>
                - 슬룸 공식 자사몰을 통해 구매한 경우<br>
                - 100% 환불 이벤트 참여 이력이 없는 경우<br>
                - 제품 수령 후 40일 이내인 경우<br>
                - 제품 수령 후 30일 동안 꾸준히 사용하신 경우<br><br>
                '슬룸 고객센터 문의하기' 버튼을 클릭하신 후, 카카오톡 1:1 상담을 통해 성함/연락처와 함께 "체험 후 환불 신청합니다." 말씀해주시면, 이벤트 접수를 도와드리겠습니다.
                """
            elif today > after_40_days:
                data['message'] = "슬룸 제품 수령 후 40일이 경과하여 이벤트 참여가 불가합니다."
            else:
                data['message'] = "제품 수령 후 30일 동안 꾸준히 사용하신 경우에만 환불 가능합니다."

        except ValueError:
            data['message'] = "잘못된 날짜 형식입니다. 다시 입력해주세요."

        return redirect(url_for('result'))

    return render_template('input_delivery_date.html')

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

# 결과 페이지
@app.route('/result')
def result():
    return render_template('result.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
