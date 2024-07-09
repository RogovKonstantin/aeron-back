from db_operations import *
from flask import jsonify


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
