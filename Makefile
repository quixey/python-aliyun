# Copyright 2014, Quixey Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.


MAKEFLAGS = --no-print-directory --always-make --silent
MAKE = make $(MAKEFLAGS)

VENV_NAME = python-aliyun
VENV_PATH = ~/.virtualenvs/$(VENV_NAME)
VENV_ACTIVATE = . $(VENV_PATH)/bin/activate

BUILD=0
all: clean test

clean:
	rm -rf build
	rm -rf python-aliyun*.deb build *.egg-info *.egg
	find . -name '*.pyc' -exec rm {} \;
	mkdir build

virtualenv:
	test -d $(VENV_PATH) || virtualenv $(VENV_PATH)
	$(VENV_ACTIVATE) && python setup.py --quiet develop
	rm -rf python-aliyun.egg-info

test: clean
	python ./setup.py nosetests --verbosity 2 --tests tests/unit --with-coverage --cover-package aliyun --cover-xml --cover-xml-file=build/coverage.xml
	mv *.egg-info build/
	rm .coverage

deb: test
	fpm -s python -t deb --deb-user root --deb-group root --iteration=$(BUILD) .
	rm -rf *.egg-info
	mv *.deb build/

docs: test
	sphinx-apidoc --separate --full -H "python-aliyun" -A "Adam Gray, Akshay Dayal, North Bits" . -o docs/
	rm -rf docs/tests* docs/setup*
	python ./setup.py build_sphinx -a -s docs --build-dir docs
