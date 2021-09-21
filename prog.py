import sys
import fire
from logzero import logger as log

sys.path.append("./tgstats")
sys.path.append("./tgstats/etl")


from tgstats.etl.extract import extract
from tgstats.etl.load import bigquery

if __name__ == "__main__":

    # bigquery(extract())
    bigquery("./data.json")
    log.info('all done')


#  d(-_-;)bm  hlo.mx 1632006243
#  vim:  ts=4 sw=4 tw=80 et :
