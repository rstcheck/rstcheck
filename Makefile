check:
	pep8 rstcheck.py setup.py
	pep257 rstcheck.py setup.py
	pylint \
		--reports=no \
		--disable=no-member \
		--rcfile=/dev/null \
		rstcheck.py setup.py
	check-manifest
	python setup.py --long-description | rst2html --strict > /dev/null
	scspell rstcheck.py setup.py README.rst

readme:
	@restview --long-description --strict
