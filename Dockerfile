FROM alpine:latest
WORKDIR /app
RUN apk add py3-pip openssl && python3 -m venv /app/venv
RUN /app/venv/bin/pip install certbot certbot-dns-cloudflare pyyaml
COPY main.py .
RUN chmod +x main.py
CMD . /app/venv/bin/active && python main.py