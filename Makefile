check:
	pep8 rstcheck.py setup.py
	pylint \
		--reports=no \
		--disable=bad-continuation \
		--disable=import-error \
		--disable=locally-disabled \
		--disable=no-member \
		--disable=not-callable \
		--disable=too-few-public-methods \
		--disable=too-many-arguments \
		--disable=undefined-variable \
		--function-rgx='[a-z_][a-z0-9_]{2,50}$$' \
		--rcfile=/dev/null \
		rstcheck.py setup.py
	check-manifest
	python setup.py --long-description | ./rstcheck.py -
	scspell rstcheck.py setup.py README.rst
	./rstcheck.py README.rst

readme:
	@restview --long-description --strict
