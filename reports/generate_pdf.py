from fpdf import FPDF
import datetime
import re
import pandas as pd
import requests
import os
from urllib.parse import urlparse
import tempfile
import matplotlib.pyplot as plt


def remove_unicode(text):
    return re.sub(r'[^\x00-\x7F]+', '', text)

class PDFReport(FPDF):
    def __init__(self, orientation='L', unit='mm', format='A4'):
        super().__init__(orientation, unit, format)
        self.set_auto_page_break(auto=True, margin=10)
        self.temp_files = []  # Track temporary files for cleanup

    def __del__(self):
        # Clean up temporary files
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass

    def get_coin_icon(self, symbol, size=32):
        """
        Fetch coin icon from CoinGecko API and return temporary file path
        
        Parameters:
        - symbol: coin symbol (e.g., 'BTC', 'ETH')
        - size: icon size (32, 64, 128, 256)
        
        Returns:
        - path to temporary PNG file or None if failed
        """
        try:
            # Normalize symbol
            symbol = symbol.upper().strip()
            
            # Map common symbols to CoinGecko IDs
            symbol_map = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum', 
                'ADA': 'cardano',
                'DOT': 'polkadot',
                'SOL': 'solana',
                'AVAX': 'avalanche-2',
                'MATIC': 'matic-network',
                'LINK': 'chainlink',
                'UNI': 'uniswap',
                'LTC': 'litecoin',
                'BCH': 'bitcoin-cash',
                'XRP': 'ripple',
                'DOGE': 'dogecoin',
                'SHIB': 'shiba-inu',
                'TRX': 'tron',
                'ATOM': 'cosmos',
                'ALGO': 'algorand',
                'XLM': 'stellar',
                'VET': 'vechain',
                'FIL': 'filecoin',
                'THETA': 'theta-token',
                'AAVE': 'aave',
                'COMP': 'compound-governance-token',
                'MKR': 'maker',
                'SUSHI': 'sushi',
                'CRV': 'curve-dao-token',
                'YFI': 'yearn-finance',
                'SNX': 'havven',
                'RUNE': 'thorchain',
                'LUNA': 'terra-luna',
                'NEAR': 'near',
                'FTM': 'fantom',
                'HBAR': 'hedera-hashgraph',
                'FLOW': 'flow',
                'ICP': 'internet-computer',
                'XTZ': 'tezos',
                'EOS': 'eos',
                'MANA': 'decentraland',
                'SAND': 'the-sandbox',
                'AXS': 'axie-infinity',
                'GALA': 'gala',
                'ENJ': 'enjincoin',
                'BAT': 'basic-attention-token',
                'ZRX': '0x',
                'STORJ': 'storj',
                'GRT': 'the-graph',
                'BAND': 'band-protocol',
                'OCEAN': 'ocean-protocol',
                'REN': 'republic-protocol',
                'ZEC': 'zcash',
                'DASH': 'dash',
                'XMR': 'monero',
                'DCR': 'decred',
                'QTUM': 'qtum',
                'ONT': 'ontology',
                'ICX': 'icon',
                'ZIL': 'zilliqa',
                'HOT': 'holo',
                'IOTA': 'iota',
                'NANO': 'nano',
                'DGB': 'digibyte',
                'SC': 'siacoin',
                'WAVES': 'waves',
                'LSK': 'lisk',
                'STEEM': 'steem',
                'KMD': 'komodo',
                'ARDR': 'ardor',
                'STRAT': 'stratis',
                'BNB': 'binancecoin',
                'BUSD': 'binance-usd',
                'USDT': 'tether',
                'USDC': 'usd-coin',
                'DAI': 'dai',
                'TUSD': 'true-usd',
                'PAX': 'paxos-standard',
                'GUSD': 'gemini-dollar'
            }
            
            coin_id = symbol_map.get(symbol, symbol.lower())
            
            # CoinGecko API endpoint for coin icons
            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
            
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                icon_url = data.get('image', {}).get('small')  # 32x32 size
                
                if icon_url:
                    # Download the icon
                    icon_response = requests.get(icon_url, timeout=5)
                    if icon_response.status_code == 200:
                        # Create temporary file
                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                        temp_file.write(icon_response.content)
                        temp_file.close()
                        
                        # Track for cleanup
                        self.temp_files.append(temp_file.name)
                        return temp_file.name
            
            return None
            
        except Exception as e:
            print(f"Failed to fetch icon for {symbol}: {e}")
            return None

    def add_coin_with_icon(self, text, symbol, icon_size=6):
        """
        Add coin name with icon - maintains consistent text sizing
        
        Parameters:
        - symbol: coin symbol for icon lookup
        - text: text to display
        - icon_size: size of icon in mm
        """
        # Set font to match other paragraphs (bold, size 10)
        self.set_font("Arial", "B", 10)
        self.set_text_color(30, 30, 30)
        
        # Get current position
        current_x = self.get_x()
        current_y = self.get_y()
        
        # Try to get coin icon
        icon_path = self.get_coin_icon(symbol)
        
        if icon_path:
            # Add icon
            self.image(icon_path, x=current_x, y=current_y, w=icon_size, h=icon_size)
            # Move cursor to right of icon with small gap
            self.set_xy(current_x + icon_size + 2, current_y)
        
        # Add text with same font size as other paragraphs
        self.multi_cell(0, 6, text)
        self.set_text_color(30, 30, 30)
        self.ln(2)

    def header(self):
        self.set_font("Arial", "B", 14)
        self.set_text_color(30, 30, 30)
        self.cell(0, 10, "TradingSignals Report", ln=True, align="C")
        self.set_font("Arial", "B", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
        self.ln(4)
        self.set_draw_color(180, 180, 180)
        self.rect(5.0, 5.0, 287.0, 200.0)  # Landscape dimensions (A4 = 297 x 210mm)

    def add_section_title(self, title):
        self.set_font("Arial", "B", 13)
        self.set_text_color(20, 20, 100)
        self.cell(0, 10, remove_unicode(title), ln=True)
        self.set_text_color(0, 0, 0)
        self.ln(3)

    def add_paragraph(self, text, color=None, bold=False):
        self.set_font("Arial", "B", 10)  # Make all text bold and consistent size
        clean_text = remove_unicode(str(text))
        if color:
            self.set_text_color(color[0], color[1], color[2])
        else:
            self.set_text_color(30, 30, 30)
        self.multi_cell(0, 6, clean_text)
        self.set_text_color(30, 30, 30)
        self.ln(2)

    def add_image(self, path, w=120, h=100, size_type='default'):
        """
        Add image with flexible sizing options
        
        Parameters:
        - path: image file path
        - w, h: default width and height (used when size_type='default')
        - size_type: 'default', 'large', 'medium', 'small', 'full_width'
        """
        # Calculate available page width (landscape A4 = 297mm, with margins ≈ 277mm usable)
        available_width = self.w - 2 * self.l_margin  # ≈ 277mm for landscape A4
        available_height = self.h - 2 * self.t_margin - 30  # Leave space for header/footer
        
        if size_type == 'large':
            # Use 90% of available width, maintain aspect ratio
            img_width = available_width * 0.9
            img_height = img_width * 0.6  # Assume 5:3 aspect ratio for charts
        elif size_type == 'full_width':
            # Use full available width
            img_width = available_width
            img_height = available_width * 0.6
        elif size_type == 'medium':
            # Use 70% of available width
            img_width = available_width * 0.7
            img_height = img_width * 0.6
        elif size_type == 'small':
            # Use 50% of available width
            img_width = available_width * 0.5
            img_height = img_width * 0.6
        else:  # 'default'
            img_width = w
            img_height = h
        
        # Center the image horizontally
        x_position = (self.w - img_width) / 2
        
        # Check if image fits on current page, if not add new page
        if self.get_y() + img_height > self.h - self.b_margin:
            self.add_page()
        
        self.image(path, x=x_position, w=img_width, h=img_height)
        self.ln(3)

    def add_key_value_table(self, summary_dict):
        self.set_font("Arial", "B", 9)
        self.set_fill_color(200, 200, 200)
        self.set_text_color(0)

        self.cell(60, 8, "Metric", border=1, align='C', fill=True)
        self.cell(60, 8, "Value", border=1, align='C', fill=True)
        self.ln()

        self.set_font("Arial", "B", 8)
        for key, value in summary_dict.items():
            key_clean = remove_unicode(str(key)).replace("_", " ").title()
            self.set_text_color(0, 0, 0)
            self.cell(60, 8, key_clean, border=1, align='C')
            
            # Color coding based on specific metric types
            value_str = str(value).lower()
            
            if 'success rate' in key_clean.lower():
                # Success rate should always be green
                self.set_text_color(0, 150, 0)
            elif 'avg profit' in key_clean.lower() or 'average profit' in key_clean.lower():
                # Average profit: green for positive, red for negative
                try:
                    # Try to extract numeric value from percentage or number
                    import re
                    numeric_match = re.search(r'-?\d+\.?\d*', str(value))
                    if numeric_match:
                        numeric_val = float(numeric_match.group())
                        if numeric_val > 0:
                            self.set_text_color(0, 150, 0)  # Green for positive
                        elif numeric_val < 0:
                            self.set_text_color(200, 0, 0)  # Red for negative
                        else:
                            self.set_text_color(0, 0, 0)  # Black for zero
                    else:
                        self.set_text_color(0, 0, 0)
                except:
                    self.set_text_color(0, 0, 0)
            elif 'successful signals' in key_clean.lower() or 'success' in key_clean.lower():
                # Successful signals should be green
                self.set_text_color(0, 150, 0)
            elif 'failed signals' in key_clean.lower() or 'fail' in key_clean.lower():
                # Failed signals should be red
                self.set_text_color(200, 0, 0)
            elif 'neutral signals' in key_clean.lower() or 'hold signals' in key_clean.lower():
                # Neutral/Hold signals should be yellow/orange
                self.set_text_color(200, 150, 0)
            elif any(word in key_clean.lower() for word in ['profit', 'win', 'gain', 'positive']):
                # Other profit-related metrics
                self.set_text_color(0, 150, 0)
            elif any(word in key_clean.lower() for word in ['loss', 'drawdown', 'negative']):
                # Other loss-related metrics
                self.set_text_color(200, 0, 0)
            else:
                # Default black for other metrics
                self.set_text_color(0, 0, 0)
                
            self.cell(60, 8, str(value), border=1, align='C')
            self.set_text_color(0, 0, 0)
            self.ln()
        self.ln(3)

    def get_confidence_color(self, confidence_percent):
        """Return RGB color based on confidence percentage (0-100)"""
        if confidence_percent >= 80:
            return (0, 100, 0)
        elif confidence_percent >= 60:
            return (50, 150, 50)
        elif confidence_percent >= 40:
            return (100, 100, 100)
        elif confidence_percent >= 20:
            return (200, 100, 100)
        else:
            return (200, 0, 0)

    def get_signal_color(self, signal):
        """Return RGB color based on signal type"""
        signal_str = str(signal).lower().strip()
        
        if any(word in signal_str for word in ['buy', 'long', 'bullish', 'up', 'bull']):
            return (0, 100, 0)
        elif any(word in signal_str for word in ['sell', 'short', 'bearish', 'down', 'bear']):
            return (200, 0, 0)
        elif any(word in signal_str for word in ['hold', 'neutral', 'wait', 'sideways']):
            return (100, 100, 100)
        else:
            try:
                float(signal_str)
                return (100, 100, 100)
            except:
                return (100, 100, 100)

    def get_sentiment_color(self, sentiment):
        """Return RGB color based on sentiment"""
        if isinstance(sentiment, (int, float)):
            if sentiment > 0.25:
                return (0, 100, 0)
            elif sentiment < -0.25:
                return (200, 0, 0)
            else:
                return (100, 100, 100)
        else:
            sentiment_str = str(sentiment).lower()
            if 'bullish' in sentiment_str or 'positive' in sentiment_str:
                return (0, 100, 0)
            elif 'bearish' in sentiment_str or 'negative' in sentiment_str:
                return (200, 0, 0)
            else:
                return (100, 100, 100)

    def get_row_confidence_color(self, row):
        """Return RGB background color for entire row based on success/failure and confidence level from Return %"""
        # Get return percentage and result column
        return_percent = row.get('Return %', 0)
        result = str(row.get('result', '')).upper().strip()
        
        try:
            return_val = float(return_percent)
        except:
            return (255, 255, 255)  # White for invalid data
        
        # Determine if it's a successful trade using the result column
        is_successful = result == 'SUCCESS'
        
        # Calculate confidence based on absolute return percentage
        abs_return = abs(return_val)
        
        # Define confidence levels based on return magnitude
        if abs_return >= 0.5:  # High confidence (0.5% or more)
            confidence_level = "high"
        elif abs_return >= 0.2:  # Medium confidence (0.2% to 0.5%)
            confidence_level = "medium"
        else:  # Low confidence (less than 0.2%)
            confidence_level = "low"
        
        # Apply color grading based on success and confidence
        if is_successful:
            # Success - Green shades (darker for higher confidence)
            if confidence_level == "high":
                return (200, 255, 200)  # Dark green shade
            elif confidence_level == "medium":
                return (230, 255, 230)  # Medium green shade
            else:  # low confidence
                return (245, 255, 245)  # Light green shade
        else:
            # Failure - Red shades (darker for higher confidence)
            if confidence_level == "high":
                return (255, 200, 200)  # Dark red shade
            elif confidence_level == "medium":
                return (255, 230, 230)  # Medium red shade
            else:  # low confidence
                return (255, 245, 245)  # Light red shade

    def add_table_with_coin_icons(self, dataframe, columns, apply_row_coloring=False):
        """Enhanced table method that adds coin icons in the 'coin' column"""
        self.set_font("Arial", "B", 8)
        self.set_fill_color(200, 200, 200)
        self.set_text_color(0)

        # Custom column widths based on content needs (Landscape page = 275mm usable)
        col_widths = {
            "timestamp": 25,
            "Timestamp": 25,
            "coin": 18,  # Slightly wider for icon + text
            "open": 16,
            "close": 16,
            "rsi": 10,
            "macd": 12,
            "bollinger": 18,
            "sentiment": 16,
            "volatility": 15,
            "signal": 14,
            "confidence": 16,
            "exit_price": 18,
            "take_profit": 18,
            "stop_loss": 18,
            "exit_reason": 16,
            "Return %": 14,
            "result": 14
        }

        # Table header
        for col in columns:
            self.cell(col_widths.get(col, 16), 7, str(col), border=1, align='C', fill=True)
        self.ln()

        # Table rows
        self.set_font("Arial", "B", 7)
        for _, row in dataframe.iterrows():
            row_start_y = self.get_y()
            
            for col_idx, col in enumerate(columns):
                value = str(row[col])
                
                # Apply row background coloring only for backtest table
                if apply_row_coloring:
                    row_bg_color = self.get_row_confidence_color(row)
                    self.set_fill_color(row_bg_color[0], row_bg_color[1], row_bg_color[2])
                    
                    # Special coloring for signal column in backtest table
                    if col == 'signal':
                        signal_str = value.lower().strip()
                        if any(word in signal_str for word in ['buy', 'long', 'bullish', 'up', 'bull']):
                            self.set_text_color(0, 150, 0)  # Bright green for BUY
                        elif any(word in signal_str for word in ['sell', 'short', 'bearish', 'down', 'bear']):
                            self.set_text_color(150, 0, 0)  # Bright red for SELL
                        else:
                            self.set_text_color(0, 0, 0)  # Black for other signals
                    else:
                        self.set_text_color(0, 0, 0)  # Black for all other columns
                else:
                    self.set_fill_color(255, 255, 255)
                    
                    # Apply text coloring based on column content for non-backtest tables
                    if col == 'signal':
                        color = self.get_signal_color(value)
                    elif col == 'sentiment':
                        color = self.get_sentiment_color(row[col])
                    elif col == 'result':
                        if any(word in value.lower() for word in ['win', 'profit', 'gain', 'positive']):
                            color = (0, 100, 0)
                        elif any(word in value.lower() for word in ['loss', 'lose', 'negative']):
                            color = (200, 0, 0)
                        else:
                            color = (0, 0, 0)
                    elif col == 'Return %':
                        try:
                            return_val = float(row[col])
                            if return_val > 0:
                                color = (0, 100, 0)
                            elif return_val < 0:
                                color = (200, 0, 0)
                            else:
                                color = (0, 0, 0)
                        except:
                            color = (0, 0, 0)
                    elif col in ['macd', 'bollinger']:
                        color = self.get_signal_color(value)
                    else:
                        color = (0, 0, 0)
                    
                    self.set_text_color(color[0], color[1], color[2])
                
                # Special handling for coin column with icons
                if col == 'coin':
                    # Save current position
                    cell_x = self.get_x()
                    cell_y = self.get_y()
                    
                    # Draw cell border first
                    self.cell(col_widths.get(col, 16), 7, "", border=1, align='C', fill=True)
                    
                    # Try to add coin icon
                    icon_path = self.get_coin_icon(value, size=32)
                    if icon_path:
                        # Add small icon inside the cell
                        icon_size = 4  # 4mm icon
                        icon_x = cell_x + 2  # 2mm from left edge
                        icon_y = cell_y + 1.5  # Center vertically
                        self.image(icon_path, x=icon_x, y=icon_y, w=icon_size, h=icon_size)
                        
                        # Add text next to icon
                        self.set_xy(cell_x + icon_size + 4, cell_y)
                        self.set_font("Arial", "B", 6)  # Smaller font for coin text
                        self.cell(col_widths.get(col, 16) - icon_size - 4, 7, value, align='L')
                        self.set_font("Arial", "B", 7)  # Reset font
                    else:
                        # Fallback: just add text
                        self.set_xy(cell_x, cell_y)
                        self.cell(col_widths.get(col, 16), 7, value, border=1, align='C', fill=True)
                else:
                    # Regular cell
                    self.cell(col_widths.get(col, 16), 7, value, border=1, align='C', fill=True)
            
            self.set_text_color(0, 0, 0)  # Reset color
            self.ln()
        self.ln(3)

    def add_table(self, dataframe, columns, apply_row_coloring=False):
        """Wrapper method to use enhanced table with coin icons"""
        self.add_table_with_coin_icons(dataframe, columns, apply_row_coloring)


def create_pdf_report(symbol, interval, signal_info, risk_info, timing_info, summary, pdf_path, backtest_df, headlines):
    pdf = PDFReport()
    pdf.add_page()

    # Extract coin symbol for icon display
    coin_symbol = symbol.replace('USDT', '').replace('USD', '').replace('BTC', '').replace('ETH', '')
    if not coin_symbol:
        coin_symbol = symbol.split('/')[0] if '/' in symbol else symbol[:3]

    # 1. Signal Info
    pdf.add_section_title("1. Signal Details")
    
    # Use the new method to add coin name with icon
    pdf.add_coin_with_icon(f"{symbol}",coin_symbol)
    pdf.add_paragraph(f"Interval: {interval}")
    
    # Color code the signal based on type
    signal_text = f"Signal: {signal_info['signal']} ({signal_info['confidence']}% confidence)"
    signal_color = pdf.get_signal_color(signal_info['signal'])
    pdf.add_paragraph(signal_text, color=signal_color, bold=True)
    
    # Color code sentiment
    sentiment_text = f"Sentiment Score: {signal_info['sentiment']}"
    sentiment_color = pdf.get_sentiment_color(signal_info['sentiment'])
    pdf.add_paragraph(sentiment_text, color=sentiment_color, bold=True)

    # 1B. Live Signal Explanation
    pdf.add_section_title("1B. Live Signal Explanation")

    signal = signal_info['signal']
    confidence = signal_info['confidence']
    sentiment = signal_info.get("sentiment", "neutral")
    volatility = signal_info.get("indicators", {}).get("volatility", "N/A")

    # Confidence phrasing
    if confidence >= 80:
        strength_phrase = "a very high level of confidence"
    elif confidence >= 65:
        strength_phrase = "a strong degree of confidence"
    elif confidence >= 55:
        strength_phrase = "moderate confidence"
    else:
        strength_phrase = "a cautious confidence level"

    # Sentiment phrasing
    if isinstance(sentiment, (float, int)):
        if sentiment > 0.25:
            sentiment_description = "with broadly optimistic sentiment observed in the market"
        elif sentiment < -0.25:
            sentiment_description = "during a period of prevailing negative sentiment"
        else:
            sentiment_description = "in a relatively neutral sentiment environment"
    else:
        sentiment_description = "with sentiment conditions being inconclusive"

    # Volatility phrasing
    if isinstance(volatility, (float, int)):
        if volatility > 1.5:
            volatility_phrase = f"Volatility was relatively high ({volatility}), suggesting potential price swings."
        elif volatility > 0.8:
            volatility_phrase = f"Moderate volatility was present at {volatility}, allowing for reasonable price movement."
        else:
            volatility_phrase = f"Low volatility conditions ({volatility}) suggest a stable but cautious environment."
    else:
        volatility_phrase = f"Volatility at the time of signal generation was recorded as {volatility}."

    # Final explanation
    if signal == "BUY":
        explanation_text = (
            f"A BUY signal was generated with {strength_phrase}. "
            f"This indicates a favorable outlook for upward price movement, {sentiment_description}. "
            f"{volatility_phrase} "
            "The system determined that market conditions were conducive to initiating a long position, backed by historical consistency."
        )
    elif signal == "SELL":
        explanation_text = (
            f"A SELL signal was issued with {strength_phrase}, suggesting the likelihood of downward market movement. "
            f"The call was made {sentiment_description}. "
            f"{volatility_phrase} "
            "This action reflects conditions where initiating a short or exit position was considered technically sound."
        )
    else:  # HOLD
        explanation_text = (
            f"A HOLD recommendation was made with {strength_phrase}. "
            f"This reflects a lack of strong directional bias at the time, {sentiment_description}. "
            f"{volatility_phrase} "
            "In such environments, the system advises remaining on the sidelines to avoid low-confidence trades."
        )

    pdf.add_paragraph(explanation_text)


    # 1C. Price Snapshot
    if 'price_snapshot' in signal_info:
        pdf.ln(2)
        pdf.set_x(pdf.l_margin)
        pdf.add_section_title("1C. Price Snapshot (Latest 5 rows)")
        price_snapshot = signal_info['price_snapshot'].copy()
        price_snapshot = price_snapshot.tail(5)
        price_snapshot.index = pd.to_datetime(price_snapshot.index)
        price_snapshot.reset_index(inplace=True)

        # Adjust column names safely
        if price_snapshot.shape[1] == 7:
            price_snapshot.columns = ["Timestamp", "Open", "High", "Low", "Close", "Volume", "Extra"]
            price_snapshot.drop("Extra", axis=1, inplace=True)
        elif price_snapshot.shape[1] == 6:
            price_snapshot.columns = ["Timestamp", "Open", "High", "Low", "Close", "Volume"]

        # Add symbol
        price_snapshot["Symbol"] = symbol
        price_snapshot = price_snapshot[["Timestamp", "Symbol", "Open", "High", "Low", "Close", "Volume"]]

        for col in ["Open", "High", "Low", "Close"]:
            price_snapshot[col] = price_snapshot[col].apply(lambda x: "{:,.2f}".format(x))
        price_snapshot["Volume"] = price_snapshot["Volume"].round(2)

        # Price snapshot table without row coloring
        pdf.add_table(price_snapshot, list(price_snapshot.columns), apply_row_coloring=False)

    # 1D. Top 5 Sentiment Headlines
    if headlines:
        pdf.add_section_title("1D. Top 10 Sentiment Headlines 📰")
        
        for i, item in enumerate(headlines[:10], 1):
            title = remove_unicode(item.get("title", ""))
            score = item.get("score", 0)
            published = item.get("published", "N/A")
            source = item.get("source", "Unknown")
            link = item.get("link", "")
            category = item.get("category", "")
            
            emoji = "[+]" if score > 0.25 else "[-]" if score < -0.25 else "[·]"
            headline_color = pdf.get_sentiment_color(score)

            # Headline with Score
            pdf.set_font("Arial", "B", 10)
            pdf.set_text_color(*headline_color)
            pdf.multi_cell(0, 6, f"{i}. {emoji} {title} (Score: {score:.2f})")
            
            # Source Info
            pdf.set_font("Arial", "", 8)
            pdf.set_text_color(100, 100, 100)
            pdf.multi_cell(0, 5,
                f"Published: {published}| Source: {source}| Category: {category if category else 'N/A'}"
            )
            
            # Link
            pdf.set_text_color(50, 50, 200)
            pdf.multi_cell(0, 5, f"{link}")
            
            pdf.ln(2)  # space between entries

        # Add sentiment explanation
        signal_sentiment = signal_info.get("sentiment", "neutral")
        explanation_color = pdf.get_sentiment_color(signal_sentiment)
        explanation_text = {
            "bullish": "Most headlines had a positive tone. Market sentiment appears optimistic.",
            "bearish": "Many headlines indicated negative or fearful tone. Market may be under pressure.",
            "neutral": "Headlines showed mixed or weak sentiment. Market is undecided or consolidating."
        }
        pdf.add_paragraph(f"\nSentiment Interpretation: {explanation_text.get(signal_sentiment, 'No data.')}",
                        color=explanation_color)

    # 1E. Indicators
    if 'indicators' in signal_info:
        pdf.add_section_title("1E. Technical Indicators")
        ind = signal_info['indicators']
        
        # Color code MACD
        macd_text = f"MACD Signal: {ind.get('macd', 'N/A')}"
        macd_color = pdf.get_signal_color(ind.get('macd', 'N/A'))
        pdf.add_paragraph(macd_text, color=macd_color, bold=True)
        
        rsi_raw = ind.get('rsi', 'N/A')
        if isinstance(rsi_raw, tuple) and len(rsi_raw) == 2:
            rsi_signal = rsi_raw[1]
        else:
            rsi_signal = str(rsi_raw)

        # Color code RSI
        rsi_text = f"RSI Signal: {rsi_signal}"
        rsi_color = pdf.get_signal_color(rsi_signal)
        pdf.add_paragraph(rsi_text, color=rsi_color, bold=True)
        
        # Color code Bollinger Bands
        bb_text = f"Bollinger Bands Signal: {ind.get('bb', 'N/A')}"
        bb_color = pdf.get_signal_color(ind.get('bb', 'N/A'))
        pdf.add_paragraph(bb_text, color=bb_color, bold=True)
        
        pdf.add_paragraph(f"Volatility: {ind.get('volatility', 'N/A')}")

    # 2. Risk Management
    pdf.add_section_title("2. Risk Management")

    # Extract entry price
    entry_price = "N/A"
    try:
        price_df = signal_info.get("price_snapshot", None)
        if isinstance(price_df, pd.DataFrame) and not price_df.empty:
            raw_entry = price_df["close"].iloc[-1]
            entry_price = f"{raw_entry:,.2f}"
        else:
            raw_entry = float(risk_info.get("entry_price", 0))
    except:
        raw_entry = float(risk_info.get("entry_price", 0))

    # Add risk details
    pdf.add_paragraph(f"Entry Price: {entry_price}", color=(0, 0, 200), bold=True)
    pdf.add_paragraph(f"Stop Loss: {risk_info['stop_loss']}", color=(200, 0, 0), bold=True)
    pdf.add_paragraph(f"Take Profit: {risk_info['take_profit']}", color=(0, 100, 0), bold=True)
    pdf.add_paragraph(f"Risk-Reward Ratio: {risk_info['rr_ratio']}", bold=True)

    # Risk Level
    risk_level = risk_info['risk_level'].lower()
    risk_color = (0, 100, 0) if 'low' in risk_level else (200, 0, 0) if 'high' in risk_level else (200, 100, 0)
    pdf.add_paragraph(f"Risk Level: {risk_info['risk_level']}", color=risk_color, bold=True)

    # Expected Profit
    try:
        profit_val = float(str(risk_info['expected_profit_percent']).replace('%', ''))
        profit_color = (0, 100, 0) if profit_val > 0 else (200, 0, 0)
    except:
        profit_color = (0, 0, 0)
    pdf.add_paragraph(f"Expected Profit % : {risk_info['expected_profit_percent']}", color=profit_color, bold=True)

    # Formal explanation
    pdf.add_paragraph(
        f"This risk management setup is based on the entry price of {entry_price}, "
        f"with a Stop Loss defined at {risk_info['stop_loss']} and a Take Profit target at {risk_info['take_profit']}. "
        f"The system uses an intelligent volatility-adjusted approach for risk placement, incorporating factors such as "
        f"market trend strength, overall sentiment, and asset-specific volatility to dynamically adjust the buffer zones. "
        f"The Risk-Reward ratio of {risk_info['rr_ratio']} reflects the balance between potential downside protection and profit opportunity."
    )

    # HOLD Note
    if signal_info['signal'].upper() == "HOLD":
        pdf.add_paragraph(
            "Note: As this is a HOLD signal, Stop Loss, Take Profit, and expected profit values are set to 0 by default. "
            "No active trade is recommended under current market conditions.",
            color=(150, 100, 0),
            bold=True
        )

    # ➕ Clean and accurate Risk Management Plot
    try:
        entry = float(str(raw_entry).replace(",", ""))
        sl = float(risk_info['stop_loss'])
        tp = float(risk_info['take_profit'])

        import matplotlib.pyplot as plt
        import os

        levels = [sl, entry, tp]
        labels = ['Stop Loss', 'Entry Price', 'Take Profit']
        colors = ['red', 'blue', 'green']

        plt.figure(figsize=(10, 4))
        for level, label, color in zip(levels, labels, colors):
            plt.axhline(y=level, color=color, linestyle='--', linewidth=2, label=f"{label}: {level:,.2f}")

        # Fill zones
        plt.fill_betweenx([sl, entry], 0, 1, color='red', alpha=0.1, transform=plt.gca().get_yaxis_transform())
        plt.fill_betweenx([entry, tp], 0, 1, color='green', alpha=0.1, transform=plt.gca().get_yaxis_transform())

        plt.title("Risk Management Levels", fontsize=14, fontweight='bold')
        plt.xticks([])
        plt.yticks(fontsize=10)
        plt.legend(loc="best", fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        os.makedirs("reports/plots", exist_ok=True)
        img_path = "reports/plots/risk_management_plot.png"
        plt.savefig(img_path)
        plt.close()

        pdf.add_image(img_path, size_type="small")

    except Exception as e:
        pdf.add_paragraph(f"(Plot Error: {e})", color=(255, 0, 0))

    # 3. Timing
    pdf.add_section_title("3. Signal Timing")

    start = timing_info['start']
    end = timing_info['end']
    duration = timing_info['duration']
    formatted_start = start.strftime('%Y-%m-%d %H:%M:%S') if start else 'N/A'
    formatted_end = end.strftime('%Y-%m-%d %H:%M:%S') if end else 'N/A'

    pdf.add_paragraph(f"Valid From: {formatted_start}")
    pdf.add_paragraph(f"Valid To: {formatted_end}")
    pdf.add_paragraph(f"Estimated Duration: {duration}")
    pdf.add_paragraph("Note: This is an estimated signal validity based on ATR, volatility, and confidence. No future data is used.")

    # Entry and Exit Prices
    pdf.ln(1)
    pdf.add_section_title("3B. Entry and Exit Price Range")

    # Entry Price from latest close in price_snapshot
    entry_price = "N/A"
    exit_price_tp = "N/A"
    exit_price_sl = "N/A"
    exit_price_timing = "N/A"

    try:
        price_df = signal_info.get("price_snapshot", None)
        if isinstance(price_df, pd.DataFrame) and not price_df.empty:
            entry_price = price_df["close"].iloc[-1]
            exit_price_timing = price_df["close"].iloc[-1]  # assumed

            # Format them
            entry_price = f"{entry_price:,.2f}"
            exit_price_timing = f"{exit_price_timing:,.2f}"
    except:
        pass

    # From risk_info
    try:
        exit_price_tp = f"{float(risk_info['take_profit']):,.2f}"
        exit_price_sl = f"{float(risk_info['stop_loss']):,.2f}"
    except:
        pass

    pdf.add_paragraph(f"📥 Entry Price: {entry_price}", bold=True)
    pdf.add_paragraph(f"📤 Exit if Take Profit Triggered: {exit_price_tp}", color=(0, 100, 0), bold=True)
    pdf.add_paragraph(f"📉 Exit if Stop Loss Triggered: {exit_price_sl}", color=(200, 0, 0), bold=True)
    pdf.add_paragraph(f"⏳ Note: Exit if the Duration is Expired before the Price Hit Stop Loss or Take Profit.", color=(100, 100, 100), bold=True)


    # 4. Backtest Table with row coloring
    pdf.add_section_title("4. Backtest Table (Last 250 candles)")
    formatted_df = format_backtest_table(backtest_df)
    pdf.add_table(formatted_df, list(formatted_df.columns), apply_row_coloring=True)

    # Clarify return % for SELL signals
    pdf.add_paragraph(
        "Note: For BUY signals, a higher exit price than entry is a SUCCESS. "
        "For SELL signals, a lower exit price is a SUCCESS. "
        "Net return % includes 0.2% Binance commission but does not affect the SUCCESS/FAILURE label. ",
        color=(50, 50, 50)
    )

   #pdf.ln(50)
    # 5. Summary
    pdf.add_section_title("5. Backtest Summary")
    if isinstance(summary, dict):
        pdf.add_key_value_table(summary)
    else:
        pdf.add_paragraph(str(summary))

    #pdf.ln(50)
    # 6. Charts - UPDATED WITH LARGER PRICE CHART
    pdf.add_section_title("6. Visualizations")
    
    # Add the main price chart with LARGE size (90% of page width)
    #pdf.add_image("reports/plots/price_chart.png", size_type='large')
    # pdf.add_image("reports/plots/dashboard_chart.png", size_type='large')
    # pdf.add_image("reports/plots/verticalstack_chart.png", size_type='large')
    # pdf.add_image("reports/plots/sidebyside_chart.png", size_type='large')
    # pdf.add_image("reports/plots/heatmap_chart.png", size_type='large')

    pdf.add_image("reports/plots/price_chart_price.png", size_type='large')
    pdf.add_image("reports/plots/price_chart_pnl.png", size_type='large')
    pdf.add_image("reports/plots/price_chart_cumulative.png", size_type='large')
    #pdf.add_image("reports/plots/price_chart_summary.png", size_type='large')
    
    # Add the pie chart with SMALL size (keep it compact as requested)
    pdf.add_image("reports/plots/backtest_chart.png", size_type='default')

    pdf.output(pdf_path)

def format_backtest_table(df, max_rows=30):
    columns = [
        "timestamp", "coin", "open", "close", "rsi", "macd",
        "bollinger", "sentiment", "volatility", "signal", "confidence",
        "exit_price", "take_profit", "stop_loss", "exit_reason",
        "net_return_percent", "result"
    ]
    df = df[columns].copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")
    for col in ["open", "close", "exit_price", "take_profit", "stop_loss"]:
        df[col] = df[col].apply(lambda x: "{:,.2f}".format(x))
    df["rsi"] = df["rsi"].round(1)
    df["net_return_percent"] = df["net_return_percent"].round(2)

    df.rename(columns={"net_return_percent": "Return %"}, inplace=True)

    return df.tail(max_rows).reset_index(drop=True)