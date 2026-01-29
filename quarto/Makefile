# Makefile for building and deploying Quarto site

.PHONY: help build clean deploy serve copy-notebook

help:
	@echo "Available commands:"
	@echo "  make build    - Build the Quarto site"
	@echo "  make clean    - Clean build artifacts"
	@echo "  make deploy   - Build and deploy to GitHub Pages"
	@echo "  make serve    - Build and serve locally"

copy-notebook:
	cp ../notebooks/bayesian_model_r.ipynb bayesian_model_r.ipynb

build: copy-notebook
	quarto render
	touch _site/.nojekyll

clean:
	rm -rf _site
	rm -f bayesian_model_r.ipynb

deploy: build
	ghp-import -n -p -f _site

serve: build
	cd _site && python -m http.server 8000

