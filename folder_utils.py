from db_operations import *
from flask import jsonify


def get_folder_id(request):
    folder_name = request.args.get("folder_name")
    if not folder_name:
        return jsonify({"error": "Folder name not provided"}), 400

    query = "SELECT folder_id FROM folders WHERE folder_name = %s"
    folder = execute_query(query, (folder_name,), fetchone=True)
    if folder:
        return jsonify({"folder_id": folder[0]}), 200
    return jsonify({"error": "Folder not found"}), 404


def save_folder(request):
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


def get_all_folders():
    query = "SELECT * FROM folders"
    folders = execute_query(query, fetchall=True)
    return jsonify([
        {"folder_id": folder[0], "folder_name": folder[1], "parent_id": folder[2]}
        for folder in folders
    ]), 200


def get_folders_with_templates():
    folder_query = "SELECT folder_id, folder_name, parent_id FROM folders"
    folders = execute_query(folder_query, fetchall=True)

    template_query = "SELECT template_id, template_name, folder_id FROM templates"
    templates = execute_query(template_query, fetchall=True)

    folder_dict = {
        folder[0]: {"folder_id": folder[0], "folder_name": folder[1], "parent_id": folder[2], "templates": []}
        for folder in folders
    }

    for template in templates:
        folder_id = template[2]
        if folder_id in folder_dict:
            folder_dict[folder_id]["templates"].append({
                "template_id": template[0],
                "template_name": template[1]
            })

    return jsonify(list(folder_dict.values())), 200
