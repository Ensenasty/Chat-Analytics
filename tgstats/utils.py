import re
import numpy as np
import pandas as pd
from boltons.iterutils import flatten


regex = re.compile(r"type\s+text\s+")
notincluded = re.compile(r"\(File not included\. Change data")


def filterdispatch(txt):
    """should return a False or None when item is not
    to be included, the value of txt otherwise"""
    if notincluded.match(txt):
        return "data not exported."

    return txt


def fixurl(txt):
    return "gs://chatanalytics/datasets/{}".format(txt)


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


def extract(val):
    if isinstance(val, int):  # seconds
        return val
    else:
        return val.total_seconds  # timedelta


def deltaaverage(arr):
    sum = 0
    narr = [extract(val) for val in arr if not pd.isna(val)]
    if len(narr) > 0:
        for e in narr:
            sum += e
        return sum / (len(narr) * 1.0)
    else:
        return 0
