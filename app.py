import streamlit as st
import yfinance as yf
import pandas as pd

# Function to compute RSI indication (Replace with your logic)
def indicator(data):
    if 'Close' not in data.columns:
        return None
    data['RSI'] = 100 - (100 / (1 + data['Close'].pct_change().rolling(14).mean()))
    return data['RSI'].apply(lambda x: 'Overbought' if x > 70 else 'Oversold' if x < 30 else 'Neutral')

# Initialize session state if not already set
if 'results_5m' not in st.session_state:
    st.session_state.results_5m = {}
if 'results_15m' not in st.session_state:
    st.session_state.results_15m = {}
if 'results_1h' not in st.session_state:
    st.session_state.results_1h = {}
if 'results_1d' not in st.session_state:
    st.session_state.results_1d = {}

# Forex pairs to track
forex_pairs = [
    "EURUSD=X", "USDJPY=X", "GBPUSD=X", "AUDUSD=X", "USDCAD=X", "USDCHF=X", "NZDUSD=X",
    "EURJPY=X", "GBPJPY=X", "EURGBP=X", "AUDJPY=X", "EURAUD=X", "EURCHF=X", "AUDNZD=X",
    "NZDJPY=X", "GBPAUD=X", "GBPCAD=X", "EURNZD=X", "AUDCAD=X", "GBPCHF=X", "AUDCHF=X",
    "EURCAD=X", "CADJPY=X", "GBPNZD=X", "CADCHF=X", "CHFJPY=X", "NZDCAD=X", "NZDCHF=X",
    "USDINR=X"
]

# Streamlit App UI
st.title("Forex Screener: RSI Overbought & Oversold Levels")

for pair in forex_pairs:
    try:
        # Download data for different timeframes
        data_5m = yf.download(pair, period='5d', interval='5m')
        data_15m = yf.download(pair, period='5d', interval='15m')
        data_1h = yf.download(pair, period='1mo', interval='1h')
        data_1d = yf.download(pair, period='6mo', interval='1d')

        # Ensure datetime index is timezone aware
        for data in [data_5m, data_15m, data_1h, data_1d]:
            if not hasattr(data.index, "tz"):
                data.index = pd.to_datetime(data.index).tz_localize("UTC").tz_convert("Asia/Kolkata")
            else:
                data.index = data.index.tz_convert("Asia/Kolkata")

        # Apply RSI indicator
        data_5m['indication'] = indicator(data_5m)
        data_15m['indication'] = indicator(data_15m)
        data_1h['indication'] = indicator(data_1h)
        data_1d['indication'] = indicator(data_1d)

        # Store results in session state
        st.session_state.results_5m[pair] = data_5m
        st.session_state.results_15m[pair] = data_15m
        st.session_state.results_1h[pair] = data_1h
        st.session_state.results_1d[pair] = data_1d

    except Exception as e:
        st.error(f"Error downloading data for {pair}: {e}")

# Display results in Streamlit
st.header("Forex Pairs with RSI Indicators")
timeframe = st.selectbox("Select Timeframe", ["5m", "15m", "1h", "1d"])
selected_results = getattr(st.session_state, f"results_{timeframe}", {})

for pair, df in selected_results.items():
    st.subheader(pair)
    st.dataframe(df.tail(5))  # Show last 5 rows of data for each pair
