user:
	python setup.py install --user

build:
	python setup.py build
	python setup.py sdist bdist_wheel

pypi:
	python -m twine upload --repository pypi dist/*

testpypi:
	python -m twine upload --repository testpypi dist/*
