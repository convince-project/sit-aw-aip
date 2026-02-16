##SIT-AW  Copyright (C) CEA 2025  Razane Azrou
FROM python:3.12-slim

# Install dependencies (C compiler)
RUN apt-get update && \
    apt-get install -y build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV GPU_MEMORY_USAGE=$GPU_MEMORY_USAGE \
    PORT=$PORT \
    MODEL=$MODEL \
    DOWNLOAD_MODEL_CACHE_DIR=$DOWNLOAD_MODEL_CACHE_DIR

RUN pip install --no-cache-dir --upgrade pip
RUN pip install vllm==0.9.0
RUN pip install transformers==4.52.0

# Command to run the service
CMD vllm serve $MODEL --host 0.0.0.0 --port $PORT --download_dir $DOWNLOAD_MODEL_CACHE_DIR --gpu-memory-utilization $GPU_MEMORY_USAGE
