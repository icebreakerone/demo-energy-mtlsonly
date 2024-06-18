# Perseus demo Data Source

This demonstration provides a simple API to implement a Data Source, with mutual authentication via MTLS certificates, and role based authorisation based on information in the client certificate.

## Setup and running the demo server

### Creating demo certificate authority and certificates

The server and clients require a private server Certificate Authority (CA), a private client CA, and server and client certificates in a `certs/` folder. These can be generated using the `certmaker.sh` script in the `scripts` directory.

```bash
mkdir certs
cd certs/
sh ../scripts/certmaker.sh 
cd ..
```

The script generates the server's certificate with the hostname of the local computer for normal HTTPS validation, as output from `hostname`.

### Running the local docker environment

The included docker compose file will bring up

* the API resource server
* an Nginx proxy, which checks the client certificate is valid and passes it to the resource server using the same header as AWS ALB (`x-amzn-mtls-clientcert`).

To run the server, leave this command running:

```bash
sudo docker compose up
```

## Retriving the data with curl

Any HTTP client which can present a client certificate, and check a server certificate against a private CA, can be used to fetch data.

`curl` is used in this example, run on the same machine as the `docker compose up` command. In the `curl` commands, `--cert` and `--key` specify the client certificate, and `--cacert` the CA which must be used to sign the server's certificate. The URL is formed using the output of `hostname`.

To fetch the report, request the `/api/v1/supply-voltage` with a `period` query parameter, for which any value can be used.

When the report is requested with a client certificate which encodes the `supply-voltage-reader@electricity` group in the certificate's subject, the server knows that the client is a participant in the Trust Framework with the role that is allowed to use the data:

```bash
curl --cert certs/6-application-one-bundle.pem --key certs/6-application-one-key.pem \
    --cacert certs/1-server-ca-cert.pem \
    https://`hostname`:8010/api/v1/supply-voltage?period=2023-07
```
This returns

```json
{"period":"2023-07","voltages":[232,249,231,232,249,236,247,240,238,243,233,233,234,243,238,249]}
```

However, if a client certificate is used which does not have this role, then an error is returned:

```bash
curl --cert certs/7-application-two-bundle.pem --key certs/7-application-two-key.pem \
    --cacert certs/1-server-ca-cert.pem \
    https://`hostname`:8010/api/v1/supply-voltage?period=2023-07
```

The resource server generates a 401 response with the body:

```json
{"detail":"Client certificate does not include role supply-voltage-reader@electricity"}
```

Finally, if the client presents a certificate which isn't signed by the client CA:

```bash
curl --cert certs/3-server-cert-bundle.pem --key certs/3-server-key.pem \
    --cacert certs/1-server-ca-cert.pem \
    https://`hostname`:8010/api/v1/info
```

Nginx will returns a `400 Bad Request`. The resource server will not receive the request, enforcing membership of the Trust Framework at the transport level.

```
<html>
<head><title>400 The SSL certificate error</title></head>
<body>
<center><h1>400 Bad Request</h1></center>
<center>The SSL certificate error</center>
...
```

## Information API

The resource server also implements an `info` API which returns information about the request and client certificate.

```bash
curl --cert certs/6-application-one-bundle.pem --key certs/6-application-one-key.pem \
    --cacert certs/1-server-ca-cert.pem \
    https://`hostname`:8010/api/v1/info
```

## Guided tour

### scripts/certmaker.sh

This [script](scripts/certmaker.sh) generates two CAs and chains of certificates. The certificate trees are documented at the top of the file.

Each of the two private CAs uses an intermediate certificate, which then signs the server or client certificates. This is so the key of the root CA certificate can be kept offline for security, enabling the root certificate to have a long lifetime. The intermediate Issuer certificates have a shorter lifetime, and their keys are kept online. These are then used to sign short lived certificates which are automatically renewed and installed, for example with an [ACME client](https://letsencrypt.org/docs/client-options/). In the event of compromise, the Issuer intermediate certificates can be easily replaced.

Client certificate Subject names contain:
* the organisation name,
* the OAuth client ID in the Common Name (CN), generated with `uuidgen`,
* and the roles in one or more Organisational Unit Names (OU).

For ease of management for clients, the client certificates have a long lifetime. They would typically be issued by the Directory through an API or user interface. 

The script also combines each server and client certificate with its intermediate Issuer into certificate bundle files, so the client and server can both present all the certificates in the chain. Without providing the Issuer certificate, the certificate chains would not be able to be verified.

### nginx/default.conf.template

This [configuration file](nginx/default.conf.template):

* sets the server certificate using the combined certificate and issuer file,
* sets the client Certificate Authority to the private client CA, and requires that any client presents a valid certificate signed by this CA,
* sets the `x-amzn-mtls-clientcert` header to the client certificate presented,
* and proxies the unencrypted request to the resource server.

By requiring and verifying the client certificate, Nginx ensures that only Trust Framework participants can make requests to the underlying resource server.

In a real deployment, the server would be configured to check for revocation of client certificates. The client does not need to check for revocation because the server certificates are replaced daily.

### resource/main.py

Data Service API is implemented by a [FastAPI server](resource/main.py). Because most of the authentication is delegated to the Nginx proxy, it does not need to do anything to ensure that only a Trust Framework participant can call API endpoints.

However, it needs to verify that only participants with the right role can access the API. The `require_role()` method checks this by:

* Decoding the client certificate from the `x-amzn-mtls-clientcert` header. It can rely on this certificate being valid and signed by the private client CA.
* Decoding the roles from the certificate's Subject attribute.
* Raising an exception if the expected role is not present in the certificate.

## Modifying the resource server

To make changes to the resource server, run the proxy and resource server with `docker compose up`, as above. When you modify the Python files, the server will automatically be reloaded.

