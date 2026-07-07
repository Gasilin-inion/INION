from flask import (
    Blueprint, render_template, request,
    redirect, url_for, send_from_directory, flash, abort
)
from werkzeug.utils import secure_filename
from pathlib import Path
import json
import pandas as pd
import datetime

# Импортируем основные функции из конвертеров
from src.converters.elibrary_excel import convert_html_to_excel, data_frame_to_workbook # type: ignore
from src.converters.excel_irbis import convert_to_irbis # type: ignore
from src.converters.key_correction_Excel_IRBIS import key_decoder, add_terms # type: ignore
from src.converters.key_correction_IRBIS_Excel import key_extraction # type: ignore
from src.services.add_keys_to_json import add_keys # type: ignore
from src.services.read_actual_file import read_actual #type: ignore
from src.services.сheck_categories import check_cat #type: ignore

converter_bp = Blueprint("converter", __name__)

# -------------------------------------------------------
# Блок конфигурации
# -------------------------------------------------------

# Читаем пути к папкам файлов в path_config
CURRENT_DIR = Path(__file__).parent
CONFIG_PATH = CURRENT_DIR.parent / "data" / "config" / "path_config.json"
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config_paths = json.load(f)
INPUT_HTML_DIR = config_paths["input_files"]
INPUT_TXT_DIR = config_paths["input_txt_dir"]
TEMP_SD_DIR = config_paths["temp_SD_dir"]
TEMP_SD_02_FILE = config_paths["temp_SD_02_file"]
TEMP_SD_04_FILE = config_paths["temp_SD_04_file"]
SD_DIC_DIR = config_paths["S-D_Dictionary_dir"]
SD_02 = config_paths["SD_02_dir"]
SD_03 = config_paths["SD_03_dir"]
SD_04 = config_paths["SD_04_dir"]
SD_06 = config_paths["SD_06_dir"]
SD_10 = config_paths["SD_10_dir"]
SD_11 = config_paths["SD_11_dir"]
SD_12 = config_paths["SD_12_dir"]
SD_13 = config_paths["SD_13_dir"]
SD_16 = config_paths["SD_16_dir"]
SD_17 = config_paths["SD_17_dir"]
SD_21 = config_paths["SD_21_dir"]
SD_02_DIC_FILE = config_paths["S-D_02_Dictionary_file"]
SD_04_DIC_FILE = config_paths["S-D_04_Dictionary_file"]
OUTPUT_TXT_FILE = config_paths["output_txt_file"]
OUTPUT_TXT_DIR = config_paths["output_txt_dir"]
OUTPUT_GBL_FILE = config_paths["file_for_GB"]
OUTPUT_GBL_DIR = config_paths["dir_for_GB"]
EDITABLE_XLSX_DIR = config_paths["files_to_edit"]
EDITED_XLSX = config_paths["dir_for_edited_excel"]
EDITABLE_XLSX = config_paths["excel_to_edit"]
IRBIS_OUTPUT_DIR = config_paths["output_files"]

# Модуль даты

today = datetime.date.today().strftime("%Y_%m_%d")

# -------------------------------------------------------
# Блок основных функций
# -------------------------------------------------------

# Главная страница
@converter_bp.route("/")
def index():
    return render_template("index.html")

# Конвертор HTML-Excel
@converter_bp.route("/html_upload", methods=["GET", "POST"])
def html_upload():
    if request.method == "POST":
        files = request.files.getlist("html_files")

        uploaded_files = []

        for file in files:
            filename = secure_filename(file.filename)
            save_path = Path(INPUT_HTML_DIR) / filename
            file.save(save_path)
            uploaded_files.append(save_path)

        # Конвертация файлов HTML в дата-фрейм
        articles_pd = convert_html_to_excel(uploaded_files)
        # Формирование таблицы Excel на основе таблицы
        data_frame_to_workbook(articles_pd)

        return redirect(url_for("converter.html_result"))

    return render_template("html_upload.html")

# Конвертор Excel-IRBIS
@converter_bp.route("/excel_upload", methods=["GET", "POST"])
def excel_upload():
    if request.method == "POST":
        # Получаем файл
        excel_file = request.files.get("excel_file")

        # Безопасное имя файла
        filename = secure_filename(excel_file.filename)
        save_path = Path(EDITED_XLSX) / filename

        # Сохранение файла на диск
        excel_file.save(save_path)

        # Преобразуем данные из excel файла в дата-фрейм
        articles_list = pd.read_excel(excel_file)

        # Конвертация файла в формат ИРБИС-64
        convert_to_irbis(articles_list)

        return redirect(url_for("converter.excel_result"))

    return render_template("excel_upload.html")

