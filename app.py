import streamlit as st
import yfinance as yf
import pandas as pd

# Set up mobile-friendly page layout
st.set_page_config(page_title="Penny Stock Scanner", layout="centered")
st.title("📈 Advanced Penny Stock Scanner")

st.header("Scanner Settings")

# Layout columns for mobile UI sliders
col1, col2 = st.columns(2)
with col1:
    max_price = st.slider("Max Price ($)", 0.50, 10.00, 5.00, step=0.50)
with col2:
    min_volume = st.number_input("Min Volume", value=100000, step=50000)

# Pattern selection drop-down
selected_pattern = st.selectbox("Select Chart Pattern", ["Bullish Engulfing", "Doji", "Hammer"])

# EXPANDED WATCHLIST: Volatile micro-caps and penny stocks
tickers = [
    "SNDL", "CEI", "ZOM", "ANY", "XSPA", "HCMC", "CTRM", "IDEX",
    "GNUS", "PROG", "BBIG", "MULN", "PHUN", "MARK", "WISH", "SENS"
]

if st.button("🚀 Run Live Market Scan", use_container_width=True):
    st.write(f"Analyzing {len(tickers)} charts for {selected_pattern} setups...")
    matches = []
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="20d")
            
            if df.empty or len(df) < 5:
                continue
                
            current_price = df['Close'].iloc[-1]
            current_volume = df['Volume'].iloc[-1]
            
            # Apply Base Filters
            if current_price <= max_price and current_volume >= min_volume:
                
                # Get data for the last 2 candles
                open_curr, close_curr = df['Open'].iloc[-1], df['Close'].iloc[-1]
                high_curr, low_curr = df['High'].iloc[-1], df['Low'].iloc[-1]
                
                open_prev, close_prev = df['Open'].iloc[-2], df['Close'].iloc[-2]
                
                is_match = False
                
                # 1. PURE MATH PATTERN LOGIC
                if selected_pattern == "Bullish Engulfing":
                    # Prev candle was red, current candle is green and completely swallows the body
                    if close_prev < open_prev and close_curr > open_curr:
                        if open_curr <= close_prev and close_curr >= open_prev:
                            is_match = True
                            
                elif selected_pattern == "Doji":
                    # Body size is tiny compared to total range
                    body_size = abs(close_curr - open_curr)
                    total_range = high_curr - low_curr
                    if total_range > 0 and (body_size / total_range) <= 0.1:
                        is_match = True
                        
                elif selected_pattern == "Hammer":
                    # Small upper body, very long lower wick, tiny/no upper wick
                    body_size = abs(close_curr - open_curr)
                    lower_wick = min(open_curr, close_curr) - low_curr
                    upper_wick = high_curr - max(open_curr, close_curr)
                    if body_size > 0 and lower_wick >= (2 * body_size) and upper_wick <= (0.5 * body_size):
                        is_match = True

                if is_match:  
                    matches.append({
                        "Ticker": ticker,
                        "Price": f"${current_price:.2f}",
                        "Volume": f"{current_volume:,}"
                    })
        except Exception as e:
            continue
            
    if matches:
        st.success(f"Found {len(matches)} matching setups!")
        result_df = pd.DataFrame(matches)
        st.dataframe(result_df, use_container_width=True)
    else:
        st.info("No matching patterns found right now. Try adjusting filters.")

