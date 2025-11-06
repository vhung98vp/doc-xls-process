import uuid
from .pattern import filter_id, filter_ids_text
from config import KAFKA


### UTILS ###
def build_doc_uid(s3_key, entity_type=KAFKA['doc_entity_type'], namespace=KAFKA['namespace_uuid']):
    return str(uuid.uuid5(namespace, f"{entity_type}:{s3_key}"))

def get_table_ids(cell_info):
    table = [[filter_id(text) if text else "" for text in row] for row in cell_info]
    cols_with_text = {j for i, row in enumerate(table) for j, text in enumerate(row) if text != ""}
    cols = sorted(cols_with_text)
    # Filer rows and cols without text

    filtered = [[row[j] for j in cols] for row in table]
    result = [row for row in filtered if any(cell != "" for cell in row)]
    return result if result and len(result[0]) > 1 else []

def content_to_ids(content):
    # texts = []
    ids = []
    table_ids = []
    for item in content:
        if 'cells' in item:
            # texts.append('\n'.join(['|'.join(row) for row in item['cells']]))
            tid = get_table_ids(item['cells'])
            table_ids.extend(tid)
            ids.extend([i for row in tid for i in row if i])
        elif 'text' in item:
            # texts.append("\n".join(item.get('text', '')))
            ids.extend(filter_ids_text(item.get('text', '')))
        else:
            # texts.append(item)
            ids.extend(filter_ids_text(item))

    # full_text = '\n'.join(texts)
    ids = list(set(ids))
    return ids, table_ids