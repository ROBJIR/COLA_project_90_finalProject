# cola_project_90_finalProject

ONL_PYT_W_6358 - final project
created: 2026-07-12 09:00


## Django configuration

Local development and tests use the fixed development key in Django settings.
Set a private value through the CASSIOPEIA_SECRET_KEY environment variable
when deploying and keep that value stable across restarts. Set
CASSIOPEIA_DEBUG=1 only for local development.

The administration dashboard requires `sysadm.view_dashboard`. Superusers
already have access.
