build:
	python setup.py sdist bdist_wheel
	pip install $$(ls -t dist/*.tar.gz | head -n 1)


publish:
	twine upload -u __token__ -p pypi-xxx-token dist/*

publish-test:
	twine upload -u __token__ -p pypi-xxx-token --repository-url https://test.pypi.org/legacy/ dist/*