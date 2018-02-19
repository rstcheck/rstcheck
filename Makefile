default: check test


# These can be obscure so only use it if it is installed.
CHECK_MANIFEST := $(shell command -v check-manifest 2> /dev/null)
SCSPELL := $(shell command -v scspell 2> /dev/null)


check:
	pycodestyle rstcheck.py setup.py
	python setup.py --long-description | ./rstcheck.py -
	./rstcheck.py README.rst
ifdef CHECK_MANIFEST
	$(CHECK_MANIFEST)
endif
ifdef SCSPELL
	$(SCSPELL) rstcheck.py setup.py README.rst
endif


test:
	./test_rstcheck.py
	time ./test.bash


readme:
	@restview --long-description --strict


.PHONY: check test readme
