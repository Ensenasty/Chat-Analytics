import json
import fileinput
from logzero import logger as log
from transform import fixtype
from utils import filterdispatch


def data_generator(r):
    all_messages = []
    rowct = 0
    with open(r, "r", encoding="utf8") as chat:
        dataset = json.load(chat)
        for conversation in dataset:
            for msg in conversation["messages"]:
                all_messages.append(fixtype(msg, conversation["title"], rowct))
                rowct += 1
    return (msg for msg in all_messages)


def extract():
    total_lines = 0
    with open("data.json", "w+", encoding="utf8") as outfile:
        firstfile = True
        outfile.writelines("[")
        for line in fileinput.input():
            if fileinput.isfirstline():
                log.info(
                    "processing ....{}".format(
                        "/".join(fileinput.filename().split("/")[-2:])
                    )
                )
                if not firstfile:
                    outfile.writelines(",")
                firstfile = False
            line = filterdispatch(line)
            total_lines += 1
            if total_lines % 5000 == 0:
                print("{:12}\r".format(fileinput.lineno()), end="\r")
            if line:
                outfile.writelines(line)
        outfile.writelines("]")
