#!/usr/bin/env make
i
BYPRODUCTS = .build .init __pycache__ .reqs
CLOUDIGNORES = README.md LICENSE
VENV      = . .venv/bin/activate &&

ifndef PROJECT
$(error define ·$$PROJECT in your environment)
$(error define ·$$DATADIRS in your environment)
endif

.PHONY: clean devenv default reqs

.SUFFIXES:
.SUFFIXES: py

default:: build
default:: deploy

devenv: reqs .cloudignore

reqs: .reqs

datafile: $(DATADIRS)

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
	rm -rf $(BYPRODUCTS)

%:


#  d(-_-;)bm  hlo.mx 1631907303
#  vim:  ts=4 sw=0 tw=80 noet :