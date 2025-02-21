import streamlit as st
import pandas as pd
import yfinance as yf
import ta

forex_pairs = [
    'EURUSD=X', 'USDJPY=X', 'GBPUSD=X', 'AUDUSD=X', 'USDCAD=X', 'USDCHF=X', 'NZDUSD=X',
    'EURJPY=X', 'GBPJPY=X', 'EURGBP=X', 'AUDJPY=X', 'EURAUD=X', 'EURCHF=X', 'AUDNZD=X',
    'NZDJPY=X', 'GBPAUD=X', 'GBPCAD=X', 'EURNZD=X', 'AUDCAD=X', 'GBPCHF=X', 'AUDCHF=X',
    'EURCAD=X', 'CADJPY=X', 'GBPNZD=X', 'CADCHF=X', 'CHFJPY=X', 'NZDCAD=X', 'NZDCHF=X', 'USDINR=X'
]

@st.cache_data
def download_data(pair, period, interval):
    try:
        data = yf.download(pair, period=period, interval=interval)
        if data.empty:
            st.warning(f"No data found for {pair} ({interval} interval).")
            return None

        if data.index.tz is None:
            data.index = data.index.tz_localize('UTC').tz_convert('Asia/Kolkata')
        else:
            data.index = data.index.tz_convert('Asia/Kolkata')
        return data
    except Exception as e:
        st.error(f"Error downloading data for {pair} ({interval} interval): {type(e).__name__}: {e}")
        return None

def indicator(df):
    if df is None or df.empty or 'Close' not in df.columns:
        return []
    indicate = []
    close_prices = df['Close'].squeeze()
    rsi_series = ta.momentum.RSIIndicator(close_prices, window=14).rsi()
    df['RSI'] = rsi_series.squeeze()
    df.dropna(inplace=True)

    for value in df['RSI']:
        if value > 70:
            indicate.append('Overbought')
        elif value < 30:
            indicate.append('Underbought')
        else:
            indicate.append('Neutral')

    return indicate

def output(data_dict, interval):
    Underbought = []
    Overbought = []
    for pair in forex_pairs:
        key = f"{pair}_{interval}"
        if key in data_dict and data_dict[key] is not None and not data_dict[key].empty and 'indication' in data_dict[key].columns:
            if data_dict[key]['indication'].iloc[-1] == 'Underbought':
                Underbought.append(pair.replace('=X', ''))
            elif data_dict[key]['indication'].iloc[-1] == 'Overbought':
                Overbought.append(pair.replace('=X', ''))
    return Underbought, Overbought


if 'data' not in st.session_state:
    st.session_state.data = {}

for pair in forex_pairs:
    for interval in ['5m', '15m', '1h', '1d']:
        key = f"{pair}_{interval}"
        if key not in st.session_state.data:
            if interval in ('5m', '15m'):
                period = '5d'
            elif interval == '1h':
                period = '1mo'
            else:
                period = '6mo'
            st.session_state.data[key] = download_data(pair, period, interval)
            if st.session_state.data[key] is not None and 'Close' in st.session_state.data[key].columns:
                st.session_state.data[key]['indication'] = indicator(st.session_state.data[key])


st.title('RSI Screener for FOREX pairs')

# You'll need a styles.css file in the same directory as your script
with open('styles.css') as f:  
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.markdown("<div class='header'>Choose your intervals to combine:</div>", unsafe_allow_html=True)

for interval in ['5m', '15m', '1h', '1d']:
    if f'show_{interval}' not in st.session_state:
        st.session_state[f'show_{interval}'] = False

for interval in ['5m', '15m', '1h', '1d']:
    st.session_state[f'show_{interval}'] = st.checkbox(f'Show {interval.upper()} Interval', value=st.session_state[f'show_{interval}'])

selected_intervals = [interval for interval in ['5m', '15m', '1h', '1d'] if st.session_state[f'show_{interval}']]

if selected_intervals:
    cols = st.columns(len(selected_intervals))
    interval_data = {}
    for interval in ['5m', '15m', '1h', '1d']:
        interval_data[interval] = output(st.session_state.data, interval)

    combined_underbought = set()
    combined_overbought = set()

    if selected_intervals:
        combined_underbought = set(interval_data[selected_intervals[0]][0])
        combined_overbought = set(interval_data[selected_intervals[0]][1])

        for interval in selected_intervals[1:]:
            combined_underbought.intersection_update(interval_data[interval][0])
            combined_overbought.intersection_update(interval_data[interval][1])

    for idx, interval in enumerate(selected_intervals):
        with cols[idx]:
            st.markdown(f"<div class='box'><div class='header'>{interval.upper()} INTERVAL</div>", unsafe_allow_html=True)
            st.markdown("<div class='content'>", unsafe_allow_html=True)
            st.write("**RSI < 30 (Underbought):**")
            st.write(", ".join(interval_data[interval][0]))
            st.write("**RSI > 70 (Overbought):**")
            st.write(", ".join(interval_data[interval][1]))
            st.markdown("</div></div>", unsafe_allow_html=True)

    if len(selected_intervals) > 1:
        st.markdown("<div class='box'><div class='header'>COMBINED RESULTS</div>", unsafe_allow_html=True)
        st.markdown("<div class='content'>", unsafe_allow_html=True)
        st.write("**RSI < 30 (Underbought):**")
        st.write(", ".join(combined_underbought))
        st.write("**RSI > 70 (Overbought):**")
        st.write(", ".join(combined_overbought))
        st.markdown("</div></div>", unsafe_allow_html=True)