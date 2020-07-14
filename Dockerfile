FROM python:3.8

ENV LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    PIPENV_USE_SYSTEM=1

WORKDIR /code
COPY Pipfile Pipfile.lock ./

RUN pip install --no-cache-dir --upgrade pip pipenv

ARG DEV="no"
ENV _DEV=${DEV}
RUN if [ "${DEV}" = "yes" ] ; \
        then pipenv install --system --dev; \
        else pipenv install --system; \
    fi

COPY . /code/counter
ENTRYPOINT ["python", "counter/import_IPFS.py"]
