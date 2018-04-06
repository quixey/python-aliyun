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

VENV_NAME = django_proj
VENV_PATH = ~/Envs/$(VENV_NAME)
VENV_ACTIVATE = . $(VENV_PATH)/bin/activate

BUILD=0
all: clean test

clean:
	rm -rf python-aliyun*.deb build *.egg-info *.egg
	find . -name '*.py[co]' -exec rm {} \;
	mkdir build

virtualenv:
	test -d $(VENV_PATH) || virtualenv $(VENV_PATH)
	$(VENV_ACTIVATE) && \
          sudo apt-get install openssl && \
          easy_install setuptools && \
          pip install -U pip sphinxcontrib-programoutput pyopenssl ndg-httpsclient pyasn1 && \
          pip -V && \
          python setup.py --quiet develop
	rm -rf python-aliyun.egg-info

test: clean
	mkdir -p build
	python ./setup.py nosetests
	mv *.egg-info build/

functionaltest:
	mkdir -p build
	python ./setup.py nosetests -w tests/functional/readonly.py
	mv *.egg-info build/

deb: test
	mkdir -p build
	fpm -s python -t deb --deb-user root --deb-group root --deb-no-default-config-files --iteration=$(BUILD) .
	rm -rf *.egg-info
	mv *.deb build/

docs: test
	sphinx-apidoc --separate --full -H "python-aliyun" -A "Adam Gray, Akshay Dayal, North Bits" . -o docs/
	rm -rf docs/tests* docs/setup*
	python ./setup.py build_sphinx -a -s docs --build-dir docs
