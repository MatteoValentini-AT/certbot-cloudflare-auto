FROM alpine:latest
RUN apk add py3-pip
RUN pip install certbot certbot-dns-cloudflare pyyaml
WORKDIR /app
COPY main.py .
RUN chmod +x main.py
CMD ["python", "-u", "main.py"]