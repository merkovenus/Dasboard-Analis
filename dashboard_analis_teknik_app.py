# app.py
import streamlit as st
import yfinance as yf
import ta
import pandas as pd
import plotly.graph_objs as go
import numpy as np

st.set_page_config(page_title="Dashboard Saham Harian", layout="wide")
st.title("📈 Dashboard Analisa Teknikal Saham Harian Syariah")

# Input kode saham
st.sidebar.header("📌 Pengaturan")
ticker = st.sidebar.text_input("Kode saham (contoh: BBCA.JK)", value="BBCA.JK")

# Fungsi untuk ambil data
@st.cache_data
def load_data(ticker):
    df = yf.download(ticker, start="2022-01-01", interval="1d", auto_adjust=True)
    df.dropna(inplace=True)
    df['rsi'] = ta.momentum.RSIIndicator(df['Close']).rsi()
    df['macd'] = ta.trend.MACD(df['Close']).macd_diff()
    df['ma20'] = df['Close'].rolling(20).mean()
    df['ma50'] = df['Close'].rolling(50).mean()
    return df

# Fungsi cari support level sederhana (paling sering dikunjungi)
def find_support(df):
    harga = df['Close'].round(-2)  # pembulatan ke puluhan
    support = harga.value_counts().idxmax()
    return support

if ticker:
    df = load_data(ticker)
    support_level = find_support(df)

    st.subheader(f"Grafik {ticker} + Support Level: Rp {support_level:,.0f}")

    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'],
                                 low=df['Low'], close=df['Close'], name='Harga'))
    fig.add_trace(go.Scatter(x=df.index, y=df['ma20'], name='MA20', line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=df.index, y=df['ma50'], name='MA50', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=df.index, y=[support_level]*len(df), name='Support',
                             line=dict(color='green', dash='dot')))
    fig.update_layout(xaxis_rangeslider_visible=False, height=600)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📊 Indikator RSI & MACD")
    st.line_chart(df[['rsi', 'macd']])

    # Sinyal beli (RSI < 30 dan MACD positif)
    latest = df.iloc[-1]
    if latest['rsi'] < 30 and latest['macd'] > 0:
        st.success("📈 Sinyal BELI: RSI rendah & MACD menguat")
    elif latest['rsi'] > 70 and latest['macd'] < 0:
        st.error("📉 Sinyal JUAL: RSI tinggi & MACD melemah")
    else:
        st.info("⏳ Tidak ada sinyal kuat saat ini")
