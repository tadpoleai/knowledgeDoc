<<<<<<< HEAD
#FROM python:3.9-slim
#FROM ubuntu:20.04
=======

>>>>>>> 9bc4c07bc8e161d7dec7336c4124fb8ee0d65893
FROM python:3.9.10-buster

ENV DEBIAN_FRONTEND=noninteractive

<<<<<<< HEAD
#RUN APT_INSTALL="apt-get install -y --no-install-recommends --allow-unauthenticated" && \
#    apt-get update && \
#    DEBIAN_FRONTEND=noninteractive $APT_INSTALL

=======
>>>>>>> 9bc4c07bc8e161d7dec7336c4124fb8ee0d65893
ENV APP /app
ENV PORT 3006
WORKDIR $APP

RUN apt-get update && apt-get install -y --no-install-recommends --allow-unauthenticated \
    build-essential \
    curl \
    software-properties-common \
    git \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# for deploy to produce
#RUN git clone https://github.com/tadpoleai/knowledgeDoc.git --branch streamlit .

# for local test
COPY . .

RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

EXPOSE $PORT
HEALTHCHECK CMD curl --fail http://localhost:$PORT/_stcore/health
ENTRYPOINT ["streamlit", "run", "streamlit_ui.py", "--server.port=3006", "--server.address=0.0.0.0"]
