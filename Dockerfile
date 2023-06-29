FROM python:3.10-slim as compiler
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN python -m venv /opt/venv
# Enable venv
ENV PATH="/opt/venv/bin:$PATH"

RUN addgroup --gid 1001 --system app && \
    adduser --no-create-home --shell /bin/false --disabled-password --uid 1001 --system --group app
USER app

RUN pip install -r requirements.txt

FROM python:3.9-slim as runner
WORKDIR /app/
COPY --from=compiler /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY pages/*.py /app/pages/
COPY models/*.py /app/models/
COPY requirements.txt /app/
COPY t2e_gui.py /app/

VOLUME /config

#ENTRYPOINT ["/app/t2e_gui.py"]
CMD ["python", "app.py"]