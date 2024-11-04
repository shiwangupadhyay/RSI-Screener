import streamlit as st
import pandas as pd
import yfinance as yf
import ta

forex_pairs = [
    'EURUSD=X', 'USDJPY=X', 'GBPUSD=X',
    'AUDUSD=X', 'USDCAD=X', 'USDCHF=X',
    'NZDUSD=X', 'EURJPY=X', 'GBPJPY=X',
    'EURGBP=X', 'AUDJPY=X', 'EURAUD=X',
    'EURCHF=X', 'AUDNZD=X', 'NZDJPY=X',
    'GBPAUD=X', 'GBPCAD=X', 'EURNZD=X',
    'AUDCAD=X', 'GBPCHF=X', 'AUDCHF=X',
    'EURCAD=X', 'CADJPY=X', 'GBPNZD=X',
    'CADCHF=X', 'CHFJPY=X', 'NZDCAD=X',
    'NZDCHF=X', 'USDINR=X'
]

# Function to calculate RSI and get indications
def indicator(df):
    indicate = []
    df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
    df.dropna(inplace=True)
    for i in range(len(df['RSI'])):
        if df['RSI'].iloc[i] > 70:
            indicate.append('Overbought')
        elif df['RSI'].iloc[i] < 30:
            indicate.append('Underbought')
        else:
            indicate.append('Neutral')
    return indicate

# Function to categorize underbought and overbought
def output(dataframe):
    Underbought = []
    Overbought = []
    for i in forex_pairs:
        clean_pair = i.replace('=X', '')  # Remove '=X' from the pair name
        if dataframe[i]['indication'].iloc[-1] == 'Underbought':
            Underbought.append(clean_pair)
        elif dataframe[i]['indication'].iloc[-1] == 'Overbought':
            Overbought.append(clean_pair)
    return Underbought, Overbought

# Initialize session state to store downloaded data
if 'results_5m' not in st.session_state:
    st.session_state.results_5m = {}
    st.session_state.results_15m = {}
    st.session_state.results_1h = {}
    st.session_state.results_1d = {}
    for pair in forex_pairs:
        try:
            data_5m = yf.download(pair, period='5d', interval='5m')
            if data_5m.index.tz is None:  # If not timezone-aware
                data_5m.index = data_5m.index.tz_localize('UTC').tz_convert('Asia/Kolkata')
            else:
                data_5m.index = data_5m.index.tz_convert('Asia/Kolkata')

            data_15m = yf.download(pair, period='5d', interval='15m')
            if data_15m.index.tz is None:
                data_15m.index = data_15m.index.tz_localize('UTC').tz_convert('Asia/Kolkata')
            else:
                data_15m.index = data_15m.index.tz_convert('Asia/Kolkata')

            data_1h = yf.download(pair, period='1mo', interval='1h')
            if data_1h.index.tz is None:
                data_1h.index = data_1h.index.tz_localize('UTC').tz_convert('Asia/Kolkata')
            else:
                data_1h.index = data_1h.index.tz_convert('Asia/Kolkata')

            data_1d = yf.download(pair, period='6mo', interval='1d')
            if data_1d.index.tz is None:
                data_1d.index = data_1d.index.tz_localize('UTC').tz_convert('Asia/Kolkata')
            else:
                data_1d.index = data_1d.index.tz_convert('Asia/Kolkata')

            # Apply RSI indicators
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


# Get underbought and overbought results for each interval
Underbought_5m, Overbought_5m = output(st.session_state.results_5m)
Underbought_15m, Overbought_15m = output(st.session_state.results_15m)
Underbought_1h, Overbought_1h = output(st.session_state.results_1h)
Underbought_1d, Overbought_1d = output(st.session_state.results_1d)

st.title('RSI Screener for FOREX pairs')

# Styling
with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.markdown("<div class='header'>Choose your intervals to combine:</div>", unsafe_allow_html=True)

# Initialize session state for checkboxes
if 'show_5m' not in st.session_state:
    st.session_state.show_5m = False
if 'show_15m' not in st.session_state:
    st.session_state.show_15m = False
if 'show_1h' not in st.session_state:
    st.session_state.show_1h = False
if 'show_1d' not in st.session_state:
    st.session_state.show_1d = False

# Checkbox states controlled by session state
st.session_state.show_5m = st.checkbox('Show 5 Minute Interval', value=st.session_state.show_5m)
st.session_state.show_15m = st.checkbox('Show 15 Minute Interval', value=st.session_state.show_15m)
st.session_state.show_1h = st.checkbox('Show 1 Hour Interval', value=st.session_state.show_1h)
st.session_state.show_1d = st.checkbox('Show 1 Day Interval', value=st.session_state.show_1d)

# Process selected intervals
selected_intervals = []
if st.session_state.show_5m:
    selected_intervals.append('5m')
if st.session_state.show_15m:
    selected_intervals.append('15m')
if st.session_state.show_1h:
    selected_intervals.append('1h')
if st.session_state.show_1d:
    selected_intervals.append('1d')

if selected_intervals:
    cols = st.columns(len(selected_intervals))

    interval_data = {
        '5m': (Underbought_5m, Overbought_5m),
        '15m': (Underbought_15m, Overbought_15m),
        '1h': (Underbought_1h, Overbought_1h),
        '1d': (Underbought_1d, Overbought_1d)
    }

    # Combine data for multiple intervals
    combined_underbought = set(interval_data[selected_intervals[0]][0])
    combined_overbought = set(interval_data[selected_intervals[0]][1])
    for interval in selected_intervals[1:]:
        combined_underbought.intersection_update(interval_data[interval][0])
        combined_overbought.intersection_update(interval_data[interval][1])

    # Display results for each interval
    for idx, interval in enumerate(selected_intervals):
        with cols[idx]:
            st.markdown(f"<div class='box'><div class='header'>{interval.upper()} INTERVAL</div>", unsafe_allow_html=True)
            st.markdown("<div class='content'>", unsafe_allow_html=True)
            st.write("**RSI < 30 (Underbought):**")
            st.write(", ".join(interval_data[interval][0]))
            st.write("**RSI > 70 (Overbought):**")
            st.write(", ".join(interval_data[interval][1]))
            st.markdown("</div></div>", unsafe_allow_html=True)

    # Display combined results
    if len(selected_intervals) > 1:
        st.markdown("<div class='box'><div class='header'>COMBINED RESULTS</div>", unsafe_allow_html=True)
        st.markdown("<div class='content'>", unsafe_allow_html=True)
        st.write("**RSI < 30 (Underbought):**")
        st.write(", ".join(combined_underbought))
        st.write("**RSI > 70 (Overbought):**")
        st.write(", ".join(combined_overbought))
        st.markdown("</div></div>", unsafe_allow_html=True)
