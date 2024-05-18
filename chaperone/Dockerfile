FROM python:3.9-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    bash \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && \
    chmod +x kubectl && \
    mv kubectl /usr/local/bin/

WORKDIR /app

RUN pip install kubernetes requests tqdm

COPY ./chaperone.py .

CMD ["python", "chaperone.py"]