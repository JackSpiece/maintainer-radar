.PHONY: test sample lint typecheck

test:
	PYTHONPATH=src python -m unittest discover -s tests

sample:
	PYTHONPATH=src python -m maintainer_radar from-json examples/sample-prs.json

lint:
	ruff check src tests

typecheck:
	mypy src
