FROM python
WORKDIR /usr/src/app
ADD cpe_target.py pyproject.toml ./
RUN pip install .
CMD ["python", "-m", "cpe_target"]
