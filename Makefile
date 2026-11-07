.PHONY:	check

check:
	black --check .
	pyrefly check
	ruff check --preview
