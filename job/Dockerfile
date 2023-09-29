FROM python:3.10-slim
WORKDIR /root

RUN apt-get update && \
    apt-get -y install gcc libmariadb-dev

RUN pip install poetry
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false && poetry install

COPY . .

ENTRYPOINT ["python", "main.py"]
