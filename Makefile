SOURCE_DIR=farkelbot
VENV_DIR?=.venv

default:
	python setup.py check build

.PHONY: clean venv setup teardown lint test

$(VENV_DIR)/bin/activate: requirements.txt
	test -d $(VENV_DIR) || virtualenv --python=python2.7 --system-site-packages $(VENV_DIR)
	. $(VENV_DIR)/bin/activate; pip install -r requirements.txt
	touch $(VENV_DIR)/bin/activate

clean:
	python setup.py clean
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg/
	rm -f MANIFEST
	rm -rf __pycache__/
	find $(SOURCE_DIR) -type f -name '*.pyc' -delete

venv: $(VENV_DIR)/bin/activate

setup: venv

teardown:
	rm -rf $(VENV_DIR)

test: setup
	. $(VENV_DIR)/bin/activate; py.test
