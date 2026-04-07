# cPanel Support Ticket: DNS and SSL Issues for testapi.businessystem.com

Subject: `testapi.businessystem.com` DNS and SSL need to be fixed for deployed Python API

Hello Support,

We have deployed a Python/FastAPI application on your cPanel server and the application itself is now working correctly on the server. However, two hosting-side issues still need to be resolved before the endpoint is production-ready.

## Issue 1: Public DNS for `testapi.businessystem.com` is not authoritative from the cPanel zone

### What we found

- In cPanel Zone Editor, there is already an `A` record for:
  - `testapi.businessystem.com -> 104.36.228.30`
- But public DNS does not resolve that hostname from the internet.
- Public authoritative nameservers for `businessystem.com` are:
  - `launch1.spaceship.net`
  - `launch2.spaceship.net`
- The cPanel zone appears to be on:
  - `ns1.shockhosting.com`
  - `ns2.shockhosting.com`

### Result

The DNS records added in cPanel are not being used publicly, so:

- `dig +short testapi.businessystem.com @1.1.1.1` returns nothing
- `dig +short testapi.businessystem.com @8.8.8.8` returns nothing
- SSL DCV/AutoSSL cannot validate the hostname

### What we need from support

Please confirm one of these:

1. Whether you can make the cPanel DNS authoritative for this subdomain, or
2. Whether the DNS record must be added at the actual public DNS provider instead of cPanel, or
3. Whether the subdomain `testapi.businessystem.com` should be delegated to your nameservers

If your side can resolve it directly, we need public DNS for:

- `testapi.businessystem.com -> 104.36.228.30`

## Issue 2: `testapi.businessystem.com` is serving a self-signed SSL certificate

### What we found

The server currently presents a self-signed certificate for `testapi.businessystem.com`.

Example error from curl:

- `curl: (60) SSL certificate problem: self-signed certificate`

This means:

- the API may work in Postman with SSL verification disabled
- but standard clients and browser-based UI integrations will fail certificate validation

### What we need from support

Please install or issue a valid CA-signed certificate for:

- `testapi.businessystem.com`

The certificate must:

- include `testapi.businessystem.com` in CN/SAN
- be trusted by standard clients
- be the certificate actively served by LiteSpeed/Apache for this hostname
- replace the current self-signed certificate

### Important dependency

This SSL issue may not be resolvable until Issue 1 is fixed, because AutoSSL/DCV requires the hostname to resolve publicly first.

## Application status on the server

The application itself is working correctly when we bypass DNS/certificate issues.

We verified:

- Passenger boots successfully
- the Python app responds correctly
- `POST /predict` returns `200` JSON when reached through the working host/IP workaround

So the remaining blockers are:

1. Public DNS for `testapi.businessystem.com`
2. Valid SSL certificate for `testapi.businessystem.com`

## Success criteria

We will consider this resolved when all of the following work normally:

```bash
dig +short testapi.businessystem.com @1.1.1.1
dig +short testapi.businessystem.com @8.8.8.8
curl -i https://testapi.businessystem.com/health
curl -i https://testapi.businessystem.com/predict
```

Expected:

- DNS returns `104.36.228.30`
- no SSL warning
- `/health` returns `200`
- `/predict` returns `200` JSON

Please let us know whether DNS must be updated in your environment or at the external authoritative DNS provider, and then please complete the SSL issuance once DNS is correct.

Thank you.