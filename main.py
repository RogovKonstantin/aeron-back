from flask import Flask
from flask import request
from flask_cors import CORS
import psycopg2

DB_NAME = 'acars'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'

app = Flask(__name__)
CORS(app, resources={r"/download": {"origins": "*"}})


def save_data_to_database(message_id, message, result):
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()

    query = "INSERT INTO message (message_id, message, result) VALUES (%s, %s, %s)"
    cursor.execute(query, (message_id, message, result))

    conn.commit()
    conn.close()


@app.route("/download", methods=["POST"])
def upload():
    data = request.get_json()
    if data:
        message_id = data.get("message_id")
        message = data.get("message")
        result = data.get("result")

        if message_id and message and result:
            save_data_to_database(message_id, message, result)
            return "Data saved to database"
        else:
            return "Incomplete data", 400
    else:
        return "No data received", 400


if __name__ == "__main__":
    app.run(debug=True)
