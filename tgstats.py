# -*- coding: utf-8 -*-
"""TGroup_Stats.ipynb

# Telegram chat analytics with Pandas

This notebook is still a work in progress. we can now proces the machine
readable json from a chat export file created with Telegram desktop. 
"""


for fn in uploaded.keys():
    print(
        'User uploaded file "{name}" with length {length} bytes'.format(
            name=fn, length=len(uploaded[fn])
        )
    )

"""# Data Processing

make  lazy json loader and use it to feed a pandas dataframe.
This dataframe will get transformed in a variety o ways for analysis

### Helper Functions

#### Module imports
"""

import itertools
import json
import math
import numpy as np
import pandas as pd
import re
import matplotlib.pyplot as plt

plt.close("all")

from boltons.iterutils import flatten
from boltons.iterutils import windowed_iter
from datetime import datetime
from logzero import logger as log

"""####
 Agregator functions
"""

regex = re.compile(r"type\s+text\s+")


def fixurl(txt):
    ...
    return txt


def text_stats(txt):
    if isinstance(txt, list):
        txt = regex.sub(
            "", " ".join(flatten(txt)), count=len(regex.findall(" ".join(flatten(txt))))
        )
    wordcount = len(txt.split(" "))
    ...
    return wordcount


def countnz(arr):
    return len([val for val in arr if not pd.isna(val)])


def deltaaverage(arr):
    sum = 0
    narr = [val.seconds for val in arr if not pd.isna(val)]
    if len(narr) > 0:
        for e in narr:
            sum += e
        return sum / (len(narr) * 1.0)
    else:
        return 0


"""#### A Deltas Generator

"""


def gendeltas(timestamps_object, objname):
    """Generates a column with time deltas calculated from the current
    and previous timestamp value. First timedelta is always 0"""
    deltaidx = pd.RangeIndex(0, len(timestamps_object), name="align")
    a = datetime.now()
    deltas = [a - a]
    for old, new in windowed_iter(timestamps_object, 2):
        # _, old,  _ = older
        # _, new,  _ = newer
        deltatime = datetime.fromisoformat(str(new)) - datetime.fromisoformat(str(old))
        if deltatime >= (a - a):
            deltas.append(deltatime)
        else:
            deltas.append(a - a)
    deltasS = pd.Series(deltas, name=objname)
    return deltasS
    # return pd.DataFrame(deltasS, index=deltaidx)


"""#### Text analysis helper funcions"""


def fixtype(msgdict):
    """augments the message data object with calculated values from
    the messages own data. This is necessary to have a correctly typed index
    so we cast datetime.datetime from elegrams mercifully chosen ISO date string
    We also fix the url in file and photo fields in order to be able to display
    this data, you may need to customize the output to your chosen storage
    facility, Currently set up for Google Cloud Storage buckets.
    """

    newmsg = msgdict.copy()
    newmsg["date"] = datetime.fromisoformat(msgdict["date"])
    if "photo" in msgdict.keys():
        newmsg["photo"] = "fixurl({})".format(msgdict["photo"])
    if "file" in msgdict.keys():
        newmsg["file"] = "fixurl({})".format(msgdict["file"])
    if "text" in msgdict.keys() and len(msgdict["text"]) > 0:
        newmsg["wordcount"] = text_stats(msgdict["text"])
    return newmsg


def addidx_fixtype(data, ordinal):
    """a shim to create an indexable column for the main dataframe, we want
    to keep fixtype() as generic as possible"""
    newdata = fixtype(data)
    newdata["align"] = ordinal
    return newdata


"""### Main processing

##### Important Constants
"""

aggregators = {
    "from": countnz,
    "id": countnz,
    "photo": countnz,
    "reply_to_message_id": countnz,
    # 'text':'string',
    "wait_time": deltaaverage,
    "wordcount": np.sum,
}

typecasts = {
    "from": "string",
    "date": "datetime64[ns]",
    "id": "Int64",
    "photo": "string",
    "reply_to_message_id": "Int64",
    "text": "string",
    "wait_time": "timedelta64[ns]",
    "wordcount": "Int64",
}

"""#### This is where the saussage is made"""


def data_generator():
    all_messages = []
    rowct = 0
    for f in uploaded:
        with open(f, "r", encoding="utf8") as chat:
            conversation = json.load(chat)
            for msg in conversation["messages"]:
                all_messages.append(addidx_fixtype(msg, rowct))
                rowct += 1
    return (msg for msg in all_messages)


src = data_generator()
for_dataframe, for_fields = itertools.tee(src)

fielder = pd.DataFrame.from_records(
    [m for m in for_fields],
    index=["align"],
)

df = pd.DataFrame.from_records(
    [m for m in for_dataframe],
    index=["align"],
    exclude=[excl for excl in list(fielder.columns) if excl not in typecasts.keys()],
)

df.fillna(np.nan, inplace=True)
deltas = gendeltas(df.date, "wait_time")
ddf = (
    df.join(
        deltas,
        on="align",
    )
    # .droplevel("align")
    .astype(typecasts).sort_index()
)

ddf.info()

"""### Have a go analyzing the data on bigquery"""

import os

dataset = os.environ["BQDATASET"]
project = os.environ["GCPPROJECT"]
schema = [
    {"name": "id", "type": "INTEGER", "mode": "NULLABLE"},
    {"name": "text", "     type": "STRING", "mode": "NULLABLE"},
    {"name": "wordcount", "type": "INTEGER", "mode": "NULLABLE"},
    {"name": "reply_to_message_id", "type": "INTEGER", "mode": "NULLABLE"},
    {"name": "photo", "    type": "STRING", "mode": "NULLABLE"},
    {"name": "wait_time", "type": "STRING", "mode": "NULLABLE"},
]

ts = ddf.to_gbq(
    "{}".format(dataset),
    project_id="{}".format(project),
    if_exists="replace",
    table_schema=schema,
)

"""## Visualizations derived from the built dataframe"""

ts = ddf
ts.reindex(ts["date"])
daily = ts.resample("D")
daily.agg(sum)
