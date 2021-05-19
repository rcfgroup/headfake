.PHONY: docs build upload
.PHONY: venv

venv:
	python3 -m venv venv

serve_docs:
	mkdocs serve -a localhost:3000

build_docs:
	mkdocs build

deploy_docs:
	mkdocs gh-deploy


build:
	python setup.py sdist

upload:
	python setup.py sdist upload -r pypi
