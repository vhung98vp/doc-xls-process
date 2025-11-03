import os
from .funcs import convert_to_new_format, read_docx, read_xlsx, read_csv, read_txt, make_avatar_file
from .utils import content_to_text, build_doc_uid
from s3 import WClient
from config import get_logger, KAFKA
logger = get_logger(__name__)


def upload_avatar(file_path, filename, doc_id):
    try:
        avatar_key = os.path.join(doc_id, f"{filename}_avatar.png")
        upload_key = WClient.upload_file(file_path, avatar_key)
        logger.info(f"Uploaded avatar to {upload_key}")
        return upload_key
    except Exception as e:
        logger.exception(f"Error uploading avatar for {file_path}: {e}")
        return None


def process_file(file_path, detect_type=2, s3_key=""):
    logger.info(f"Processing file: {file_path} from {'local' if not s3_key else 'S3'}...")
    filename = os.path.basename(file_path)
    _, ext = os.path.splitext(filename)
    ext = ext.lower()
    file_content, title, avatar_key = [], "", ""
    doc_id = build_doc_uid(s3_key)

    try:
        file_path = convert_to_new_format(file_path)
        if ext in [".doc", ".docx"]:
            file_content = read_docx(file_path)
        elif ext == ".txt":
            file_content = read_txt(file_path)
        elif ext in [".xls", ".xlsx"]:
            file_content = read_xlsx(file_path)
        elif ext == ".csv":
            file_content = read_csv(file_path)
        else:
            logger.error(f"Unsupported file type: {file_path}")
            return None
        
        full_text, ids, table_ids = content_to_text(file_content)
        result = {
                "file_name": filename,
                # "title": title,
                "content": file_content,
                "full_text": full_text,
                "ids": ids,
                "table_ids": table_ids,
            }
        
        if s3_key:
            avatar_path = make_avatar_file(file_path)
            avatar_key = upload_avatar(file_path, filename, doc_id)
            result.update({
                KAFKA["doc_id_key"]: doc_id,
                "s3_path": s3_key,
                "avatar": avatar_key,
            }) 

        return result
    except Exception as e:
        logger.exception(f"Error processing file {file_path}: {e}")
    finally:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            if os.path.exists(avatar_path):
                os.remove(avatar_path)
        except Exception as e:
            logger.warning(f"Error cleaning up temporary files: {e}")