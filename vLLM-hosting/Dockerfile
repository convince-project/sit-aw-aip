#SIT-AW  Copyright (C) CEA 2025  Razane Azrou
FROM python:3.12-slim

#install dependencies (c compiler it seems)
RUN apt-get update && \
apt-get install -y build-essential && \
apt-get clean && \
rm -rf /var/lib/apt/lists/*

#variables than can be set in run time
ENV GPU_MEMORY_USAGE=0.85
ENV PORT=23333
ENV MODEL=Qwen/Qwen2.5-VL-7B-Instruct

RUN pip install --no-cache-dir --upgrade pip
RUN pip install vllm==0.9.0
RUN pip install transformers==4.52.0

EXPOSE $PORT

#you can change the value of the port if you want
CMD vllm serve $MODEL --host 0.0.0.0 --port $PORT --download_dir /root/.cache/huggingface --gpu-memory-utilization $GPU_MEMORY_USAGE











