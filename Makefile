.PHONY: install run-all ingestion training scoring deployment reporting apicalls fullprocess

install:
	pip install -e .

run-all:
	dras run-all

ingestion:
	dras run-step --name ingestion

training:
	dras run-step --name training

scoring:
	dras run-step --name scoring

deployment:
	dras run-step --name deployment

reporting:
	dras run-step --name reporting

apicalls:
	dras run-step --name apicalls

fullprocess:
	dras run-step --name fullprocess
