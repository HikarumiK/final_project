import os
import math
# import mysql.connector # ← この行を削除
import psycopg2 # ← この行を追加
from psycopg2.extras import DictCursor # ← この行を追加
from flask import Flask, render_template, request
from dotenv import load_dotenv
from flask_httpauth import HTTPBasicAuth

load_dotenv()
app = Flask(__name__)
auth = HTTPBasicAuth()

USERS = {"admin": "secret"}

@auth.verify_password
def verify_password(username, password):
    if username in USERS and USERS[username] == password:
        return username

ITEMS_PER_PAGE = 25

def get_db_connection():
    """データベース接続を取得する関数 (PostgreSQL版)"""
    # .envからローカル接続情報を取得
    conn_str = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(conn_str)
    return conn

# --- これ以降の @app.route(...) の中身は一切変更ありません ---
# (省略)