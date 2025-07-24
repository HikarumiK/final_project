import os
import math
import psycopg2
from psycopg2.extras import DictCursor
from flask import Flask, render_template, request
from dotenv import load_dotenv
from flask_httpauth import HTTPBasicAuth

# .envファイルから環境変数を読み込む
load_dotenv()

app = Flask(__name__)
auth = HTTPBasicAuth()

# サイトにアクセスするためのユーザー名とパスワード
# 重要：公開する際は、より複雑なパスワードに変更してください
USERS = {
    "admin": "secret"
}

@auth.verify_password
def verify_password(username, password):
    """パスワードを検証する関数"""
    if username in USERS and USERS[username] == password:
        return username

# 1ページあたりの表示件数
ITEMS_PER_PAGE = 25

def get_db_connection():
    """データベース接続を取得する関数 (PostgreSQL版)"""
    conn_str = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(conn_str)
    return conn

@app.route('/')
@auth.login_required
def home():
    """ホームページ"""
    return render_template('home.html')

# --- 施術関連ページ ---
@app.route('/procedures/')
@auth.login_required
def show_procedures():
    """施術一覧ページ"""
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '')
    sort_by = request.args.get('sort', 'name_asc')

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)

    base_query = """
        SELECT p.procedure_id, p.name, p.description,
               COUNT(ct.treatment_id) AS clinic_count, MIN(ct.price) AS min_price
        FROM Procedures p LEFT JOIN Clinic_Treatments ct ON p.procedure_id = ct.procedure_id
    """
    params = []
    
    if search_query:
        base_query += " WHERE p.name ILIKE %s OR p.description ILIKE %s" # PostgreSQLではILIKEで大文字小文字を区別しない
        params.extend([f"%{search_query}%", f"%{search_query}%"])

    base_query += " GROUP BY p.procedure_id, p.name, p.description"

    if sort_by == 'price_asc': order_clause = " ORDER BY min_price ASC NULLS LAST, p.name ASC" #価格未設定を最後に
    elif sort_by == 'clinic_count_desc': order_clause = " ORDER BY clinic_count DESC, p.name ASC"
    else: order_clause = " ORDER BY p.name ASC"
    base_query += order_clause

    offset = (page - 1) * ITEMS_PER_PAGE
    
    # 総件数を取得するクエリ
    count_query = f"SELECT COUNT(*) FROM ({base_query}) as subquery"
    cursor.execute(count_query, params)
    total_count = cursor.fetchone()[0]
    total_pages = math.ceil(total_count / ITEMS_PER_PAGE)
    
    # データを取得するクエリ
    data_query = base_query + f" LIMIT {ITEMS_PER_PAGE} OFFSET {offset}"
    cursor.execute(data_query, params)
    procedures = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('procedures.html',
                           procedures=procedures, page=page, total_pages=total_pages,
                           search_query=search_query, sort_by=sort_by)

