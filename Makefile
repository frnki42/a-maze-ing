VENV = .venv
VENV_PY = $(VENV)/bin/python
MARKER = $(VENV)/.stamp
CONFIG = config.txt
MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports \
			 --disallow-untyped-defs --check-untyped-defs

.PHONY: install run debug clean lint lint-strict

install: $(MARKER)

$(MARKER): requirements.txt
	python3 -m venv $(VENV)
	$(VENV_PY) -m pip install -r requirements.txt
	touch $(MARKER)

run: $(MARKER)
	$(VENV_PY) a_maze_ing.py $(CONFIG)

debug: $(MARKER)
	$(VENV_PY) -m pdb a_maze_ing.py $(CONFIG)

clean:
	rm -rf .mypy_cache __pycache__ */__pycache__

lint: $(MARKER)
	$(VENV_PY) -m flake8 .
	$(VENV_PY) -m mypy . $(MYPY_FLAGS)

lint-strict: $(MARKER)
	$(VENV_PY) -m flake8 .
	$(VENV_PY) -m mypy . --strict
