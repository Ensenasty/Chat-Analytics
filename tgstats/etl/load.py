import os
from logzero import logger as log
from extract import data_generator

from transform import create_dataframe


def bigquery(
    datafile,
    dataset=os.environ["BQDATASET"],
    project=os.environ["GCPPROJECT"],
    schema=[
        {"name": "conversation", "type": "STRING"},
        {"name": "id", "type": "INTEGER"},
        {"name": "from", "type": "STRING"},
        {"name": "text", "type": "STRING"},
        {"name": "wordcount", "type": "INTEGER"},
        {"name": "reply_to_message_id", "type": "INTEGER"},
        {"name": "photo", "type": "STRING"},
        {"name": "wait_time", "type": "FLOAT"},
    ],
):

    log.info("creating bigquery dataset")
    src = data_generator(datafile)
    chatinfo = create_dataframe(src)
    ts = chatinfo.to_gbq(
        "{}".format(dataset),
        project_id="{}".format(project),
        if_exists="replace",
        table_schema=schema,
    )
    if ts:
        return True
    else:
        return False
