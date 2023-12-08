FROM python:3.10.5
COPY requirements.txt .

RUN export PIP_DEFAULT_TIMEOUT=100

RUN apt-get install g++
RUN apt-get update && apt-get upgrade -y && apt-get install gcc

RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

COPY . /getIdWithUsername
WORKDIR /getIdWithUsername

EXPOSE 443

CMD ["python", "-m", "main"]