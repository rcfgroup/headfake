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
	rm -r dist
	python setup.py sdist
	python setup.py bdist_wheel

upload:
	twine check dist/*
	twine upload -r pypi dist/*

upload_test:
	twine check dist/*
	twine upload -r testpypi dist/*