@app.route('/procedure/<int:procedure_id>/')
@auth.login_required
def show_procedure_detail(procedure_id):
    """施術詳細ページ"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)
    cursor.execute("SELECT * FROM Procedures WHERE procedure_id = %s", (procedure_id,))
    procedure = cursor.fetchone()
    if not procedure: return "施術が見つかりません", 404
    cursor.execute("""
        SELECT c.clinic_id, c.clinic_name, ct.price, ct.price_details, ct.equipment_or_material, ct.our_notes
        FROM Clinic_Treatments ct JOIN Clinics c ON ct.clinic_id = c.clinic_id
        WHERE ct.procedure_id = %s ORDER BY ct.price ASC
    """, (procedure_id,))
    treatments = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('procedure_detail.html', procedure=procedure, treatments=treatments)

# --- お悩み関連ページ ---
@app.route('/concerns/')
@auth.login_required
def show_concerns():
    """お悩み一覧ページ"""
    page, search_query = request.args.get('page', 1, type=int), request.args.get('q', '')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)
    base_query, params = "SELECT %s * FROM Concerns", ["*"]
    if search_query:
        base_query += " WHERE name ILIKE %s"
        params.append(f"%{search_query}%")
    
    count_query = base_query % "COUNT(*)"
    cursor.execute(count_query, params[1:] if "*" in params else params)
    total_count = cursor.fetchone()[0]
    total_pages = math.ceil(total_count / ITEMS_PER_PAGE)
    
    offset = (page - 1) * ITEMS_PER_PAGE
    data_query = base_query % "*"
    cursor.execute(data_query + f" ORDER BY concern_id ASC LIMIT {ITEMS_PER_PAGE} OFFSET {offset}", params[1:] if "*" in params else params)
    concerns = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('concerns.html', concerns=concerns, page=page,
                           total_pages=total_pages, search_query=search_query)

@app.route('/concern/<int:concern_id>/')
@auth.login_required
def show_concern_detail(concern_id):
    """お悩み詳細ページ"""
    page = request.args.get('page', 1, type=int)
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)
    cursor.execute("SELECT * FROM Concerns WHERE concern_id = %s", (concern_id,))
    concern = cursor.fetchone()
    if not concern: return "お悩みが見つかりません", 404
    base_query = """
        SELECT p.* FROM Procedures p
        JOIN Concern_Procedure_Links cpl ON p.procedure_id = cpl.procedure_id
        WHERE cpl.concern_id = %s
    """
    
    count_query = f"SELECT COUNT(*) FROM ({base_query}) as subquery"
    cursor.execute(count_query, (concern_id,))
    total_count = cursor.fetchone()[0]
    total_pages = math.ceil(total_count / ITEMS_PER_PAGE)

    offset = (page - 1) * ITEMS_PER_PAGE
    cursor.execute(base_query + f" ORDER BY p.name ASC LIMIT {ITEMS_PER_PAGE} OFFSET {offset}", (concern_id,))
    procedures = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('concern_detail.html', concern=concern, procedures=procedures,
                           page=page, total_pages=total_pages)

# --- クリニック関連ページ ---
@app.route('/clinics/')
@auth.login_required
def show_clinics():
    """クリニック一覧ページ"""
    page, search_query = request.args.get('page', 1, type=int), request.args.get('q', '')
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)
    base_query, params = "SELECT %s * FROM Clinics", ["*"]
    if search_query:
        base_query += " WHERE clinic_name ILIKE %s"
        params.append(f"%{search_query}%")

    count_query = base_query % "COUNT(*)"
    cursor.execute(count_query, params[1:] if "*" in params else params)
    total_count = cursor.fetchone()[0]
    total_pages = math.ceil(total_count / ITEMS_PER_PAGE)
    
    offset = (page - 1) * ITEMS_PER_PAGE
    data_query = base_query % "*"
    cursor.execute(data_query + f" ORDER BY clinic_name ASC LIMIT {ITEMS_PER_PAGE} OFFSET {offset}", params[1:] if "*" in params else params)
    clinics = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('clinics.html', clinics=clinics, page=page,
                           total_pages=total_pages, search_query=search_query)

@app.route('/clinic/<int:clinic_id>/')
@auth.login_required
def show_clinic_detail(clinic_id):
    """クリニック詳細ページ"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)
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
    cursor.close()
    conn.close()
    return render_template('clinic_detail.html', clinic=clinic, treatments=treatments)

# --- 医師関連ページ ---
@app.route('/doctors/')
@auth.login_required
def show_doctors():
    """医師一覧ページ"""
    page, search_query, specialist_only = request.args.get('page', 1, type=int), request.args.get('q', ''), request.args.get('specialist') == 'true'
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)
    base_query = "FROM Doctors d LEFT JOIN Institutions i ON d.institution_id = i.institution_id"
    params, where_clauses = [], []
    if search_query:
        where_clauses.append("d.name ILIKE %s")
        params.append(f"%{search_query}%")
    if specialist_only:
        where_clauses.append("d.is_specialist = TRUE")
    
    if where_clauses:
        base_query += " WHERE " + " AND ".join(where_clauses)
    
    count_query = "SELECT COUNT(*) " + base_query
    cursor.execute(count_query, params)
    total_count = cursor.fetchone()[0]
    total_pages = math.ceil(total_count / ITEMS_PER_PAGE)

    offset = (page - 1) * ITEMS_PER_PAGE
    data_query = "SELECT d.doctor_id, d.name, d.is_specialist, i.name AS institution_name " + base_query
    cursor.execute(data_query + f" ORDER BY d.name ASC LIMIT {ITEMS_PER_PAGE} OFFSET {offset}", params)
    doctors = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('doctors.html', doctors=doctors, page=page,
                           total_pages=total_pages, search_query=search_query,
                           specialist_only=specialist_only)

@app.route('/doctor/<int:doctor_id>/')
@auth.login_required
def show_doctor_detail(doctor_id):
    """医師詳細ページ"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=DictCursor)
    cursor.execute("""
        SELECT d.doctor_id, d.name, d.is_specialist, i.name AS institution_name
        FROM Doctors d LEFT JOIN Institutions i ON d.institution_id = i.institution_id
        WHERE d.doctor_id = %s
    """, (doctor_id,))
    doctor = cursor.fetchone()
    if not doctor: return "医師が見つかりません", 404
    cursor.close()
    conn.close()
    return render_template('doctor_detail.html', doctor=doctor)

if __name__ == '__main__':
    app.run(debug=True)