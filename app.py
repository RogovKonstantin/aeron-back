from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2

DB_NAME = 'acars'
DB_USER = 'user_back'
DB_PASSWORD = 'Gdfhg354'

app = Flask(__name__)
CORS(app, resources={r"/download": {"origins": "*"}})


def get_db_connection():
    return psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host="127.0.0.1", port="5432")


def save_message_to_database(message, result):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO message (message, result) VALUES (%s, %s)"
    cursor.execute(query, (message, result))
    conn.commit()
    conn.close()


def save_template_to_database(template_name, picking_template, template, model, message, folder_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO templates (template_name, picking_template, template, model, message, folder_id) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (template_name, picking_template, template, model, message, folder_id))
    conn.commit()
    conn.close()


def save_folder_to_database(folder_name, parent_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO folders (folder_name, parent_id) VALUES (%s, %s)',
                   (folder_name, parent_id))
    conn.commit()
    cursor.close()
    conn.close()


def get_template_from_database(template_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM templates WHERE template_id = %s"
    cursor.execute(query, (template_id,))
    template = cursor.fetchone()
    conn.close()
    return template


def get_all_templates_from_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT template_id, template_name FROM templates"
    cursor.execute(query)
    templates = cursor.fetchall()
    conn.close()
    return templates


@app.route("/save-message", methods=["POST"])
def save_message():
    data = request.get_json()
    if data:
        message = data.get("message")
        result = data.get("result")
        if message and result:
            save_message_to_database(message, result)
            return "Message saved to database", 201
        else:
            return "Incomplete data", 400
    else:
        return "No data received", 400


@app.route("/save-template", methods=["POST"])
def save_template():
    data = request.get_json()
    if data:
        template_name = data.get("template_name")
        picking_template = data.get("picking_template")
        template = data.get("template")
        model = data.get("model")
        message = data.get("message")
        folder_id = data.get("folder_id")
        if template_name and picking_template and template and model and message and folder_id:
            save_template_to_database(template_name, picking_template, template, model, message, folder_id)
            return "Template saved to database", 201
        else:
            return "Incomplete data", 400
    else:
        return "No data received", 400


@app.route("/save-folder", methods=["POST"])
def save_folder():
    data = request.get_json()
    if data:
        folder_name = data.get("folder_name")
        parent_id = data.get("parent_id")
        if folder_name and (parent_id is None or isinstance(parent_id, int)):
            save_folder_to_database(folder_name, parent_id)
            return "Folder saved to database", 201
        else:
            return "Incomplete data", 400
    else:
        return "No data received", 400


@app.route("/get-template/<int:template_id>", methods=["GET"])
def get_template(template_id):
    template = get_template_from_database(template_id)
    if template:
        return jsonify({
            "template_id": template[0],
            "template_name": template[1],
            "picking_template": template[2],
            "template": template[3],
            "model": template[4],
            "message": template[5],
            "folder_id": template[6]
        })
    else:
        return "Template not found", 404


@app.route("/get-all-templates", methods=["GET"])
def get_all_templates():
    templates = get_all_templates_from_database()
    return jsonify([
        {"template_id": template[0], "template_name": template[1]}
        for template in templates
    ])


if __name__ == "__main__":
    app.run(debug=True)
