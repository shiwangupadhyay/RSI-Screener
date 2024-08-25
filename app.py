import streamlit as st
import pandas as pd
import yfinance as yf
import ta

# Define the forex pairs
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

# Function to calculate RSI indication
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

# Function to process data and get indications
def output(dataframe):
    Underbought = []
    Overbought = []
    for i in forex_pairs:
        if dataframe[i]['indication'].iloc[-1] == 'Underbought':
            Underbought.append(i)
        elif dataframe[i]['indication'].iloc[-1] == 'Overbought':
            Overbought.append(i)
    return Underbought, Overbought

# Download data for different intervals
results_5m = {}
results_15m = {}
results_1h = {}
results_1d = {}

for pair in forex_pairs:
    data_5m = yf.download(pair, period='5d', interval='5m')
    data_5m.index = data_5m.index.tz_convert('Asia/Kolkata')

    data_15m = yf.download(pair, period='5d', interval='15m')
    data_15m.index = data_15m.index.tz_localize('UTC').tz_convert('Asia/Kolkata')
    
    data_1h = yf.download(pair, period='1mo', interval='1h')
    data_1h.index = data_1h.index.tz_convert('Asia/Kolkata')

    data_1d = yf.download(pair, period='1mo', interval='1d')

    data_5m['indication'] = indicator(data_5m)
    data_15m['indication'] = indicator(data_15m)
    data_1h['indication'] = indicator(data_1h)
    data_1d['indication'] = indicator(data_1d)

    results_5m[pair] = data_5m
    results_15m[pair] = data_15m
    results_1h[pair] = data_1h
    results_1d[pair] = data_1d

# Process data for each interval
Underbought_5m, Overbought_5m = output(results_5m)
Underbought_15m, Overbought_15m = output(results_15m)
Underbought_1h, Overbought_1h = output(results_1h)
Underbought_1d, Overbought_1d = output(results_1d)

# Streamlit app
st.title('Forex RSI Analysis')

# Load CSS
with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Prompt for interval selection
st.markdown("<div class='header'>Choose your intervals to combine:</div>", unsafe_allow_html=True)

# Checkboxes for intervals
show_5m = st.checkbox('Show 5 Minute Interval')
show_15m = st.checkbox('Show 15 Minute Interval')
show_1h = st.checkbox('Show 1 Hour Interval')
show_1d = st.checkbox('Show 1 Day Interval')

selected_intervals = []
if show_5m:
    selected_intervals.append('5m')
if show_15m:
    selected_intervals.append('15m')
if show_1h:
    selected_intervals.append('1h')
if show_1d:
    selected_intervals.append('1d')

# Display results in horizontal manner
if selected_intervals:
    cols = st.columns(len(selected_intervals))

    interval_data = {
        '5m': (Underbought_5m, Overbought_5m),
        '15m': (Underbought_15m, Overbought_15m),
        '1h': (Underbought_1h, Overbought_1h),
        '1d': (Underbought_1d, Overbought_1d)
    }

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
