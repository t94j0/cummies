FROM saltstack/centos-5

RUN mkdir -p /src/cummies
WORKDIR /src/cummies

COPY cummies.py cummies.py

CMD ["python", "./cummies.py"]
