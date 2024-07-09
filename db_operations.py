import psycopg2
from psycopg2 import sql
import logging
from config import Config

DB_NAME = 'acars'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'
DB_HOST = "127.0.0.1"
DB_PORT = "5432"

logger = logging.getLogger(__name__)


def get_db_connection():
    return psycopg2.connect(dbname=Config.DB_NAME,
                            user=Config.DB_USER,
                            password=Config.DB_PASSWORD,
                            host=Config.DB_HOST,
                            port=Config.DB_PORT)


def execute_query(query, params=None, fetchone=False, fetchall=False):
    conn = psycopg2.connect(dbname=Config.DB_NAME,
                            user=Config.DB_USER,
                            password=Config.DB_PASSWORD,
                            host=Config.DB_HOST,
                            port=Config.DB_PORT)
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            if fetchone:
                result = cursor.fetchone()
            elif fetchall:
                result = cursor.fetchall()
            else:
                result = None
        conn.commit()
        return result
    except psycopg2.Error as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        conn.close()


def save_to_database(table, columns, values):
    query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
        sql.Identifier(table),
        sql.SQL(', ').join(map(sql.Identifier, columns)),
        sql.SQL(', ').join(sql.Placeholder() * len(values))
    )
    execute_query(query, values)
