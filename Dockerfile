FROM python:3.7.6-slim-buster

# RUN pip install --upgrade pip \
#     && pip install pipenv

# ENV FTA=/family-tree-api
# WORKDIR ${FTA}

# COPY Pipfile* ./

# RUN pipenv install --deploy --ignore-pipfile
# COPY family_tree family_tree/
# COPY manage.py .

# CMD ["pipenv", "run", "python", "manage.py"]


ENV DA=/data-aggregator
WORKDIR ${DA}

COPY requirements.txt requirements.txt

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"
RUN python3.7 -m venv ${VIRTUAL_ENV} && \
    pip install --upgrade pip && \
    pip install -r src/requirements.txt && \
    mkdir -v files/

COPY . .

CMD python src/app.py