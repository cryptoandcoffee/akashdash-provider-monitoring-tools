FROM python:3.9-alpine

RUN apk add --no-cache \
    kubectl \
    curl \
    socat \
    bc \
    jq

WORKDIR /app

RUN pip install kubernetes requests

COPY ./house_cleaner1.py .

CMD ["python", "house_cleaner1.py"]
