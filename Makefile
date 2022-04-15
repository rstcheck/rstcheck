default: check test


# These checkers are more obscure. So consider them optional. Only run them if
# they are installed.
CHECK_MANIFEST := $(shell command -v check-manifest 2> /dev/null)
SCSPELL := $(shell command -v scspell 2> /dev/null)


check:
	tox -e pre-commit
	./rstcheck.py README.rst
ifdef CHECK_MANIFEST
	$(CHECK_MANIFEST)
endif
ifdef SCSPELL
	$(SCSPELL) rstcheck.py README.rst
endif


test:
	./test_rstcheck.py
	time ./test.bash


readme:
	@restview --long-description --strict


.PHONY: check test readme
