
SPHINXBUILD ?= sphinx-build
SPHINXOPTS ?=
SOURCEDIR := source
BUILDDIR := build

.PHONY: help
help:
	@$(SPHINXBUILD) -M help $(SPHINXOPTS) $(O) _ _

%:
	@$(SPHINXBUILD) -M $@ $(SPHINXOPTS) $(O) "$(SOURCEDIR)" "$(BUILDDIR)"
