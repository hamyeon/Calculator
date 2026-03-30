import os
import json
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
        response = json.dumps({
            "message": "Backend is running. Use POST with num1 and num2."
        }).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(response)

    def do_POST(self):
        try:
            if not DATABASE_URL:
                raise ValueError("DATABASE_URL is not set")

            init_db()

            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)

            num1 = float(data.get("num1", 0))
            num2 = float(data.get("num2", 0))
            result = num1 + num2

            with psycopg.connect(DATABASE_URL) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO calculator_logs (num1, num2, result)
                        VALUES (%s, %s, %s)
                    """, (num1, num2, result))
                conn.commit()

            response = json.dumps({"result": result}).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.end_headers()
            self.wfile.write(response)

        except Exception as e:
            response = json.dumps({"error": str(e)}).encode("utf-8")

            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(response)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
