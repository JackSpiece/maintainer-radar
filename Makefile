.PHONY: test sample

test:
	PYTHONPATH=src python -m unittest discover -s tests

sample:
	PYTHONPATH=src python -m maintainer_radar from-json examples/sample-prs.json
