import os
import psycopg
from http.server import BaseHTTPRequestHandler

DATABASE_URL = os.environ.get("DATABASE_URL")

def init_db():
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS calculator_logs (
                    id SERIAL PRIMARY KEY,
                    num1 DOUBLE PRECISION NOT NULL,
                    num2 DOUBLE PRECISION NOT NULL,
                    result DOUBLE PRECISION NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW()
                )
            """)
        conn.commit()

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if not DATABASE_URL:
                raise ValueError("DATABASE_URL is not set")

            init_db()

            with psycopg.connect(DATABASE_URL) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, num1, num2, result, created_at
                        FROM calculator_logs
                        ORDER BY id DESC
                        LIMIT 50
                    """)
                    rows = cur.fetchall()

            html = """
            <!DOCTYPE html>
            <html lang="ko">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>계산 로그</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        background: #f4f4f4;
                        padding: 30px;
                    }
                    h1 {
                        margin-bottom: 20px;
                    }
                    a {
                        display: inline-block;
                        margin-bottom: 20px;
                    }
                    table {
                        border-collapse: collapse;
                        width: 100%;
                        background: white;
                    }
                    th, td {
                        border: 1px solid #ddd;
                        padding: 10px;
                        text-align: center;
                    }
                    th {
                        background: #222;
                        color: white;
                    }
                </style>
            </head>
            <body>
                <a href="/">← 계산기로 돌아가기</a>
                <h1>계산 로그</h1>
                <table>
                    <tr>
                        <th>ID</th>
                        <th>num1</th>
                        <th>num2</th>
                        <th>result</th>
                        <th>created_at</th>
                    </tr>
            """

            for row in rows:
                html += f"""
                    <tr>
                        <td>{row[0]}</td>
                        <td>{row[1]}</td>
                        <td>{row[2]}</td>
                        <td>{row[3]}</td>
                        <td>{row[4]}</td>
                    </tr>
                """

            html += """
                </table>
            </body>
            </html>
            """

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(f"Error: {e}".encode("utf-8"))
