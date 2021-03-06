import itertools
from datetime import datetime

import numpy as np
import pandas as pd
from boltons.iterutils import windowed_iter
from logzero import logger as log
from pandas.core.frame import DataFrame

from utils import fixurl, text_stats, countnz


def gendeltas(timestamps_object, objname, seconds=False, dataframe=False):
    """Generates a column with time deltas calculated from the current
    and previous timestamp value. First timedelta is always 0"""
    deltaidx = pd.RangeIndex(0, len(timestamps_object), name="align")
    a = datetime.now()
    if seconds:
        zerodelta = 0
    else:
        zerodelta = a - a
    deltas = [zerodelta]
    for old, new in windowed_iter(timestamps_object, 2):
        # _, old,  _ = older
        # _, new,  _ = newer
        deltatime = datetime.fromisoformat(str(new)) - datetime.fromisoformat(str(old))
        if seconds:
            deltatime = deltatime.total_seconds()
        if deltatime >= zerodelta:
            deltas.append(deltatime)
        else:
            deltas.append(zerodelta)
    deltasS = pd.Series(deltas, name=objname)
    if DataFrame:
        return pd.DataFrame(deltasS, index=deltaidx)
    else:
        return deltasS


def fixtype(data, title, ordinal):
    """augments the message data object with calculated values from
    the messages own data. This is necessary to have a correctly typed index
    so we cast datetime.datetime from elegrams mercifully chosen ISO date string
    We also fix the url in file and photo fields in order to be able to display
    this data, you may need to customize the output to your chosen storage
    facility, Currently set up for Google Cloud Storage buckets.
    """
    newdata = data.copy()
    newdata["conversation"] = title
    newdata["date"] = datetime.fromisoformat(data["date"])
    if "from" in data.keys():
        newdata["user"] = data["from"]
    if "photo" in data.keys():
        newdata["photo"] = fixurl(data["photo"])
    if "file" in data.keys():
        newdata["file"] = fixurl(data["file"])
    if "text" in data.keys() and len(data["text"]) > 0:
        newdata["wordcount"] = text_stats(data["text"])
    newdata["align"] = ordinal
    return newdata


default_agg = {
    "from": countnz,
    "id": countnz,
    "photo": countnz,
    "reply_to_message_id": countnz,
    # 'text':'string',
    "wait_time": np.average,
    "wordcount": np.sum,
}

default_cast = {
    "conversation": "string",
    "from": "string",
    "date": "datetime64[ns]",
    "id": "Int64",
    "photo": "string",
    "reply_to_message_id": "Int64",
    "text": "string",
    "wait_time": "float",
    # "wait_time": "timedelta64[ns]", #use this to get pandas timedeltas
    "wordcount": "Int64",
}


def create_dataframe(src, typecasts=default_cast, aggregators=default_agg):
    """Creates as dataframe containing chat info

    Parameters:
        src: a data generator with Teleram chat data
        casts: a dictionary of fields: types
        aggregators: a dictionary of fields:aggregating function

    Returns:
        dataframe: conforming to fields declared in casts
        with funcions for aggregation assigned according to
        the aggregators array
    """
    log.debug("entering create_dataframe()")
    # duplicate datastream from generator so you dont need to reset it
    # when datastream is exhausted.
    for_dataframe, for_fields = itertools.tee(src)
    # fielder is a dataframe with all columns. its purpose is to generate
    # column lists via inclusion or exclusion from a subset
    fielder = pd.DataFrame.from_records(
        [m for m in for_fields],
        index=["align"],
    )  # use the dataframe for field masking agains the list we know we need
    # excluded_fields = (
    # [excl for excl in fielder.columns if excl not in typecasts.keys()],
    # )
    # build a new dataframe using the for_dataframe duplicated stream, add an
    # add an index called allign so we can add new columns in their corresponding
    # places.
    df = pd.DataFrame.from_records([m for m in for_dataframe], index=["align"],).fillna(
        np.nan
    )  # empty fields get np.nan as a value
    # now create a deltas vectpr by walking thrugh the column of datetimes
    if typecasts["wait_time"] == "float":
        seconds = True
    deltas = gendeltas(df.date, "wait_time", seconds)  # when seconds ins false
    # you get a column of pandas ditmedelta types, otherwise total seconds
    # do the deed
    ddf = (
        df.join(  # joining
            deltas,  # te deltas vector ... you get the idea
            on="align",
        )
        .astype(typecasts)
        .sort_index()
    )
    return ddf
