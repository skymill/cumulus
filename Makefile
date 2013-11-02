gen-docs:
	pip install Sphinx
	cd docs; make html
install:
	python setup.py build
	python setup.py install
