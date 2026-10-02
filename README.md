# ARI — Bot de informes financieros y geopolíticos

> Axael Contreras · Telegram + Python

Bot de Telegram que te manda **cada mañana un informe con datos de mercado y noticias
de geopolítica**, listo para leer de un vistazo.

## Qué hace

- 📊 **Datos de mercado** — cotizaciones de BTC, ETH, SPY y QQQ vía Financial Modeling Prep
- 💹 **Noticias financieras** — headlines de mercado de SPY, QQQ y AAPL
- 🌍 **Geopolítica** — noticias sobre geopolítica y guerra comercial (vía NewsAPI, opcional)
- ⏰ **Envío programado** — con zona horaria `America/Santiago`, para que salga a la hora chilena
- 📱 **Entrega en Telegram** — un comando y recibes el informe

## Comandos

| Comando | Qué hace |
|---|---|
| `/start` | Mensaje de bienvenida |
| `/informe` | Envía el informe completo ahora mismo |

## Requisitos

- Python 3.10+
- Un token de bot de [@BotFather](https://t.me/BotFather)
- Una API key de [Financial Modeling Prep](https://site.financialmodelingprep.com/developer/docs/)
- (Opcional) API key de [NewsAPI](https://newsapi.org) para la sección geopolítica

## Variables de entorno

Copia el ejemplo y complétalo:

```bash
cp .env.example .env
```

| Variable | Descripción | Obligatoria |
|---|---|---|
| `BOT_TOKEN` | Token del bot de Telegram | ✅ |
| `CHAT_ID` | Tu ID de chat de Telegram | ✅ |
| `FMP_KEY` | API key de Financial Modeling Prep | ✅ |
| `NEWSAPI_KEY` | API key de NewsAPI | ❌ (sin ella no hay geopolítica) |

> Nunca subas tus claves al repo: `.env` está en `.gitignore`.

## Instalación y uso

```bash
pip install -r requirements.txt
python bot.py
```

## Despliegue en Railway

El repo incluye [`railway.toml`](railway.toml) para despliegue. En Railway:

1. Crea un proyecto y enlázalo con este repo
2. Agrega las variables de entorno (`BOT_TOKEN`, `CHAT_ID`, `FMP_KEY`, `NEWSAPI_KEY`)
3. Railway detecta el Procfile/TOML y despliega

## Tech

- `python-telegram-bot[job-queue]==21.6`
- `requests==2.31.0`
- `pytz==2024.1`

## Licencia

MIT — ver [LICENSE](LICENSE).
