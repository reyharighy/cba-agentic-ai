FROM python:3.12

RUN pip install --no-cache-dir uv --root-user-action=ignore

ARG WORKDIR_PATH
ARG AGENT_API_PORT

ENV WORKDIR_PATH=${WORKDIR_PATH}
ENV AGENT_API_PORT=${AGENT_API_PORT}
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR ${WORKDIR_PATH}

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . ./

RUN useradd -m -u 1000 agentapiuser && \
    chown -R agentapiuser:agentapiuser ${WORKDIR_PATH}

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && chown agentapiuser:agentapiuser /entrypoint.sh

USER agentapiuser

ENTRYPOINT ["/entrypoint.sh"]
