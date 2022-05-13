pipeline_run:
	python ./modules/main.py

container:
	docker run -it -v ${PWD}:/home/ flvbssln/roe_deepnote:v1 /bin/bash 