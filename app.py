from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2 import sql
from db_init import DatabaseSetup

db_setup = DatabaseSetup()
db_setup.setup()
DB_NAME = 'acars'
DB_USER = 'user_back'
DB_PASSWORD = 'Gdfhg354'
DB_HOST = "127.0.0.1"
DB_PORT = "5432"

app = Flask(__name__)
CORS(app)


def get_db_connection():
    return psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)


def execute_query(query, params=None, fetchone=False, fetchall=False):
    result = None
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            if fetchone:
                result = cursor.fetchone()
            if fetchall:
                result = cursor.fetchall()
    return result


def save_to_database(table, columns, values):
    query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
        sql.Identifier(table),
        sql.SQL(', ').join(map(sql.Identifier, columns)),
        sql.SQL(', ').join(sql.Placeholder() * len(values))
    )
    execute_query(query, values)


@app.route("/save-message", methods=["POST"])
def save_message():
    data = request.get_json()
    if not data:
        return "No data received", 400

    message = data.get("message")
    result = data.get("result")
    if not (message and result):
        return "Incomplete data", 400

    save_to_database('message', ['message', 'result'], [message, result])
    return "Message saved to database", 201


@app.route("/save-template", methods=["POST"])
def save_template():
    data = request.get_json()
    if not data:
        return "No data received", 400

    required_fields = ['template_name', 'folder_id']
    if not all(field in data for field in required_fields):
        return "Incomplete data", 400

    save_to_database('templates', required_fields, [data[field] for field in required_fields])
    return "Template saved to database", 201


@app.route("/save-folder", methods=["POST"])
def save_folder():
    data = request.get_json()
    if not data:
        return "No data received", 400

    folder_name = data.get("folder_name")
    parent_id = data.get("parent_id")
    if not folder_name or not isinstance(parent_id, int):
        return "Incomplete data", 400

    save_to_database('folders', ['folder_name', 'parent_id'], [folder_name, parent_id])
    return "Folder saved to database", 201


@app.route("/get-folder-id", methods=["GET"])
def get_folder_id():
    folder_name = request.args.get("folder_name")
    if not folder_name:
        return "Folder name not provided", 400
    query = "SELECT folder_id FROM folders WHERE folder_name = %s"
    folder = execute_query(query, (folder_name,), fetchone=True)
    if folder:
        return jsonify({"folder_id": folder[0]})
    return "Folder not found", 404


@app.route("/get-template", methods=["GET"])
def get_template():
    template_id = request.args.get("template_id")
    if not template_id:
        return "Template ID not provided", 400

    try:
        template_id = int(template_id)
    except ValueError:
        return "Invalid Template ID", 400

    query = "SELECT template FROM templates WHERE template_id = %s"
    template = execute_query(query, (template_id,), fetchone=True)
    if template:
        return jsonify({"template": template[0]})
    return "Template not found", 404


@app.route("/get-all-templates", methods=["GET"])
def get_all_templates():
    query = "SELECT template_id, template_name, folder_id FROM templates"
    templates = execute_query(query, fetchall=True)
    return jsonify([
        {"template_id": template[0], "template_name": template[1], "folder_id": template[2]}
        for template in templates
    ])


@app.route("/get-all-folders", methods=["GET"])
def get_all_folders():
    query = "SELECT * FROM folders"
    folders = execute_query(query, fetchall=True)
    return jsonify([
        {"folder_id": folder[0], "folder_name": folder[1], "parent_id": folder[2]}
        for folder in folders
    ])


if __name__ == "__main__":
    app.run(debug=True)
