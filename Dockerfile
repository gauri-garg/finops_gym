FROM ghcr.io/meta-pytorch/openenv-base:latest

WORKDIR /app

COPY . .

RUN uv pip install -e .

ENV PYTHONPATH="/app:$PYTHONPATH"
ENV ENABLE_WEB_INTERFACE=true

EXPOSE 7860

CMD ["serve", "--port", "7860"]