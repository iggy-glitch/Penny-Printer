import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# Set up mobile-friendly page layout
st.set_page_config(page_title="Pro Stock Scanner", layout="centered")
st.title("🛡️ Alpha Trend Penny Stock Scanner")
st.write("Multi-factor algorithmic filter for high-probability setups.")

st.header("Scanner Core Thresholds")

# UI Sliders optimized for mobile layouts
col1, col2 = st.columns(2)
with col1:
    max_price = st.slider("Max Stock Price ($)", 0.50, 10.00, 5.00, step=0.50)
with col2:
    vol_multiplier = st.slider("Required Volume Surge", 1.5, 4.0, 2.0, step=0.5, help="Current volume must be X times the 20-day average.")

selected_pattern = st.selectbox("Select Core Candlestick Trigger", ["Bullish Engulfing", "Doji", "Hammer"])

# Broad Watchlist: High-activity, volatile micro-caps and penny stocks
tickers = [
    "SNDL", "CEI", "ZOM", "ANY", "XSPA", "MULN", "PHUN", "MARK", 
    "WISH", "SENS", "CTRM", "IDEX", "GNUS", "PROG", "BBIG", "ATER"
]

# Helper function to manually calculate 14-day RSI without external dependencies
def calculate_rsi(prices, period=14):
    deltas = np.diff(prices)
    seed = deltas[:period]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    rsi = np.zeros_like(prices)
    rsi[:period] = 100. - 100. / (1. + rs)

    for i in range(period, len(prices)):
        delta = deltas[i - 1]
        if delta > 0:
            up_val = delta
            down_val = 0.
        else:
            up_val = 0.
            down_val = -delta
        up = (up * (period - 1) + up_val) / period
        down = (down * (period - 1) + down_val) / period
        rs = up / down if down != 0 else 0
        rsi[i] = 100. - 100. / (1. + rs)
    return rsi

if st.button("🚀 Execute Multi-Factor Market Scan", use_container_width=True):
    st.write(f"Scanning {len(tickers)} assets through multi-layered mathematical criteria...")
    matches = []
    
    for ticker in tickers:
        try:
            # Pull 40 days of history to comfortably calculate 20-day averages and 14-day RSIs
            stock = yf.Ticker(ticker)
            df = stock.history(period="40d")
            
            if df.empty or len(df) < 25:
                continue
                
            # Current Day Core Values
            current_price = df['Close'].iloc[-1]
            current_volume = df['Volume'].iloc[-1]
            
            # --- LAYER 1: ACCURACY FILTER - VOLUME ANALYSIS ---
            # Calculate average volume of the previous 20 days (excluding today)
            avg_volume_20d = df['Volume'].iloc[-21:-1].mean()
            
            # --- LAYER 2: ACCURACY FILTER - TREND DIRECTION ---
            # Calculate 20-day Simple Moving Average (SMA) baseline
            sma_20d = df['Close'].iloc[-21:-1].mean()
            
            # --- LAYER 3: ACCURACY FILTER - MOMENTUM RANGE (RSI) ---
            rsi_values = calculate_rsi(df['Close'].to_numpy(), period=14)
            current_rsi = rsi_values[-1]
            
            # Executing Tiered Criteria Checks
            if current_price <= max_price:
                # 1. Volume must be significantly stronger than average (Institutional Buying)
                if current_volume >= (avg_volume_20d * vol_multiplier):
                    # 2. Price must be above 20 SMA (Confirms macro short-term uptrend)
                    if current_price > sma_20d:
                        # 3. RSI must be healthy (Not dead <30, and not unsustainably overbought >65)
                        if 30 <= current_rsi <= 65:
                            
                            # --- LAYER 4: CANDLESTICK PATTERN MATCHING ENGINE ---
                            open_curr, close_curr = df['Open'].iloc[-1], df['Close'].iloc[-1]
                            high_curr, low_curr = df['High'].iloc[-1], df['Low'].iloc[-1]
                            open_prev, close_prev = df['Open'].iloc[-2], df['Close'].iloc[-2]
                            
                            is_pattern_match = False
                            
                            if selected_pattern == "Bullish Engulfing":
                                if close_prev < open_prev and close_curr > open_curr:
                                    if open_curr <= close_prev and close_curr >= open_prev:
                                        is_pattern_match = True
                                        
                            elif selected_pattern == "Doji":
                                body_size = abs(close_curr - open_curr)
                                total_range = high_curr - low_curr
                                if total_range > 0 and (body_size / total_range) <= 0.1:
                                    is_pattern_match = True
                                    
                            elif selected_pattern == "Hammer":
                                body_size = abs(close_curr - open_curr)
                                lower_wick = min(open_curr, close_curr) - low_curr
                                upper_wick = high_curr - max(open_curr, close_curr)
                                if body_size > 0 and lower_wick >= (2 * body_size) and upper_wick <= (0.5 * body_size):
                                    is_pattern_match = True
                                    
                            if is_pattern_match:
                                surge_ratio = current_volume / avg_volume_20d
                                matches.append({
                                    "Ticker": ticker,
                                    "Price": f"${current_price:.2f}",
                                    "Volume Surge": f"{surge_ratio:.1f}x Normal",
                                    "RSI (14d)": f"{current_rsi:.1f}",
                                    "Trend Status": "Bullish (Above 20 SMA)"
                                })
        except Exception as e:
            continue
            
    # Display Filtered Results
    if matches:
        st.success(f"Found {len(matches)} high-probability confirmations!")
        result_df = pd.DataFrame(matches)
        st.dataframe(result_df, use_container_width=True)
    else:
        st.info("No tickers completely cleared all 4 confirmation layers. Markets are quiet or criteria is highly protective.")
