PKG=pysub
TMP_FILE:=$(shell mktemp).img

~/.pysub:
	cp .pysub ~/.pysub

default: ~/.pysub
	python setup.py install
	-rm -rf dist build $(PKG).egg-info

install-pip: ~/.pysub
	pip install .
	-rm -rf dist build $(PKG).egg-info

.PHONY: install-full
install-full: ~/.pysub
	pip install -r requirements.txt
	pip install .
	-rm -rf dist build $(PKG).egg-info

.PHONY: install-dev
install-de: ~/.pysub
	pip install -r requirements
	pip install -e .[full]
	-rm -rf dist build $(PKG).egg-info

singularity/pysub_test.img:
	sudo singularity build $(TMP_FILE) singularity/Singularity
	cp $(TMP_FILE) singularity/$(PKG)_test.img
	sudo rm $(TMP_FILE)

.PHONY: tests
tests: singularity/pysub_test.img
	PY_MAJOR_VERSION=py`python -c 'import sys; print(sys.version_info[0])'` pytest --cov-report term-missing -v --cov=$(PKG) --cov-config=.coveragerc tests
	flake8 $(PKG)
