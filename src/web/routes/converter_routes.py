from flask import (
    Blueprint, render_template, request,
    redirect, url_for, send_from_directory
)
from werkzeug.utils import secure_filename
from pathlib import Path
import json

# Импортируем основные функции из конвертеров
from src.converters.elibrary_excel_test import convert_html_to_excel # type: ignore
from src.converters.excel_irbis_test import convert_excel_to_irbis # type: ignore
from src.converters.key_correction_Excel_IRBIS import key_decoder # type: ignore
from src.converters.key_correction_IRBIS_Excel import key_extraction # type: ignore
from src.services.add_keys_to_excel import append_with_pandas # type: ignore

converter_bp = Blueprint("converter", __name__)

# Читаем пути к папкам файлов в path_config
CONFIG_PATH = Path("data/config/path_config.json")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config_paths = json.load(f)
INPUT_HTML_DIR = config_paths["input_files"]
INPUT_TXT_DIR = config_paths["input_txt_dir"]
SD_DIC_DIR = config_paths["S-D_Dictionary_dir"]
SD_02_DIC_FILE = config_paths["S-D_02_Dictionary_file"]
SD_04_DIC_FILE = config_paths["S-D_04_Dictionary_file"]
OUTPUT_TXT_FILE = config_paths["output_txt_file"]
OUTPUT_TXT_DIR = config_paths["output_txt_dir"]
OUTPUT_GBL_FILE = config_paths["file_for_GB"]
OUTPUT_GBL_DIR = config_paths["dir_for_GB"]
EDITABLE_XLSX_DIR = config_paths["files_to_edit"]
IRBIS_OUTPUT_DIR = config_paths["output_files"]

# Назначаем путь к главной странице
@converter_bp.route("/")
def index():
    return render_template("index.html")

# Назначаем путь к папке "upload"
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

        return redirect(url_for(
            "converter.result",
            excel_count=len(excel_files)
        ))

    return render_template("upload.html")

# Скачивание результата обработки таблицы
@converter_bp.route("/result")
def result():
    excel_files = list(Path(EDITABLE_XLSX_DIR).glob("*.xlsx"))

    return render_template(
        "result.html",
        excel_files=excel_files
    )

# Выделение ненормированных ключей из файла .txt
@converter_bp.route("/txt_key_upload", methods=["GET", "POST"])
def upload_txt_key_file():
    if request.method == "POST":
        # Получаем файл
        file_1 = request.files.get("file_1")

        # Безопасное имя файла
        filename = secure_filename(file_1.filename)
        save_path = Path(INPUT_TXT_DIR) / filename

        # Сохранение файла на диск
        file_1.save(save_path)

        # Выделение ключей и номера специальности
        key_list, topic_num = key_extraction(save_path)
        if topic_num == '02':
            append_with_pandas(SD_02_DIC_FILE, "Sheet", "synonym", key_list)
        elif topic_num == '04':
            append_with_pandas(SD_04_DIC_FILE, "Sheet", "synonym", key_list)

        return redirect(url_for("converter.key_excel_result"))

    return render_template("keywords_1.html")

# Конвертация таблицы автозамены в формат .gbl
@converter_bp.route("/exel_key_upload", methods=["GET", "POST"])
def upload_excel_key_file():
    if request.method == "POST":
        # Получаем файл
        file_2 = request.files.get("file_2")

        # Безопасное имя файла
        filename = secure_filename(file_2.filename)
        save_path = Path(SD_DIC_DIR) / filename

        # Сохранение файла на диск
        file_2.save(save_path)

        # Конвертер Excel to IRBIS-64
        gbl_list = key_decoder(save_path)
        with open(OUTPUT_GBL_FILE, 'w', encoding='utf-8') as file_2:
            file_2.write(''.join(gbl_list))

        return redirect(url_for("converter.key_gbl_result"))

    return render_template("keywords_2.html")

# Вывод дополненной таблицы автозамены
@converter_bp.route("/key_excel_result")
def key_excel_result():
    excel_file = Path(SD_DIC_DIR).glob("*.xlsx")

    return render_template("key_excel_result.html", excel_file=excel_file)

# Вывод финального файла конвертации файла в формате .gbl
@converter_bp.route("/key_result")
def key_gbl_result():
    gbl_file = Path(OUTPUT_GBL_DIR).glob("*.gbl")

    return render_template("key_gbl_result.html", gbl_file=gbl_file)

# Скачивание файла в формате Excel
@converter_bp.route("/download_excel/<path:filename>")
def download_excel_file(filename):
    return send_from_directory(SD_DIC_DIR, filename, as_attachment=True)

# Скачивание файла в формате .gbl
@converter_bp.route("/download_gbl/<path:filename>")
def download_gbl_file(filename):
    return send_from_directory(OUTPUT_GBL_DIR, filename, as_attachment=True)