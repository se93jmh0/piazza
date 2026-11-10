.PHONY:	lint unittests smoketest

all:	lint unittests

lint:
	black --line-length 79 --check .
	pyrefly check
	ruff check --preview

unittests:
	python -m pytest --verbose --cov
