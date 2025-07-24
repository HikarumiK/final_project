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
    "ryota": "hikaru"
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
        base_query += " WHERE p.name ILIKE %s OR p.description ILIKE %s"
        params.extend([f"%{search_query}%", f"%{search_query}%"])

    base_query += " GROUP BY p.procedure_id, p.name, p.description"

    if sort_by == 'price_asc': order_clause = " ORDER BY min_price ASC NULLS LAST, p.name ASC"
    elif sort_by == 'clinic_count_desc': order_clause = " ORDER BY clinic_count DESC, p.name ASC"
    else: order_clause = " ORDER BY p.name ASC"
    
    count_query = f"SELECT COUNT(*) FROM ({base_query}) as subquery"
    cursor.execute(count_query, params)
    total_count = cursor.fetchone()[0]
    total_pages = math.ceil(total_count / ITEMS_PER_PAGE)
    
    offset = (page - 1) * ITEMS_PER_PAGE
    data_query = base_query + order_clause + f" LIMIT {ITEMS_PER_PAGE} OFFSET {offset}"
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