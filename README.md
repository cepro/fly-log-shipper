# fly-log-shipper

see [README](https://github.com/superfly/fly-log-shipper) in the repository this was forked from for details.

This fork adds some custom transformations to logs coming out of our fly apps to ensure all output logs are in a structured JSON format.

See our modified [vector.toml](https://github.com/cepro/fly-log-shipper/blob/main/vector-config/vector.toml) for details.

## Launch

```sh
# create fly.toml - edit and set env variables
cp fly.example.toml fly.toml

fly launch --org <org> --no-public-ips --no-deploy --name fly-log-shipper-<org>

# remove http_service section created by fly and redeploy
#   couldn't see a command line option to achieve this on launch ... 
vim fly.toml

fly secrets set ACCESS_TOKEN=$(fly auth token)

fly deploy
fly scale count 1
```