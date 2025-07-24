import os
import math
import mysql.connector
from flask import Flask, render_template, request
from dotenv import load_dotenv
from flask_httpauth import HTTPBasicAuth # ★ 新規インポート

load_dotenv()
app = Flask(__name__)
auth = HTTPBasicAuth() # ★ 認証オブジェクトを作成

# --- ▼▼▼ ここから新規追加 ▼▼▼ ---

# ユーザー名とパスワードを設定
# 重要：実際の運用では、より複雑なパスワードに変更してください
USERS = {
    "ryota": "hikaru"
}

@auth.verify_password
def verify_password(username, password):
    """パスワードを検証する関数"""
    if username in USERS and USERS[username] == password:
        return username

# --- ▲▲▲ ここまで新規追加 ▲▲▲ ---


ITEMS_PER_PAGE = 25

def get_db_connection():
    # (変更なし)
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        database=os.environ.get('DB_NAME')
    )

@app.route('/')
@auth.login_required # ★ この行を追加
def home():
    return render_template('home.html')

@app.route('/procedures/')
@auth.login_required # ★ この行を追加
def show_procedures():
    # (関数の中身は変更なし)
    page, search_query, sort_by = request.args.get('page', 1, type=int), request.args.get('q', ''), request.args.get('sort', 'name_asc')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    base_query = """
        SELECT SQL_CALC_FOUND_ROWS p.procedure_id, p.name, p.description,
               COUNT(ct.treatment_id) AS clinic_count, MIN(ct.price) AS min_price
        FROM Procedures p LEFT JOIN Clinic_Treatments ct ON p.procedure_id = ct.procedure_id
    """
    params = []
    if search_query:
        base_query += " WHERE p.name LIKE %s OR p.description LIKE %s"
        params.extend([f"%{search_query}%", f"%{search_query}%"])
    base_query += " GROUP BY p.procedure_id, p.name, p.description"
    if sort_by == 'price_asc': order_clause = " ORDER BY min_price ASC, p.name ASC"
    elif sort_by == 'clinic_count_desc': order_clause = " ORDER BY clinic_count DESC, p.name ASC"
    else: order_clause = " ORDER BY p.name ASC"
    offset = (page - 1) * ITEMS_PER_PAGE
    cursor.execute(base_query + order_clause + f" LIMIT {ITEMS_PER_PAGE} OFFSET {offset}", params)
    procedures = cursor.fetchall()
    cursor.execute("SELECT FOUND_ROWS() AS total_count;")
    total_pages = math.ceil(cursor.fetchone()['total_count'] / ITEMS_PER_PAGE)
    cursor.close(), conn.close()
    return render_template('procedures.html', procedures=procedures, page=page, total_pages=total_pages, search_query=search_query, sort_by=sort_by)

@app.route('/procedure/<int:procedure_id>/')
@auth.login_required # ★ この行を追加
def show_procedure_detail(procedure_id):
    # (関数の中身は変更なし)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Procedures WHERE procedure_id = %s", (procedure_id,))
    procedure = cursor.fetchone()
    if not procedure: return "施術が見つかりません", 404
    cursor.execute("""
        SELECT c.clinic_id, c.clinic_name, ct.price, ct.price_details, ct.equipment_or_material, ct.our_notes
        FROM Clinic_Treatments ct JOIN Clinics c ON ct.clinic_id = c.clinic_id
        WHERE ct.procedure_id = %s ORDER BY ct.price ASC
    """, (procedure_id,))
    treatments = cursor.fetchall()
    cursor.close(), conn.close()
    return render_template('procedure_detail.html', procedure=procedure, treatments=treatments)

@app.route('/concerns/')
@auth.login_required # ★ この行を追加
def show_concerns():
    # (関数の中身は変更なし)
    page, search_query = request.args.get('page', 1, type=int), request.args.get('q', '')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    base_query, params = "SELECT SQL_CALC_FOUND_ROWS * FROM Concerns", []
    if search_query:
        base_query += " WHERE name LIKE %s"
        params.append(f"%{search_query}%")
    offset = (page - 1) * ITEMS_PER_PAGE
    cursor.execute(base_query + f" ORDER BY concern_id ASC LIMIT {ITEMS_PER_PAGE} OFFSET {offset}", params)
    concerns = cursor.fetchall()
    cursor.execute("SELECT FOUND_ROWS() AS total_count;")
    total_pages = math.ceil(cursor.fetchone()['total_count'] / ITEMS_PER_PAGE)
    cursor.close(), conn.close()
    return render_template('concerns.html', concerns=concerns, page=page, total_pages=total_pages, search_query=search_query)

