check:
	pep8 rstcheck.py setup.py
	pylint \
		--reports=no \
		--disable=bad-continuation \
		--disable=no-member \
		--rcfile=/dev/null \
		rstcheck.py setup.py
	check-manifest
	python setup.py --long-description | \
		rstcheck --report=1 --ignore=cpp,python -
	scspell rstcheck.py setup.py README.rst
	./rstcheck.py --ignore=cpp,python README.rst

readme:
	@restview --long-description --strict
