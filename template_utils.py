from db_operations import *
import re
from flask import jsonify


def process_template_string(template_string):
    # Remove the initial and trailing quotes
    template_string = template_string.strip('"')
    # Replace the escaped newlines with actual newlines
    template_string = template_string.replace('\\n', '\n')
    # Convert the string representation of the template into a valid dictionary
    template_dict = {}
    pattern = re.compile(r'"([^"]+)": r"(.+?)"', re.DOTALL)
    matches = pattern.findall(template_string)
    for key, value in matches:
        template_dict[key] = value.replace(r'\\', '\\')
    return template_dict


def parse_message(template, message):
    parsed_data = {}
    for key, pattern in template.items():
        match = re.findall(pattern, message)
        parsed_data[key] = match
    return parsed_data


def get_template(request):
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


def save_template(request):
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


def get_all_templates():
    query = "SELECT template_id, template_name, folder_id FROM templates"
    templates = execute_query(query, fetchall=True)
    return jsonify([
        {"template_id": template[0], "template_name": template[1], "folder_id": template[2]}
        for template in templates
    ])


def get_template_details(request):
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


def update_template(request):
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
