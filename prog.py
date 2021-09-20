import sys
import fire

sys.path.append("./tgstats")
sys.path.append("./tgstats/etl")


from tgstats.etl.extract import extract

if __name__ == "__main__":

    fire.Fire(extract())


#  d(-_-;)bm  hlo.mx 1632006243
#  vim:  ts=4 sw=4 tw=80 et :
