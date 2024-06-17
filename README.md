# Perseus demo energy provider

Emulates authentication and resource api endpoints for the Perseus demo. Authentication is built on top of [Ory Hydra](https://www.ory.sh).

## Authentication API

The authentication app is in the [authentication](authentication) directory. It provides endpoints for authenticating and identifying users, and for handling and passing on requests from the client API to the FAPI API. It uses a

Authentication API documentation is available at https://perseus-demo-authentication.ib1.org/api-docs.

## Resource API

The resource api is in the [resource](resource) directory. It demonstrates how to protect an API endpoint using a certificate bound token obtained from the authentication API's interaction with the FAPI provider.

Resource API documentation is available at https://perseus-demo-energy.ib1.org/api-docs.

## Running a dev server

```bash
cd authentication|resource
pipenv install --dev
pipenv run uvicorn api.main:app --reload
```

## Creating self-signed certificates

The docker compose and client.py scripts require a set of self-signed certificates in a certs/ folder. These can be generated using the `certmaker.sh` script in the `scripts` directory.

```bash
cd scripts
./certmaker.sh
```

You will need to create a "certs" directory in the root of the project, and move the generated certificates into it.

### Using client certificates

Most of the endpoints require a client certificate to be presented. As the directory service is not yet available, the contents of the certificate will not be checked with an external, so any valid certificate will be acceptable. The certificate **is** used to confirm identity, so the same one must be presented in all requests.

## Creating signing certificates

A separate set of certificates are required for signing JWTs. These can be generated using the `signingcerts.sh` script in the `scripts` directory.

```bash
cd scripts
./signingcerts.sh
```

The default configuration will expect these certificate to be in authentication/api/certs. The location can be changed by setting the DIRECTORY_CERTIFICATE and DIRECTORY_PRIVATE_KEY environment variables.

## Running the local docker environment

The included docker compose file will bring up both APIs. It uses nginx to proxy requests to uvicorn, with nginx configuration to pass through client certificates to the backend, using the same header as used by AWS ALB (`x-amzn-mtls-clientcert`).

```bash
docker-compose up
```

The environment variables in the docker compose file point to the FAPI api running on localhost port 8020 (http://host.docker.internal:8020). As the FAPI api is not running in the docker environment, you may need to change these environment variables to match your local environment. It will also work with the live FAPI api by changing these values to "https://perseus-demo-authentication.ib1.org".

## Testing the API with curl

```bash
curl --cert certs/client-cert.pem --key certs/client-key.pem --cacert certs/ca-cert.pem  https://`hostname`:8010/api/v1/info
```
