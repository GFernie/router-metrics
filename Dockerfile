FROM python
WORKDIR /usr/src/app
ADD pyproject.toml src/ ./
RUN --mount=type=cache,target=/root/.cache/pip,mode=0755 pip install .
CMD ["python", "-m", "router_metrics.target"]
