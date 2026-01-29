.PHONY: env delete_env update_env clean lint format tests ipynb md

PROJECT_NAME = LifeExpectancy

# Environment management (using mamba for speed)
env:
	mamba env create -f environment.yml
	@echo "Installing R kernel for Jupyter..."
	mamba run -n $(PROJECT_NAME) R -e "IRkernel::installspec()"
	@echo ""
	@echo ">>> Environment ready. Activate with:"
	@echo ">>> conda activate $(PROJECT_NAME)"

delete_env:
	mamba env remove --name $(PROJECT_NAME)

update_env:
	mamba env update -f environment.yml --prune

# Notebook conversion (jupytext)
ipynb:
	@echo "Converting md files to ipynb..."
	@for md_file in notebooks/*.md; do \
		base=$$(basename $$md_file .md); \
		echo "Converting $$md_file to notebooks/$$base.ipynb"; \
		jupytext --to ipynb $$md_file --output notebooks/$$base.ipynb; \
	done
	@echo "Conversion complete!"

md:
	@echo "Converting ipynb files to md (overwriting)..."
	@for ipynb_file in notebooks/*.ipynb; do \
		base=$$(basename $$ipynb_file .ipynb); \
		echo "Converting $$ipynb_file to notebooks/$$base.md"; \
		jupytext --to md $$ipynb_file --output notebooks/$$base.md; \
	done
	@echo "Conversion complete!"

# Code quality
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

lint:
	flake8 notebooks/*.py
	black --check notebooks/*.py

format:
	black notebooks/*.py

# Testing
tests:
	pytest --nbmake notebooks/*.ipynb
