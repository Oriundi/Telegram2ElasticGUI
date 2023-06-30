FROM python:3.10-slim as compiler

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

#RUN apt-get update && \
#    apt-get install -y --no-install-recommends gcc

RUN python -m venv /opt/venv
## Enable venv
ENV PATH="/opt/venv/bin:$PATH"

RUN addgroup --gid 777 --system app && \
    adduser --no-create-home --shell /bin/false --disabled-password --uid 777 --system --group app

COPY requirements.txt .
RUN pip install -r requirements.txt

USER app

FROM python:3.10-slim as runner
COPY --from=compiler /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app/
COPY pages/*.py /app/pages/
COPY models/*.py /app/models/
COPY t2e_gui.py /app/
COPY logger.py /app/

VOLUME /config

EXPOSE 8050

#ENTRYPOINT ["/app/t2e_gui.py"]
#CMD ["python", "t2e_gui.py"]
CMD [ "gunicorn", "--workers=2", "--threads=2", "-b 127.0.0.1:8050", "t2e_gui:server"]