from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta

app = Flask(__name__)

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
            return redirect(url_for('know_delivery_date'))
        else:
            return render_template('question_event.html', error="100% 환불 이벤트 참여 이력이 없어야 합니다.")
    return render_template('question_event.html')

# 세 번째 페이지: 배송 완료일 확인 여부
@app.route('/question3', methods=['GET', 'POST'])
def know_delivery_date():
    if request.method == 'POST':
        know_delivery_date = request.form.get('know_delivery_date')
        if know_delivery_date == "예":
            return redirect(url_for('enter_delivery_date'))
        else:
            return render_template('question3.html', error="배송 완료일을 알고 있어야 합니다.")
    return render_template('question3.html')

from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta

app = Flask(__name__)

# 루트 경로 정의 (홈 페이지)
@app.route('/')
def home():
    return render_template('home.html')

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

# 결과 페이지
@app.route('/result', methods=['GET'])
def refund_event_info():
    return render_template('result.html')

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))  # Render에서 제공하는 포트 가져오기
    app.run(host='0.0.0.0', port=port)