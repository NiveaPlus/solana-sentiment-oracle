# Solana Sentiment Oracle 🧠📈

This project is a real-time sentiment oracle for Solana (SOL), built with Streamlit.

## Features

- 📊 Aggregates data from: Fear & Greed Index, CryptoPanic, LunarCrush, TAAPI.io, Helius, CoinMarketCal
- 📈 Shows live SOL/USDT price chart (from Binance)
- 🕒 Auto-refreshes every 5 minutes
- 📉 Tracks Buy / Hold / Sell sentiment with history graph

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Cloud

1. Push this project to GitHub
2. Visit [streamlit.io/cloud](https://streamlit.io/cloud)
3. Select your repo and deploy `app.py`
