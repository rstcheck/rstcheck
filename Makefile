check:
	pep8 rstcheck.py setup.py
	check-manifest
	python setup.py --long-description | ./rstcheck.py -
	scspell rstcheck.py setup.py README.rst
	./rstcheck.py README.rst

readme:
	@restview --long-description --strict
