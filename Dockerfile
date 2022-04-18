FROM python
RUN pip install huawei-lte-api prometheus-client
ADD cpe_target.py ./
CMD ["python", "cpe_target.py"]
