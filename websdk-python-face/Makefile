# 构建相关
build:
	python setup.py sdist bdist_wheel
	pip install $$(ls -t dist/*.tar.gz | head -n 1)

# 发布相关
publish:
	twine upload -u __token__ -p pypi-xxx-token dist/*

publish-test:
	twine upload -u __token__ -p pypi-xxx-token --repository-url https://test.pypi.org/legacy/ dist/*

# 测试相关
test:
	pytest tests/ -v

# 生成覆盖率报告（终端显示）
coverage:
	coverage run -m pytest tests/
	coverage report

# 生成覆盖率报告（HTML格式）
coverage-html:
	coverage run -m pytest tests/
	coverage html
	@echo "HTML coverage report generated in htmlcov/index.html"

# 生成覆盖率报告（XML格式，适用于CI/CD）
coverage-xml:
	coverage run -m pytest tests/
	coverage xml

# 使用 pytest-cov 生成覆盖率（推荐）
test-cov:
	pytest tests/ --cov=xfyunsdkface --cov-report=term-missing --cov-report=html --cov-report=xml

# 清理覆盖率文件
clean-coverage:
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf .pytest_cache/

# 清理构建文件
clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info

# 清理所有生成的文件
clean: clean-coverage clean-build
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

.PHONY: build publish publish-test test coverage coverage-html coverage-xml test-cov clean-coverage clean-build clean