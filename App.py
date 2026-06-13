import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# Set up mobile-friendly page layout
st.set_page_config(page_title="Penny Stock Scanner", layout="centered")
st.title("📈 Penny Stock Pattern Scanner")

st.header("Scanner Settings")
max_price = st.slider("Maximum Stock Price ($)", 0.50, 10.00, 5.00, step=0.50)
selected_pattern = st.selectbox("Select Chart Pattern", ["Bullish Engulfing", "Doji", "Hammer"])

pattern_map = {
    "Bullish Engulfing": "engulfing",
    "Doji": "doji",
    "Hammer": "hammer"
}

# A starter list of volatile penny stocks to scan
tickers = ["SNDL", "CEI", "ZOM", "ANY", "XSPA", "HCMC", "CTRM", "IDEX"]

if st.button("🚀 Run Live Market Scan", use_container_width=True):
    st.write("Scanning charts... please wait...")
    matches = []
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="30d")
            
            if df.empty or len(df) < 5:
                continue
                
            current_price = df['Close'].iloc[-1]
            
            if current_price <= max_price:
                pattern_df = df.ta.cdl_pattern(name=pattern_map[selected_pattern])
                
                if not pattern_df.empty:
                    signal = pattern_df.iloc[-1].values[0]
                    if signal > 0:  
                        matches.append({
                            "Ticker": ticker,
                            "Price": f"${current_price:.2f}",
                            "Volume": int(df['Volume'].iloc[-1])
                        })
        except Exception as e:
            continue
            
    if matches:
        st.success(f"Found {len(matches)} matching setups!")
        result_df = pd.DataFrame(matches)
        st.dataframe(result_df, use_container_width=True)
    else:
        st.info("No matching patterns found right now. Try adjusting filters.")
