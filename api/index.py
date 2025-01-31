from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def home():
    return 'Welcome to the Homepage!'

@app.route('/question_site', methods=['GET', 'POST'])
def select_purchase_site():
    if request.method == 'POST':
        purchase_site = request.form.get('purchase_site')
        if purchase_site == "슬룸 공식 홈페이지":
            return redirect(url_for('event_experience'))
        else:
            return render_template('question_site.html', error="구매처를 슬룸 공식 홈페이지로 선택해주세요.")
    return render_template('question_site.html')

@app.route('/question_event', methods=['GET', 'POST'])
def event_experience():
    if request.method == 'POST':
        event_participation = request.form.get('event_participation')
        if event_participation == "아니오":
            return redirect(url_for('know_delivery_date'))
        else:
            return render_template('question_event.html', error="100% 환불 이벤트 참여 이력이 없어야 합니다.")
    return render_template('question_event.html')

@app.route('/question3', methods=['GET', 'POST'])
def know_delivery_date():
    if request.method == 'POST':
        know_delivery_date = request.form.get('know_delivery_date')
        if know_delivery_date == "예":
            return redirect(url_for('enter_delivery_date'))
        else:
            return render_template('question3.html', error="배송 완료일을 알고 있어야 합니다.")
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
            else:
                error = "배송 완료일은 오늘 기준으로 30일 이상, 40일 이내여야 합니다."
                return render_template('enter_delivery_date.html', error=error)
        except ValueError:
            return render_template('enter_delivery_date.html', error="올바른 날짜 형식을 입력해주세요.")
    return render_template('enter_delivery_date.html')

@app.route('/result', methods=['GET'])
def refund_event_info():
    return render_template('result.html')

# Vercel 서버리스 함수로 Flask 앱 반환
def handler(request):
    return app(request)
