gen-docs:
	pip install -r docs/requirements.txt
	cd docs; make html
install:
	python setup.py build
	python setup.py install
