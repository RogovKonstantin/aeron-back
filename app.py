from template_utils import *
from folder_utils import *
from parse_utils import *
from db_init import DatabaseSetup
from flask import Flask, request
from flask_cors import CORS

db_setup = DatabaseSetup()
db_setup.setup()
app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@app.errorhandler(Exception)
def handle_error(e):
    logger.error(f"An error occurred: {str(e)}")
    return jsonify({"error": "Internal Server Error"}), 500


@app.route("/parse", methods=["POST", "PUT"])
def parse_route():
    return parse(request)


@app.route("/get-template", methods=["GET"])
def get_template_route():
    return get_template(request)


@app.route("/save-template", methods=["POST"])
def save_template_route():
    return save_template(request)


@app.route("/get-all-templates", methods=["GET"])
def get_all_templates_route():
    return get_all_templates()


@app.route("/get-template-details", methods=["GET"])
def get_template_details_route():
    return get_template_details(request)


@app.route("/update-template", methods=["PUT", "POST"])
def update_template_route():
    return update_template(request)


@app.route('/save-folder', methods=['POST'])
def save_folder_route():
    return save_folder(request)


@app.route("/get-all-folders", methods=["GET"])
def get_all_folders_route():
    return get_all_folders()


@app.route("/get-folders-with-templates", methods=["GET"])
def get_folders_with_templates_route():
    return get_folders_with_templates()


@app.route("/get-folder-id", methods=["GET"])
def get_folder_id_route():
    return get_folder_id(request)


if __name__ == "__main__":
    app.run(debug=True)
