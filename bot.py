import os
import logging
import datetime
import requests
import pytz
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ── Variables de entorno ──────────────────────────────────────
BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID    = os.environ["CHAT_ID"]
FMP_KEY    = os.environ["FMP_KEY"]
NEWS_KEY   = os.environ.get("NEWSAPI_KEY", "")
CHILE_TZ   = pytz.timezone("America/Santiago")


# ── Helpers de datos ─────────────────────────────────────────
def get_market_data():
    try:
        return requests.get(
            f"https://financialmodelingprep.com/api/v3/quote/BTCUSD,ETHUSD,SPY,QQQ?apikey={FMP_KEY}",
            timeout=10
        ).json()
    except Exception:
        return []

def get_fin_news():
    try:
        return requests.get(
            f"https://financialmodelingprep.com/api/v3/stock_news?tickers=SPY,QQQ,AAPL&limit=4&apikey={FMP_KEY}",
            timeout=10
        ).json()
    except Exception:
        return []

def get_geo_news():
    try:
        return requests.get(
            f"https://newsapi.org/v2/top-headlines?q=geopolitics+trade+war+china&language=en&pageSize=4&apiKey={NEWS_KEY}",
            timeout=10
        ).json()
    except Exception:
        return {"articles": []}


# ── Construir briefing ────────────────────────────────────────
def build_briefing():
    prices   = get_market_data()
    fin_news = get_fin_news()
    geo_news = get_geo_news()

    now      = datetime.datetime.now(CHILE_TZ)
    date_str = now.strftime("%A %d de %B, %Y")

    msg = f"🌅 <b>Buenos días, Axael!</b>\n📅 {date_str}\n\n"

    # Mercados
    msg += "📊 <b>MERCADOS</b>\n"
    if isinstance(prices, list):
        for p in prices:
            pct   = round(p.get("changesPercentage", 0), 2)
            price = round(p.get("price", 0), 2)
            e     = "🟢" if pct >= 0 else "🔴"
            msg  += f"{e} <b>{p.get('symbol')}</b>: ${price:,.2f} ({pct:+.2f}%)\n"

    # Noticias financieras
    msg += "\n💼 <b>NOTICIAS FINANCIERAS</b>\n"
    if isinstance(fin_news, list):
        for n in fin_news[:3]:
            msg += f"• {n.get('title', '')}\n"

    # Geopolítica
    msg += "\n🌍 <b>GEOPOLÍTICA</b>\n"
    for a in geo_news.get("articles", [])[:3]:
        msg += f"• {a.get('title', '')}\n"

    msg += "\n<i>Ari — Asistente Virtual 🤖</i>"
    return msg


# ── Jobs automáticos ──────────────────────────────────────────
async def job_briefing(context):
    """Briefing diario a las 8am."""
    msg = build_briefing()
    await context.bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="HTML")

async def job_alertas(context):
    """Revisa precios cada 15 min. Alerta si cambia ±2.5%."""
    prices = get_market_data()
    if not isinstance(prices, list):
        return
    alertas = [p for p in prices if abs(p.get("changesPercentage", 0)) >= 2.5]
    if not alertas:
        return
    msg = "⚡ <b>ALERTA DE MERCADO</b>\n\n"
    for p in alertas:
        pct   = round(p.get("changesPercentage", 0), 2)
        price = round(p.get("price", 0), 2)
        e     = "🚀" if pct >= 0 else "📉"
        msg  += f"{e} <b>{p.get('symbol')}</b>: ${price:,.2f} ({pct:+.2f}%)\n"
    now  = datetime.datetime.now(CHILE_TZ).strftime("%H:%M")
    msg += f"\n<i>{now} hrs — Ari Monitor</i>"
    await context.bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="HTML")


# ── Comandos ──────────────────────────────────────────────────
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "🤖 <b>Hola! Soy Ari, tu asistente virtual.</b>\n\n"
        "/briefing — Resumen completo ahora\n"
        "/precio [TICKER] — Ej: /precio BTCUSD\n"
        "/mercado — Resumen de mercados\n"
        "/noticias — Últimas noticias\n"
        "/ayuda — Ver esta lista"
    )
    await update.message.reply_text(msg, parse_mode="HTML")

async def cmd_precio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ticker = context.args[0].upper() if context.args else "BTCUSD"
    try:
        res = requests.get(
            f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={FMP_KEY}",
            timeout=10
        ).json()
        if isinstance(res, list) and res:
            p     = res[0]
            pct   = round(p.get("changesPercentage", 0), 2)
            price = round(p.get("price", 0), 2)
            high  = round(p.get("dayHigh", 0), 2)
            low   = round(p.get("dayLow", 0), 2)
            e     = "🟢" if pct >= 0 else "🔴"
            msg   = (
                f"{e} <b>{p.get('symbol')}</b>\n"
                f"💵 Precio: ${price:,.2f}\n"
                f"📈 Cambio 24h: {pct:+.2f}%\n"
                f"📊 Máx: ${high:,.2f} / Mín: ${low:,.2f}"
            )
        else:
            msg = "❌ Ticker no encontrado.\nEjemplos: BTCUSD · ETHUSD · AAPL · SPY"
    except Exception:
        msg = "❌ Error al consultar el precio."
    await update.message.reply_text(msg, parse_mode="HTML")

async def cmd_mercado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prices = get_market_data()
    if not isinstance(prices, list) or not prices:
        await update.message.reply_text("❌ No se pudieron obtener datos.")
        return
    now = datetime.datetime.now(CHILE_TZ).strftime("%H:%M")
    msg = f"📊 <b>RESUMEN DE MERCADO</b>\n🕐 {now} hrs\n\n"
    for p in prices:
        pct   = round(p.get("changesPercentage", 0), 2)
        price = round(p.get("price", 0), 2)
        e     = "🟢" if pct >= 0 else "🔴"
        msg  += f"{e} <b>{p.get('symbol')}</b>: ${price:,.2f} ({pct:+.2f}%)\n"
    await update.message.reply_text(msg, parse_mode="HTML")

async def cmd_noticias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    geo      = get_geo_news()
    articles = geo.get("articles", [])
    if not articles:
        await update.message.reply_text("❌ No se pudieron obtener noticias.")
        return
    msg = "🌍 <b>NOTICIAS GEOPOLÍTICAS</b>\n\n"
    for a in articles[:5]:
        msg += f"• {a.get('title', '')}\n\n"
    await update.message.reply_text(msg, parse_mode="HTML")

async def cmd_briefing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Generando tu briefing...")
    msg = build_briefing()
    await update.message.reply_text(msg, parse_mode="HTML")


# ── Main ──────────────────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler(["start", "ayuda"], cmd_start))
    app.add_handler(CommandHandler("precio",   cmd_precio))
    app.add_handler(CommandHandler("mercado",  cmd_mercado))
    app.add_handler(CommandHandler("noticias", cmd_noticias))
    app.add_handler(CommandHandler("briefing", cmd_briefing))

    # Jobs programados
    jq = app.job_queue
    jq.run_daily(
        job_briefing,
        time=datetime.time(hour=8, minute=0, tzinfo=CHILE_TZ)
    )
    jq.run_repeating(job_alertas, interval=900, first=120)  # cada 15 min

    print("✅ Ari bot iniciado!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
