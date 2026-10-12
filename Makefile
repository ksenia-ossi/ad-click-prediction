PY ?= python3
export PYTHONPATH := src

.PHONY: data db-up db-load sql eda train test all

data:            ## download the official 100k-row Criteo sample
	$(PY) -m criteo_ctr.download

db-up:           ## start PostgreSQL in Docker
	docker compose up -d && sleep 3

db-load: db-up   ## create schema and COPY the sample into PostgreSQL
	$(PY) -m criteo_ctr.db load

sql:             ## run the exploration queries in src/criteo_ctr/sql/explore.sql
	$(PY) -m criteo_ctr.db explore

eda:             ## pandas EDA -> reports/figures/*.png + reports/eda.md
	$(PY) -m criteo_ctr.eda

train:           ## train baseline / logistic regression / LightGBM -> reports/metrics.md
	$(PY) -m criteo_ctr.train

test:
	$(PY) -m pytest -q

all: data db-load sql eda train test
