from flask import (
    Blueprint, render_template, request,
    redirect, url_for, send_from_directory
)
from werkzeug.utils import secure_filename
from pathlib import Path
import json

from src.converters.elibrary_excel_test import convert_html_to_excel
from src.converters.excel_irbis_test import convert_excel_to_irbis

converter_bp = Blueprint("converter", __name__)

# ---------------------------------------------------------------------
# КОНФИГУРАЦИЯ
# ---------------------------------------------------------------------

CONFIG_PATH = Path("data/config/path_config.json")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config_paths = json.load(f)
INPUT_HTML_DIR = config_paths["input_files"]
EDITABLE_XLSX_DIR = config_paths["files_to_edit"]
IRBIS_OUTPUT_DIR = config_paths["output_files"]


@converter_bp.route("/")
def index():
    return render_template("index.html")


@converter_bp.route("/upload", methods=["GET", "POST"])
def upload_files():
    if request.method == "POST":
        files = request.files.getlist("files")

        uploaded_files = []

        for file in files:
            filename = secure_filename(file.filename)
            save_path = Path(INPUT_HTML_DIR) / filename
            file.save(save_path)
            uploaded_files.append(save_path)

        # HTML → Excel
        excel_files = convert_html_to_excel(uploaded_files)

        # Excel → IRBIS
        irbis_files = convert_excel_to_irbis(excel_files)

        return redirect(url_for(
            "converter.result",
            excel_count=len(excel_files),
            irbis_count=len(irbis_files)
        ))

    return render_template("upload.html")


@converter_bp.route("/result")
def result():
    excel_files = list(Path(EDITABLE_XLSX_DIR).glob("*.xlsx"))
    irbis_files = list(Path(IRBIS_OUTPUT_DIR).glob("*"))

    return render_template(
        "result.html",
        excel_files=excel_files,
        irbis_files=irbis_files
    )


@converter_bp.route("/download/<path:filename>")
def download_file(filename):
    return send_from_directory(IRBIS_OUTPUT_DIR, filename, as_attachment=True)
