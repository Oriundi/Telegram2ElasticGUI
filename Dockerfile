FROM python:3.10-slim as compiler
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN python -m venv /opt/venv
# Enable venv
ENV PATH="/opt/venv/bin:$PATH"

RUN addgroup --gid 777 --system app && \
    adduser --no-create-home --shell /bin/false --disabled-password --uid 777 --system --group app

COPY requirements.txt .
RUN pip install -r requirements.txt

USER app

FROM python:3.9-slim as runner
COPY --from=compiler /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app/
COPY pages/*.py /app/pages/
COPY models/*.py /app/models/
COPY t2e_gui.py /app/

VOLUME /sessions

#ENTRYPOINT ["/app/t2e_gui.py"]
CMD ["python", "t2e_gui.py"]