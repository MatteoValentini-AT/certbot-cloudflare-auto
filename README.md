# matteovalentini/certbot-cloudflare-auto 
A lightweight docker image which automatically creates and renews all your certificates with ```certbot-dns-cloudflare```

## Prerequisites
- A [Cloudflare](https://cloudflare.com) account with at least one domain
- A [Cloudflare API token](https://dash.cloudflare.com/profile/api-tokens) with the ```Zone:DNS:Edit``` permission

## Usage (docker-compose)
### docker-compose.yml
```yaml
version: '3.8'
services:
  certbot:
    image: matteovalentini/certbot-cloudflare-auto
    container_name: certbot
    restart: unless-stopped
    volumes:
      - ./certs:/etc/letsencrypt
      - ./config:/app/config
    secrets:
      - secret1 # e.g. mysecret1
      - secret2
      - ...
secrets:
    secret1: # e.g. mysecret1
        file: <path-to-secret1> # e.g. ./secrets/mysecret1.txt
    secret2:
        file: <path-to-secret2>
    ...
```
### config/certs.conf
```yaml
certs:
  domain1.com: # e.g. matteovalentini.at
    secret: secret1 # e.g. mysecret1
    mail: your-mail@example.com # required for letsencrypt
    domains: # (sub)domains for which you want to create a certificate
      - "*.domain1.com" # wildcard domains are supported
  domain2.com:
    secret: secret2
    mail: your-mail@example.com
    domains:
      - "domain2.com"
      - "www.domain2.com"
      - "mail.domain2.com"
```
1) Create ```docker-compose.yml``` and ```config/certs.conf``` as shown above. For each domain, add a new entry in ```config/certs.conf```
2) Create a token which has access to modify the DNS records of your domains on Cloudflare 
(see [this](https://developers.cloudflare.com/fundamentals/api/get-started/create-token/) guide)
and store it in a file (e.g. ```./secrets/mysecret1.txt```) in the following format ```dns_cloudflare_api_token = your-api-token```
3) Run ```docker-compose up -d```
4) Your certificates will be created in ```./certs/live/``` and will be automatically renewed every 24 hours

## License, Issues and Contributing
This project is licensed under the GPLv3 - see the [LICENSE](LICENSE) file for details.

For issues and contributions, please go to the [Github repository]().
