venv:
	@eval mkdir -p venv
	@eval python3 -m venv venv --clear
	@eval . venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

clean:
	@eval rm -rf venv

run:
	@eval . venv/bin/activate && python wg_wol_relay.py