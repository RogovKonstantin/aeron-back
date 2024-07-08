import json

from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2 import sql
import re
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
        return jsonify({"error": "No data received"}), 400

    message = data.get("message")
    result = data.get("result")
    if not (message and result):
        return jsonify({"error": "Incomplete data"}), 400

    save_to_database('message', ['message', 'result'], [message, result])
    response = {
        "message": message,
        "result": result
    }
    return jsonify(response), 201


@app.route("/save-template", methods=["POST"])
def save_template():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400

    required_fields = ['template_name', 'folder_id']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Incomplete data"}), 400

    folder_id = data['folder_id']
    if folder_id in [1, 2]:
        return jsonify({"error": "Templates cannot be created in folders with id 1 and 2"}), 403

    save_to_database('templates', required_fields, [data[field] for field in required_fields])
    response = {
        "template_name": data['template_name'],
        "folder_id": data['folder_id']
    }
    return jsonify(response), 201


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


@app.route("/get-folders-with-templates", methods=["GET"])
def get_folders_with_templates():
    folder_query = "SELECT folder_id, folder_name, parent_id FROM folders"
    folders = execute_query(folder_query, fetchall=True)

    template_query = "SELECT template_id, template_name, folder_id FROM templates"
    templates = execute_query(template_query, fetchall=True)

    folder_dict = {
        folder[0]: {"folder_id": folder[0], "folder_name": folder[1], "parent_id": folder[2], "templates": []} for
        folder in folders}

    for template in templates:
        folder_id = template[2]
        if folder_id in folder_dict:
            folder_dict[folder_id]["templates"].append({
                "template_id": template[0],
                "template_name": template[1]
            })

    return jsonify(list(folder_dict.values()))


@app.route("/get-template-details", methods=["GET"])
def get_template_details():
    template_id = request.args.get("template_id")

    if not template_id:
        return jsonify({"error": "Incomplete data"}), 400

    try:
        template_id = int(template_id)
    except ValueError:
        return jsonify({"error": "Invalid template_id"}), 400

    query = """
        SELECT message, template, template_name, template_id 
        FROM templates 
        WHERE template_id = %s
    """
    template_details = execute_query(query, (template_id,), fetchone=True)

    if template_details:
        return jsonify(
            {"message": template_details[0], "template": template_details[1], "template_name": template_details[2],
             "template_id": template_details[3]})

    return jsonify({"error": "Template not found"}), 404


