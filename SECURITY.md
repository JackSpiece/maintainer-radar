# Security

Maintainer Radar is local-first and does not store GitHub tokens.

Live GitHub access is delegated to the GitHub CLI. If you use `gh`, token storage
is handled by `gh` itself.

For the permissions model and data flow, see
[docs/privacy-permissions.md](docs/privacy-permissions.md).

Please report security issues through a private GitHub security advisory when
available. If that is not available, open a minimal public issue that says a
security report is available without disclosing exploit details.
