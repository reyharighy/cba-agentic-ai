FROM python:3.12

RUN pip install --no-cache-dir uv --root-user-action=ignore

ARG WORKDIR_PATH
WORKDIR ${WORKDIR_PATH}

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY . ./

RUN useradd -m -u 1000 agentapiuser
RUN chown -R agentapiuser:agentapiuser ${WORKDIR_PATH}

USER agentapiuser

CMD ["sleep", "infinity"]
