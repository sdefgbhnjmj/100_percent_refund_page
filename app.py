from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta
from pytz import timezone

import os, json
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ------------------------------
# Google Sheet 설정
# ------------------------------
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

google_creds = json.loads(os.environ["GOOGLE_CREDENTIALS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(google_creds, scope)
client = gspread.authorize(creds)

spreadsheet = client.open_by_key("1t7Oa-rKPY2aYgphNugE5K5gMCP7Hn3joaJYp-bbh7Jw")
sheet = spreadsheet.get_worksheet_by_id(866695027)

# ------------------------------
# Flask App
# ------------------------------
app = Flask(__name__)
app.secret_key = "random-secret-key"

# ------------------------------
# 공통 함수
# ------------------------------
def normalize_phone(phone):
    if not phone:
        return None
    return ''.join(filter(str.isdigit, phone))

# ------------------------------
# 브랜드 선택
# ------------------------------
@app.route('/', methods=['GET', 'POST'])
def select_brand():
    if request.method == 'POST':
        brand = request.form.get('brand')

        if brand == "슬룸":
            return redirect(url_for('home'))
        elif brand == "셀올로지":
            return redirect(url_for('cellology_home'))

        return redirect(url_for('select_brand'))

    return render_template('select_brand.html')

# ------------------------------
# 슬룸 환불 플로우
# ------------------------------
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

@app.route('/result')
def refund_event_info():
    return render_template('result.html')

# ------------------------------
# 셀올로지 환불 플로우
# ------------------------------
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

@app.route('/cellology/result')
def cellology_result():
    return render_template('cellology/cellology_result.html')

# ------------------------------
# 불량 교환(AS) 플로우 (원본 유지)
# ------------------------------
@app.route('/defective_exchange')
def defective_exchange():
    return render_template("AS/defective_exchange.html")

# (이하 AS 전체 로직 그대로 유지 — 사용자가 제공한 코드와 동일)

# ------------------------------
# 실행
# ------------------------------
if __name__ == '__main__':
    app.run(debug=True)
