from db_operations import *
import json
import re
from flask import jsonify


def parse(request):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400

    template_id = data.get("template_id")
    template_name = data.get("template_name")
    template_str = data.get("template")
    message = data.get("message")

    if not (template_id and template_name and template_str and message):
        return jsonify({"error": "Incomplete data"}), 400

    try:
        processed_template = process_template_string(template_str)
        parsed_result = parse_message(processed_template, message)

        if parsed_result:
            # Save message and parsing result to messages table
            save_to_database('messages', ['message', 'result'], [message, json.dumps(parsed_result)])

            # Update template and message fields in templates table
            query = """
                UPDATE templates
                SET template = %s, message = %s
                WHERE template_id = %s
            """
            execute_query(query, (template_str, message, template_id))

            response = {
                "template_id": template_id,
                "template_name": template_name,
                "parsed_result": parsed_result,
                "original_message": message
            }
            return jsonify(response), 200
        else:
            # Save message and error to messages table
            save_to_database('messages', ['message', 'result'], [message, 'Failed to parse message'])
            return jsonify({"error": "Failed to parse message"}), 500

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        save_to_database('messages', ['message', 'result'], [message, f"Invalid JSON format: {e}"])
        return jsonify({"error": f"Invalid JSON format: {e}"}), 400
    except Exception as e:
        logger.error(f"Error during parsing: {e}")
        save_to_database('messages', ['message', 'result'], [message, f"Error during parsing: {e}"])
        return jsonify({"error": f"Error during parsing: {e}"}), 500


def parse_message(template, message):
    parsed_data = {}
    for key, pattern in template.items():
        match = re.findall(pattern, message)
        parsed_data[key] = match
    return parsed_data


def process_template_string(template_string):
    template_string = template_string.strip('"')
    template_string = template_string.replace('\\n', '\n')
    template_dict = {}
    pattern = re.compile(r'"([^"]+)": r"(.+?)"', re.DOTALL)
    matches = pattern.findall(template_string)
    for key, value in matches:
        template_dict[key] = value.replace(r'\\', '\\')
    return template_dict