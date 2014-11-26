check:
	pep8 rstcheck.py setup.py
	pylint \
		--reports=no \
		--disable=bad-continuation \
		--disable=locally-disabled \
		--disable=no-member \
		--disable=too-few-public-methods \
		--disable=too-many-arguments \
		--rcfile=/dev/null \
		rstcheck.py setup.py
	check-manifest
	python setup.py --long-description | \
		rstcheck --ignore=cpp,python,rst -
	scspell rstcheck.py setup.py README.rst
	./rstcheck.py --ignore=cpp,python,rst README.rst

readme:
	@restview --long-description --strict
