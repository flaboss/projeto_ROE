pipeline_run:
	python ./modules/main.py

container:
	docker run -it -v ${PWD}:/home/ flvbssln/roe_deepnote:v1 /bin/bash 

format:
	black *.py

lint:
	pylint --disable=R,C *.py

requirements:
	pip install -r requirements.txt