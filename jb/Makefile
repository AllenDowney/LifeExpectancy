# Makefile for building and deploying the Jupyter Book (MyST) site

.PHONY: help figs build build-local clean deploy serve

help:
	@echo "Available commands:"
	@echo "  make figs         - Copy the figures and tables the site uses from ../notebooks"
	@echo "  make build        - Build the site for GitHub Pages"
	@echo "  make build-local  - Build without a base URL (local serve)"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make deploy       - Build and deploy to GitHub Pages"
	@echo "  make serve        - Build locally and serve at http://localhost:8000"

figs:
	python sync_figs.py

# postbuild.py fixes the site address (the theme writes localhost), adds canonical
# links, rewrites the sitemap, and adds the page-view counter.
build:
	rm -rf _build/html
	BASE_URL=/LifeExpectancy/ jupyter book build --html
	touch _build/html/.nojekyll
	python postbuild.py _build/html

build-local:
	jupyter book build --html

clean:
	rm -rf _build

deploy: build
	ghp-import -n -p -f _build/html

serve: build-local
	cd _build/html && python -m http.server 8000
