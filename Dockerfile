FROM alpine:latest
RUN apk add py3-pip poetry openssl
WORKDIR /app
COPY main.py .
COPY pyproject.toml .
RUN poetry install
RUN chmod +x main.py
CMD ["python", "-u", "main.py"]