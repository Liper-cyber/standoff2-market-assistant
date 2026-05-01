from psycopg2.extras import RealDictCursor
import psycopg2
from config.database import DB_CONFIG


class DatabaseService:
    def execute_query(self, query , params = None, fetch_one=False , fetch_all=False):
        """Универсальная функция для выполнения запросов"""
        conn = None
        cur = None
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor(cursor_factory=RealDictCursor)
            if params:
                cur.execute(query , params)
            else:
                cur.execute(query)
            query_type = query.strip().upper().split()[0]
            if query_type in ('UPDATE', 'INSERT', 'DELETE', 'ALTER', 'CREATE', 'DROP', 'TRUNCATE'):
                conn.commit()
            if len(query) < 15:
                print("✅ Изменения сохранены в запросе: " , query[:15])

            if fetch_one:
                return cur.fetchone()
            elif fetch_all:
                return cur.fetchall()
            else:
                return cur.rowcount
        except Exception as e:
            if conn:
                conn.rollback()
            print(e)
        finally:
            if cur: cur.close()
            if conn: conn.close()



data = DatabaseService()