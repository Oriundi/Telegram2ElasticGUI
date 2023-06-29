FROM python:3.10

WORKDIR /app

COPY pages/*.py /app/pages/
COPY models/*.py /app/models/
COPY requirements.txt /app/
COPY t2e_gui.py /app/

RUN pip install -r requirements.txt

VOLUME /config

ENTRYPOINT ["/app/t2e_gui.py"]