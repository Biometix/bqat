# Wrapping up this commit and bumping version
echo "__version__ = '$1'" > bqat/__init__.py
poetry version "$1"

poetry build --format wheel
pytest --junitxml=reports/junit/junit.xml --html=reports/junit/report.html
genbadge tests -o reports/junit/tests-badge.svg
coverage run -m pytest
coverage xml -o reports/coverage/coverage.xml
coverage html -d reports/coverage/
genbadge coverage -o reports/coverage/coverage-badge.svg

#tox
#git tag v"$1"
#git push --tags