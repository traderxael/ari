#!/usr/bin/env bash
# Detecta credenciales LITERALES commiteadas en el repo.
# Distingue un secreto real (BOT_TOKEN = "abc123...") de LEER una variable
# (os.environ["BOT_TOKEN"]), que es lo normal en codigo Python.
# El .env.example queda excluido a proposito: es una plantilla sin valores reales.
set -uo pipefail

PATTERN='(BOT_TOKEN|FMP_KEY|NEWSAPI_KEY)[[:space:]]*=[[:space:]]*("[^"]{12,}"|'"'"'[^'"'"']{12,}'"'"'|[A-Za-z0-9_-]{24,})'

if git grep -nE "$PATTERN" -- . ':!.env.example'; then
  echo "::error::Se detectaron credenciales literales commiteadas (arriba). Revisa el commit."
  exit 1
fi

echo "OK: sin credenciales literales commiteadas"