@app.route('/concern/<int:concern_id>/')
@auth.login_required # ★ この行を追加
def show_concern_detail(concern_id):
    # (関数の中身は変更なし)
    page = request.args.get('page', 1, type=int)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Concerns WHERE concern_id = %s", (concern_id,))
    concern = cursor.fetchone()
    if not concern: return "お悩みが見つかりません", 404
    base_query = """
        SELECT SQL_CALC_FOUND_ROWS p.* FROM Procedures p
        JOIN Concern_Procedure_Links cpl ON p.procedure_id = cpl.procedure_id
        WHERE cpl.concern_id = %s ORDER BY p.name ASC
    """
    offset = (page - 1) * ITEMS_PER_PAGE
    cursor.execute(base_query + f" LIMIT {ITEMS_PER_PAGE} OFFSET {offset}", (concern_id,))
    procedures = cursor.fetchall()
    cursor.execute("SELECT FOUND_ROWS() AS total_count;")
    total_pages = math.ceil(cursor.fetchone()['total_count'] / ITEMS_PER_PAGE)
    cursor.close(), conn.close()
    return render_template('concern_detail.html', concern=concern, procedures=procedures, page=page, total_pages=total_pages)

@app.route('/clinics/')
@auth.login_required # ★ この行を追加
def show_clinics():
    # (関数の中身は変更なし)
    page, search_query = request.args.get('page', 1, type=int), request.args.get('q', '')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    base_query, params = "SELECT SQL_CALC_FOUND_ROWS * FROM Clinics", []
    if search_query:
        base_query += " WHERE clinic_name LIKE %s"
        params.append(f"%{search_query}%")
    offset = (page - 1) * ITEMS_PER_PAGE
    cursor.execute(base_query + f" ORDER BY clinic_name ASC LIMIT {ITEMS_PER_PAGE} OFFSET {offset}", params)
    clinics = cursor.fetchall()
    cursor.execute("SELECT FOUND_ROWS() AS total_count;")
    total_pages = math.ceil(cursor.fetchone()['total_count'] / ITEMS_PER_PAGE)
    cursor.close(), conn.close()
    return render_template('clinics.html', clinics=clinics, page=page, total_pages=total_pages, search_query=search_query)

@app.route('/clinic/<int:clinic_id>/')
@auth.login_required # ★ この行を追加
def show_clinic_detail(clinic_id):
    # (関数の中身は変更なし)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Clinics WHERE clinic_id = %s", (clinic_id,))
    clinic = cursor.fetchone()
    if not clinic: return "クリニックが見つかりません", 404
    cursor.execute("""
        SELECT p.procedure_id, p.name AS procedure_name, ct.price, ct.price_details,
               ct.equipment_or_material, ct.our_notes
        FROM Clinic_Treatments ct JOIN Procedures p ON ct.procedure_id = p.procedure_id
        WHERE ct.clinic_id = %s ORDER BY p.name ASC
    """, (clinic_id,))
    treatments = cursor.fetchall()
    cursor.close(), conn.close()
    return render_template('clinic_detail.html', clinic=clinic, treatments=treatments)

@app.route('/doctors/')
@auth.login_required # ★ この行を追加
def show_doctors():
    # (関数の中身は変更なし)
    page, search_query, specialist_only = request.args.get('page', 1, type=int), request.args.get('q', ''), request.args.get('specialist') == 'true'
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    base_query = "SELECT SQL_CALC_FOUND_ROWS d.doctor_id, d.name, d.is_specialist, i.name AS institution_name FROM Doctors d LEFT JOIN Institutions i ON d.institution_id = i.institution_id"
    params, where_clauses = [], []
    if search_query:
        where_clauses.append("d.name LIKE %s")
        params.append(f"%{search_query}%")
    if specialist_only:
        where_clauses.append("d.is_specialist = TRUE")
    if where_clauses:
        base_query += " WHERE " + " AND ".join(where_clauses)
    offset = (page - 1) * ITEMS_PER_PAGE
    cursor.execute(base_query + f" ORDER BY d.name ASC LIMIT {ITEMS_PER_PAGE} OFFSET {offset}", params)
    doctors = cursor.fetchall()
    cursor.execute("SELECT FOUND_ROWS() AS total_count;")
    total_pages = math.ceil(cursor.fetchone()['total_count'] / ITEMS_PER_PAGE)
    cursor.close(), conn.close()
    return render_template('doctors.html', doctors=doctors, page=page, total_pages=total_pages, search_query=search_query, specialist_only=specialist_only)

@app.route('/doctor/<int:doctor_id>/')
@auth.login_required # ★ この行を追加
def show_doctor_detail(doctor_id):
    # (関数の中身は変更なし)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT d.doctor_id, d.name, d.is_specialist, i.name AS institution_name
        FROM Doctors d LEFT JOIN Institutions i ON d.institution_id = i.institution_id
        WHERE d.doctor_id = %s
    """, (doctor_id,))
    doctor = cursor.fetchone()
    if not doctor: return "医師が見つかりません", 404
    cursor.close(), conn.close()
    return render_template('doctor_detail.html', doctor=doctor)

if __name__ == '__main__':
    app.run(debug=True)