@app.route("/update-template", methods=["PUT", "POST"])
def update_template():
    data = request.get_json()
    template_id = data.get("template_id")
    new_template_value = data.get("new_template_value")

    if not all([template_id, new_template_value]):
        return jsonify({"error": "Incomplete data"}), 400

    try:
        template_id = int(template_id)
    except ValueError:
        return jsonify({"error": "Invalid template_id"}), 400

    query = """
        UPDATE templates 
        SET template = %s
        WHERE template_id = %s
        RETURNING template_id, template_name, template
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (new_template_value, template_id))
                updated_template = cursor.fetchone()
                conn.commit()
    except psycopg2.Error as e:
        return jsonify({"error": f"Database error: {e}"}), 500

    if updated_template:
        response = {
            "template_id": updated_template[0],
            "template_name": updated_template[1],
            "template": updated_template[2]
        }
        return jsonify(response), 200
    else:
        return jsonify({"error": f"Template with ID {template_id} not found"}), 404


@app.route('/save-folder', methods=['POST'])
def save_folder():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400

    folder_name = data.get("folder_name")
    parent_id = data.get("parent_id")
    if not folder_name or not isinstance(parent_id, int):
        return jsonify({"error": "Incomplete data"}), 400

    save_to_database('folders', ['folder_name', 'parent_id'], [folder_name, parent_id])
    response = {
        "folder_name": folder_name,
        "parent_id": parent_id
    }
    return jsonify(response), 201


@app.route("/parse", methods=["POST", "PUT"])
def parse():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400

    template_id = data.get("template_id")
    template_name = data.get("template_name")
    template = data.get("template")
    message = data.get("message")

    if not (template_id and template_name and template and message):
        return jsonify({"error": "Incomplete data"}), 400

    # Fetch the existing template from the database
    existing_template_query = "SELECT template, message, template_name FROM templates WHERE template_id = %s"
    existing_template = execute_query(existing_template_query, (template_id,), fetchone=True)

    if not existing_template:
        return jsonify({"error": "Template not found"}), 404

    existing_template_json, existing_message, existing_template_name = existing_template

    # Serialize incoming template for comparison
    serialized_template = json.dumps(template, sort_keys=True)

    # Check if the template or message has changed
    template_changed = serialized_template != existing_template_json
    message_changed = message != existing_message

    # Assume parse_message is a function that parses the message using the provided template
    parsed_result = parse_message(template, message)

    if template_changed and parsed_result:
        # Logic for saving as a new template if changed
        new_template_name = find_next_template_name(template_name)
        folder_id_query = "SELECT folder_id FROM templates WHERE template_id = %s"
        folder_id = execute_query(folder_id_query, (template_id,), fetchone=True)[0]
        save_to_database('templates', ['template_name', 'template', 'message', 'folder_id'],
                         [new_template_name, serialized_template, message, folder_id])

        # Save the original message and the parsing result
        save_message_and_result_query = "INSERT INTO messages (message, result) VALUES (%s, %s)"
        execute_query(save_message_and_result_query, (message, json.dumps(parsed_result)))

        # Fetch the ID and name of the newly created template
        new_template_query = "SELECT template_id, template_name FROM templates WHERE template_name = %s ORDER BY template_id DESC LIMIT 1"
        new_template = execute_query(new_template_query, (new_template_name,), fetchone=True)

        response = {"template_id": new_template[0], "template_name": new_template[1], "parsed_result": parsed_result}
        return jsonify(response), 200

    elif not template_changed and parsed_result:
        # Update the existing template if not changed
        update_template_query = """
            UPDATE templates 
            SET template = %s, message = %s
            WHERE template_id = %s
            RETURNING template_id
        """
        updated_template_id = execute_query(update_template_query, (serialized_template, message, template_id), fetchone=True)[0]

        # Save the original message and the parsing result
        save_message_and_result_query = "INSERT INTO messages (message, result) VALUES (%s, %s)"
        execute_query(save_message_and_result_query, (message, json.dumps(parsed_result)))

        if updated_template_id:
            response = {"template_id": updated_template_id, "template_name": existing_template_name, "parsed_result": parsed_result}
            return jsonify(response), 200
        else:
            return jsonify({"error": "Template update failed"}), 404

    elif not template_changed and not parsed_result:
        # Handle case where template hasn't changed and parsing failed
        return jsonify({"message": message, "parsed_result": parsed_result}), 200

    return jsonify({"error": "Template not updated"}), 400


def parse_message(template, message):
    parsed_data = {}
    for key, pattern in template.items():
        match = re.findall(pattern, message)
        parsed_data[key] = match
    return parsed_data


def find_next_template_name(template_name):
    query = """
        SELECT template_name FROM templates 
        WHERE template_name LIKE %s
        ORDER BY template_name DESC
        LIMIT 1
    """
    similar_templates = execute_query(query, (f"{template_name}%",), fetchall=True)

    if similar_templates:
        last_template_name = similar_templates[0][0]
        match = re.search(r'\d+$', last_template_name)
        if match:
            number_suffix = int(match.group()) + 1
            new_template_name = f"{template_name} {number_suffix}"
        else:
            new_template_name = f"{template_name} 1"
    else:
        new_template_name = f"{template_name} 1"

    return new_template_name




if __name__ == "__main__":
    app.run(debug=True)