# Выделение ненормированных ключей из файла .txt
@converter_bp.route("/txt_key_upload", methods=["GET", "POST"])
def upload_txt_key_file():
    if request.method == "POST":
        file_1 = request.files.get("file_1")

        if not file_1 or file_1.filename == "":
            flash("Пожалуйста, загрузите файл .txt.", "error")
            return redirect(request.url)

        filename = secure_filename(file_1.filename)
        save_path = Path(INPUT_TXT_DIR) / filename
        file_1.save(save_path)

        key_list, topic_num = key_extraction(save_path)

        # Формируем дата-фрейм на основе исходного файла
        result_df = check_cat(save_path, topic_num)

        errors_df_exists = True
        errors_df_empty = result_df.empty
        errors_df_rows = result_df.to_dict(orient="records") if not errors_df_empty else []

        # Формируем название выходного файла
        today_str = datetime.date.today().strftime("%Y_%m_%d")  # локальная дата
        output_filename = f"{topic_num}_SD_for_editing_{today_str}.xlsx"
        SD_for_editing = str(Path(TEMP_SD_DIR) / output_filename)

        generated_file = None

        sd_map = {
            "02": SD_02,
            "03": SD_03,
            "04": SD_04,
            "06": SD_06,
            "10": SD_10,
            "11": SD_11,
            "12": SD_12,
            "13": SD_13,
            "16": SD_16,
            "17": SD_17,
            "21": SD_21,
        }

        if topic_num in sd_map:
            actual_SD = read_actual(sd_map[topic_num])
            add_keys(actual_SD, SD_for_editing, key_list)
            generated_file = output_filename
        else:
            flash(f"Специальность {topic_num} не поддерживается для генерации SD-файла.", "warning")

        excel_file_list = [generated_file] if generated_file else []

        return render_template(
            "key_excel_result.html",
            excel_file=excel_file_list,
            errors_df_exists=errors_df_exists,
            errors_df_empty=errors_df_empty,
            errors_df_rows=errors_df_rows,
        )

    return render_template("key_excel_upload.html")


# Конвертация таблицы автозамены в формат .gbl
@converter_bp.route("/excel_key_upload", methods=["GET", "POST"])
def upload_excel_key_file():
    if request.method == "POST":
        # Получаем файл
        file_2 = request.files.get("file_2")

        # Безопасное имя файла
        filename = secure_filename(file_2.filename)
        save_path = Path(TEMP_SD_DIR) / filename

        # Сохранение файла на диск
        file_2.save(save_path)

        # Конвертертируем отредактированную ТА в задания для глобальной корректировки
        df_result, new_terms, spec = key_decoder(file_path=save_path, tgt_dir=OUTPUT_GBL_DIR)
        
        # Обновляем основной файл для ТА
        if spec == '02':
            SD_JSON_PATH = f"{SD_DIC_DIR}/02_SD/{spec}_SD_{today}.json"
            df_result.to_json(SD_JSON_PATH, orient='records', force_ascii=False, indent=2)
        elif spec == '04':
            SD_JSON_PATH = f"{SD_DIC_DIR}/04_SD/{spec}_SD_{today}.json"
            df_result.to_json(SD_JSON_PATH, orient='records', force_ascii=False, indent=2)

        # Добавляем новые термины
        add_terms(new_terms, spec)

        return redirect(url_for("converter.key_gbl_result"))

    return render_template("key_gbl_upload.html")

# -------------------------------------------------------
# Блок выводов
# -------------------------------------------------------

# Вывод результата конвертациии html файлов в таблицу
@converter_bp.route("/html_result")
def html_result():
    excel_files = list(Path(EDITABLE_XLSX_DIR).glob("*.xlsx"))

    return render_template("html_result.html", excel_files=excel_files)

# Вывод результата конвертациии excel в .txt файл, предназначенный для импорта в ИРБИС
@converter_bp.route("/excel_result")
def excel_result():
    txt_files = list(Path(IRBIS_OUTPUT_DIR).glob("*.txt"))

    return render_template("excel_result.html", txt_files=txt_files)

# Вывод дополненной таблицы автозамены
@converter_bp.route("/key_excel_result")
def key_excel_result():
    # Преобразуем в список строк (имена файлов), чтобы шаблону было удобно
    excel_files = [f.name for f in Path(TEMP_SD_DIR).glob("*.xlsx")]
    return render_template("key_excel_result.html", excel_file=excel_files)

# Вывод финального файла конвертации файла в формате .gbl
@converter_bp.route("/key_result")
def key_gbl_result():
    gbl_file = Path(OUTPUT_GBL_DIR).glob("*.gbl")

    return render_template("key_gbl_result.html", gbl_file=gbl_file)

# -------------------------------------------------------
# Блок скачиваний
# -------------------------------------------------------

# Скачивание списка статей
@converter_bp.route("/download_articles/<path:filename>")
def download_article_list(filename):
    return send_from_directory(EDITABLE_XLSX_DIR, filename, as_attachment=True)

# Скачивание файлов для импорта в ИРБИС
@converter_bp.route("/download_txt_list/<path:filename>")
def download_txt_list(filename):
    return send_from_directory(IRBIS_OUTPUT_DIR, filename, as_attachment=True)

# Скачивание файла в формате Excel
@converter_bp.route("/download_excel/<path:filename>")
def download_excel_file(filename):
    file_path = Path(TEMP_SD_DIR) / filename
    if not file_path.is_file():
        abort(404)
    return send_from_directory(TEMP_SD_DIR, filename, as_attachment=True)

# Скачивание файла в формате .gbl
@converter_bp.route("/download_gbl/<path:filename>")
def download_gbl_file(filename):
    return send_from_directory(OUTPUT_GBL_DIR, filename, as_attachment=True)