FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# set path to out python api file
ENV MODULE_NAME="main.app"

# copy contents of project into docker
COPY ./ /app

# install poetry
RUN pip install poetry

# disable virtualenv for poetry
RUN poetry config virtualenv.create false

# install dependencies
RUN poetry install