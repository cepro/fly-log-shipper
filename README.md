# fly-log-shipper

see [README](https://github.com/superfly/fly-log-shipper) in the repository this was forked from for details.

This fork adds some custom transformations to logs coming out of our fly apps to ensure all output logs are in a structured JSON format.

See our modified [vector.toml](https://github.com/cepro/fly-log-shipper/blob/main/vector-config/vector.toml) for details.

## Launch

```sh
fly launch --config fly/fly-<org>.toml --org <org> --no-public-ips --no-deploy --name fly-log-shipper-<org>

fly secrets --config fly/fly-<org>.toml set ACCESS_TOKEN=$(fly auth token)

fly deploy --config fly/fly-<org>.toml
fly scale --config fly/fly-<org>.toml count 1
```