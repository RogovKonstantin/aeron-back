from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2

DB_NAME = 'acars'
DB_USER = 'user_back'
DB_PASSWORD = 'Gdfhg354'

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host="127.0.0.1", port="5432")

cursor = conn.cursor()

create_table_query1 = '''CREATE TABLE IF NOT EXISTS folders (
                            folder_id SERIAL PRIMARY KEY,
                            folder_name VARCHAR(255) NOT NULL,
                            parent_id INTEGER,
                            FOREIGN KEY (parent_id) REFERENCES folders(folder_id)
                        )'''
cursor.execute(create_table_query1)

create_table_query2 = '''CREATE TABLE IF NOT EXISTS message (
                            message_id SERIAL PRIMARY KEY,
                            message VARCHAR(255) NOT NULL,
                            result VARCHAR(255)
                        )'''
cursor.execute(create_table_query2)

create_table_query3 = '''CREATE TABLE IF NOT EXISTS templates (
                            template_id SERIAL PRIMARY KEY,
                            template_name VARCHAR(255) NOT NULL,
                            picking_template VARCHAR(255),
                            template VARCHAR(255),
                            model VARCHAR(255),
                            message VARCHAR(255),
                            folder_id INTEGER,
                            FOREIGN KEY (folder_id) REFERENCES folders(folder_id)
                        )'''
cursor.execute(create_table_query3)

populate_table_query1 = '''INSERT INTO folders (folder_name, parent_id)
                            VALUES ('Folder A', NULL),
                                   ('Folder B', NULL),
                                   ('Subfolder 1', 1),
                                   ('Subfolder 2', 1)'''
cursor.execute(populate_table_query1)

populate_table_query2 = '''INSERT INTO message (message, result)
                            VALUES ('Message 1', 'Result A'),
                                   ('Message 2', 'Result B')'''
cursor.execute(populate_table_query2)

populate_table_query3 = '''INSERT INTO templates (template_name, picking_template, template, model, message, folder_id)
                            VALUES ('Template 1', 'Picking A', 'Template A', 'Model A', 'Message 1', 1),
                                   ('Template 2', 'Picking B', 'Template B', 'Model B', 'Message 2', 2)'''
cursor.execute(populate_table_query3)

conn.commit()

conn.close()


app = Flask(__name__)
CORS(app, resources={r"/download": {"origins": "*"}})


def get_db_connection():
    return psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)


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
