# TLS

This section explains how to add TLS support on Squest.

The TLS endpoint is managed by a reverse proxy on top of the default web server.
This is not the only way to handle this part. Many tools like Nginx, Apache or Traefik could be used, and you are free 
to use the one you want instead of this proposed configuration.
The only recommendation we have is to keep the default nginx web server as main http entrypoint.

## TLS using Caddy

[Caddy](https://caddyserver.com/) is a powerful webserver written in Go which provide a 
[reverse proxy](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy#reverse-proxy) feature.

In the example below, we'll use self-signed certificate. Follow the [official documentation](https://caddyserver.com/docs/automatic-https) 
if you want to configure it to use an ACME like "Let's Encrypt" instead.

Place your certificate and key file in the folder `docker/certs`.

E.g:
```
docker
├── Caddyfile
├── certs
│    ├── squest.crt
│    └── squest.key
```

Update the `docker/Caddyfile` with the FQDN of your server. By default, the FQDN is set to `squest.domain.local`
```
squest.domain.local {   # This line should match the ALLOWED_HOSTS in your Squest environment
    reverse_proxy nginx:8080
    encode gzip zstd
    tls /etc/ssl/private/squest.crt /etc/ssl/private/squest.key
    # or:
    # tls /etc/ssl/private/cert.pem

    log {
      level error
    }
}
```

Update the `ALLOWED_HOSTS` environment variable from the configuration file `docker/environment_variables/squest.env` 
to match your FQDN.
```bash
ALLOWED_HOSTS=squest.domain.local
```

Start docker compose with the TLS configuration:
```bash
docker-compose -f docker-compose.yml -f tls.docker-compose.yml up
```

The squest service is then reachable via HTTP and HTTPS standard ports (80/443).

- http://squest.domain.local
- https://squest.domain.local
