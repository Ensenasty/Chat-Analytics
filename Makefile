#!/usr/bin/env make

BYPRODUCTS != find . -name __pycache__ | grep -v .venv
BYPRODUCTS += .build .init __pycache__ .reqs
CLOUDIGNORES = README.md LICENSE
VENV      = . .venv/bin/activate &&

DATADIRS  = Ensenada-20210917/ ensenadaBC-20210917/ sexEnsenadaFinal/json/ 
DATADIRS += usana-20210917/ valechat-20210907/ valechat-sddy-20210915/
DATADIRS += ensenasty-20210920/ latinparty-20200920/
PROJECT = telegramops

SRC != find . -name \*.py | grep -v .venv
SRC += Makefile

DATA = data.json
BASEDIR = ~/Downloads/TelegramDesktop/
DATASETS := $(addprefix $(BASEDIR), $(DATADIRS))
DATAFILES := $(addsuffix result.json,$(DATASETS))


vpath %.py . tgstats:tgstats/etl

ifndef PROJECT
$(error define ·$$PROJECT in your environment)
$(error define ·$$DATADIRS in your environment)
endif

.PHONY: clean devenv default reqs

.SUFFIXES:
.SUFFIXES: py

all: $(DATA) $(CLOUDIGNORES)

default:: clean
default:: $(DATA)

devenv: reqs .cloudignore

reqs: .reqs

data: data.json $(SRC)

.reqs: requirements.txt .venv/bin/activate
	$(VENV) pip install --upgrade pip wheel
	$(VENV) pip install -r requirements.txt
	touch $@

.venv/bin/activate:
	python3 -m venv .venv
	
.cloudignore: .gitignore $(CLOUDIGNORES)
	cp $< $@
	echo $(CLOUDIGNORES)
	for f in $(CLOUDIGNORES);  do  echo $$f >> $@ ; done
	
.dockerignore: $(DOCKERIGNORES)

clean:
	-rm -rf $(BYPRODUCTS)
	-rm -rf $(DATA)

$(DATA): $(DATAFILES)
	$(VENV) python prog.py $^


%:

,end="\r"
#  d(-_-;)bm  hlo.mx 1631907303
#  vim:  ts=4 sw=0 tw=80 noet :                    