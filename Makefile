default: check test


check:
	pycodestyle rstcheck.py setup.py
	check-manifest
	python setup.py --long-description | ./rstcheck.py -
	scspell rstcheck.py setup.py README.rst
	./rstcheck.py README.rst


test:
	./test_rstcheck.py
	time ./test.bash


readme:
	@restview --long-description --strict


.PHONY: check test readme
