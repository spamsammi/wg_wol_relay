venv:
	@eval mkdir -p venv
# Specific version of python used is 3.9.2
ifeq ($(VERSIONED),true)
	@eval $(shell which python3.9) -m venv venv --clear
	@eval . venv/bin/activate && pip install --upgrade pip && pip install -r requirements-3.9.txt
else
	@eval python3 -m venv venv --clear
	@eval . venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
endif

clean:
	@eval rm -rf build dist *.spec

purge: clean
	@eval rm -r venv

run: venv
	@eval . venv/bin/activate && python wg_wol_relay.py

build: venv
	@eval . venv/bin/activate && pyinstaller --onefile wg_wol_relay.py

install: venv
	@eval bin/install.sh

uninstall:
	@eval bin/install.sh -u