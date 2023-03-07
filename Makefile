# creates a docker container based on the image/docker file - for development purposes
container:
	docker run -it --rm -v ${PWD}:/home/ flvbssln/roe_deepnote:v1 /bin/bash

# install requirements - if needed
requirements:
	pip install -r requirements.txt
	pip install -e.

# runs the entire processing pipeline
pipeline_run:
	python ./modules/main.py

# runs tests
test:
	python3 ./modules/test/test_functions.py

# cleans execution/ compiled files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

# formats using black
format:
	black modules

# lints using flake8
lint:
	flake8 modules
