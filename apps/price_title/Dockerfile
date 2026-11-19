FROM python:3.12-slim
WORKDIR /app
COPY price_title.py .
ENV STATE_DIR=/state PYTHONUNBUFFERED=1
RUN mkdir /state && chown nobody /state
VOLUME /state
USER nobody
CMD ["python3", "/app/price_title.py"]
