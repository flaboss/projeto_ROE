FROM deepnote/python:3.7
WORKDIR /home/
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
