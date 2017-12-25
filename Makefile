TITLE = teaching
BUILDDIR  = _build
TEX2PDF  := cd $(BUILDDIR) && TEXINPUTS="../_static:" pdflatex -shell-escape #-interaction=batchmode
BIBTEX   := cd $(BUILDDIR) && bibtex

all: clean $(TITLE)

clean:
	rm -rf $(BUILDDIR)/* *.pdf

$(BUILDDIR):
	mkdir -p $@

$(BUILDDIR)/%.pdf: %.tex
	($(TEX2PDF) $(<F) 1>/dev/null)


$(TITLE): $(TITLE).tex $(BUILDDIR)
	cp *.tex $(BUILDDIR)/.
	cp $(TITLE).bib $(BUILDDIR)/.
	cp _static/*.jpg $(BUILDDIR)/.
	cp _static/*.bst $(BUILDDIR)/.
	($(TEX2PDF) $(TITLE).tex)
	($(BIBTEX) $(TITLE))
	($(TEX2PDF) $(TITLE).tex)
	($(TEX2PDF) $(TITLE).tex)
	cp $(BUILDDIR)/$(@).pdf $(@).pdf 
