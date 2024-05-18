FROM python:3.9-alpine

RUN apk add --no-cache \
    kubectl \
    curl \
    socat \
    bash

WORKDIR /app

RUN pip install kubernetes requests

COPY ./rpc_switch.py .

CMD ["python", "rpc_switch.py"]
