FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*


ENV CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS -DLLAMA_METAL=OFF -DLLAMA_CUDA_KQUANTS_ITER=1 -DLLAMA_CUBLAS=OFF"
ENV FORCE_CMAKE="1"
RUN pip install llama-cpp-python

COPY ./requirements.txt .
RUN python -m pip install -r requirements.txt

RUN cp /opt/conda/lib/python3.10/site-packages/bitsandbytes/libbitsandbytes_cuda117.so /opt/conda/lib/python3.10/site-packages/bitsandbytes/libbitsandbytes_cpu.so

WORKDIR /app
COPY . /app

EXPOSE 8502

HEALTHCHECK CMD curl --fail http://localhost:8502/_stcore/health

ENTRYPOINT ["streamlit", "run", "Main.py", "--server.port=8502", "--server.address=0.0.0.0"]