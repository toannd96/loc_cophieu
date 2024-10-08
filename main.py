import pandas as pd
import pandas_ta as ta
import json
import re
from flask import Flask, request, jsonify, render_template
from vnstock3 import Vnstock
from datetime import datetime, timedelta

app = Flask(__name__)

# Mở tệp JSON với mã hóa UTF-8
with open('signals_config.json', encoding='utf-8') as f:
    signals_map = json.load(f)

# Phân tích dữ liệu chứng khoán
class StockAnalysis:
    def __init__(self, data):
        self.data = data

    # Tính toán chỉ báo MACD
    def calculate_macd(self, short_window=12, long_window=26, signal_window=9):
        macd = ta.macd(self.data['close'], fast=short_window, slow=long_window, signal=signal_window)
        self.data = pd.concat([self.data, macd], axis=1)
        self.data.rename(columns={
            'MACD_12_26_9': 'macd',
            'MACDs_12_26_9': 'signal_line'
        }, inplace=True)
        return self

    # MACD cắt lên đường tín hiệu
    def identify_macd_cross_up(self):
        self.data['macd_cross_up_signal'] = (self.data['macd'] > self.data['signal_line']) & (self.data['macd'].shift(1) <= self.data['signal_line'].shift(1))
        return self

    # MACD cắt xuống đường tín hiệu
    def identify_macd_cross_down(self):
        self.data['macd_cross_down_signal'] = (self.data['macd'] < self.data['signal_line']) & (self.data['macd'].shift(1) >= self.data['signal_line'].shift(1))
        return self

    # Tính toán chỉ báo Bollinger Band
    def calculate_bollinger_bands(self, window=20, std_dev=2):
        bollinger = ta.bbands(self.data['close'], length=window, std=std_dev)
        self.data = pd.concat([self.data, bollinger], axis=1)
        return self

    # Giá chạm dải biên trên dải Bollinger Band
    def identify_bollinger_touch_upper(self):
        self.data['bb_touch_upper'] = self.data['close'] >= self.data['BBU_20_2.0']
        return self

    # Giá chạm dải biên dưới dải Bollinger Band
    def identify_bollinger_touch_lower(self):
        self.data['bb_touch_lower'] = self.data['close'] <= self.data['BBL_20_2.0']
        return self

    # Giá vượt ra ngoài biên trên dải Bollinger Band
    def identify_bollinger_breakout_upper(self):
        self.data['bb_breakout_upper'] = self.data['close'] > self.data['BBU_20_2.0']
        return self

    # Giá vượt ra ngoài biên dưới dải Bollinger Band
    def identify_bollinger_breakout_lower(self):
        self.data['bb_breakout_lower'] = self.data['close'] < self.data['BBL_20_2.0']
        return self
    
    # Tính đường MA cho một khoảng thời gian bất kỳ 
    def calculate_ma(self, window):
        return self.data['close'].rolling(window=window).mean()

    # Giá cắt lên đường MA_N
    def identify_ma_cross_up(self, window):
        ma = self.calculate_ma(window)
        self.data[f'ma_cross_up_{window}'] = (self.data['close'] > ma) & (self.data['close'].shift(1) <= ma.shift(1))
        return self

    # Giá cắt xuống đường MA_N
    def identify_ma_cross_down(self, window):
        ma = self.calculate_ma(window)
        self.data[f'ma_cross_down_{window}'] = (self.data['close'] < ma) & (self.data['close'].shift(1) >= ma.shift(1))
        return self

    # Giá nằm trên đường MA_N
    def identify_ma_above(self, window):
        ma = self.calculate_ma(window)
        self.data[f'ma_above_{window}'] = self.data['close'] > ma
        return self
    
    # Giá nằm dưới đường MA_N
    def identify_ma_below(self, window):
        ma = self.calculate_ma(window)
        self.data[f'ma_below_{window}'] = self.data['close'] < ma
        return self

    # Tính toán chỉ báo RSI
    def calculate_rsi(self, window=14):
        rsi = ta.rsi(self.data['close'], length=window)
        self.data = pd.concat([self.data, rsi.rename('rsi')], axis=1)
        return self

    # RSI > 70
    def identify_rsi_gt_overbought(self):
        self.data['rsi_gt_overbought'] = self.data['rsi'] > 70
        return self

    # RSI < 70
    def identify_rsi_lt_overbought(self):
        self.data['rsi_lt_overbought'] = self.data['rsi'] < 70
        return self

    # RSI < 30
    def identify_rsi_lt_oversold(self):
        self.data['rsi_lt_oversold'] = self.data['rsi'] < 30
        return self

    # RSI > 30
    def identify_rsi_gt_oversold(self):
        self.data['rsi_gt_oversold'] = self.data['rsi'] > 30
        return self

    # Giá vượt đỉnh theo khoảng thời gian (window)
    def identify_high_breakout(self, window):
        self.data[f'price_high_{window}'] = self.data['high'].rolling(window=window).max()
        self.data[f'price_high_breakout_{window}'] = self.data['close'] > self.data[f'price_high_{window}'].shift(1)
        return self

    # Giá thủng đáy theo khoảng thời gian (window)
    def identify_low_breakout(self, window):
        self.data[f'price_low_{window}'] = self.data['low'].rolling(window=window).min()
        self.data[f'price_low_breakout_{window}'] = self.data['close'] < self.data[f'price_low_{window}'].shift(1)
        return self

# Lấy thông tin về mã chứng khoán
class StockInfo:
    def __init__(self, stock):
        self.stock = stock

    # Danh sách mã chứng khoán theo nhóm
    def get_symbols_by_group(self, group='VN30'):
        return self.stock.listing.symbols_by_group(group)

    # Danh sách mã chứng khoán theo ngành
    def get_symbols_by_industry(self, industry=None):
        industry_symbols = self.stock.listing.symbols_by_industries()
        if industry:
            return industry_symbols[industry_symbols['icb_name3'] == industry]
        else:
            return industry_symbols

    # Danh sách thuộc nhóm và ngành
    def get_filtered_symbols(self, symbols_group, symbols_industry):
        symbol_industries = symbols_industry['symbol'].tolist()
        return list(set(symbols_group) & set(symbol_industries))

    def get_company_name(self, industry_symbols, symbol):
        return industry_symbols[industry_symbols['symbol'] == symbol]['organ_name'].values[0]

    def get_industry_name(self, industry_symbols, symbol):
        return industry_symbols[industry_symbols['symbol'] == symbol]['icb_name3'].values[0]

class ExtractSignal:
    @staticmethod
    def extract_window(prefix, signal):
        match = re.search(fr'{prefix}.*_(\d+)$', signal)
        if match:
            return int(match.group(1))
        return None

    @staticmethod
    def extract_action(prefix, signal):
        match = re.search(fr'{prefix}_(.*?)(?:_\d+)?$', signal)
        if match:
            return match.group(1)
        return None

    @staticmethod
    def extract_prefix(signal):
        match = re.match(r'^([a-z]+)_', signal)
        if match:
            return match.group(1)
        return None

def process_ma_signals(analysis, signal, check_period_hours, recent_signals):
    prefix = ExtractSignal.extract_prefix(signal)
    window = ExtractSignal.extract_window(prefix, signal)
    action = ExtractSignal.extract_action(prefix, signal)

    if action == 'cross_up':
        analysis.identify_ma_cross_up(window)
    if action == 'cross_down':
        analysis.identify_ma_cross_down(window)
    if action == 'above':
        analysis.identify_ma_above(window)
    if action == 'below':
        analysis.identify_ma_below(window)

    column_name = f'ma_{action}_{window}'
    time_check_period_ago = analysis.data['time'].iloc[-1] - timedelta(hours=check_period_hours)
    condition = (analysis.data[column_name]) & (analysis.data['time'] >= time_check_period_ago)
    if not recent_signals.empty:
        recent_signals = recent_signals.reset_index(drop=True)
    recent_signals = analysis.data[condition] if recent_signals.empty else recent_signals[recent_signals.index.isin(analysis.data[condition].index)]
    
    return recent_signals

def process_macd_signals(analysis, signal, check_period_hours, recent_signals):
    analysis.calculate_macd()
    prefix = ExtractSignal.extract_prefix(signal)
    action = ExtractSignal.extract_action(prefix, signal)

    if action == 'cross_up_signal':
        analysis.identify_macd_cross_up()
    if action == 'cross_down_signal':
        analysis.identify_macd_cross_down()

    column_name = f'macd_{action}'
    time_check_period_ago = analysis.data['time'].iloc[-1] - timedelta(hours=check_period_hours)
    condition = (analysis.data[column_name]) & (analysis.data['time'] >= time_check_period_ago)
    if not recent_signals.empty:
        recent_signals = recent_signals.reset_index(drop=True)
    recent_signals = analysis.data[condition] if recent_signals.empty else recent_signals[recent_signals.index.isin(analysis.data[condition].index)]
    
    return recent_signals

def process_bb_signals(analysis, signal, check_period_hours, recent_signals):
    analysis.calculate_bollinger_bands()
    prefix = ExtractSignal.extract_prefix(signal)
    action = ExtractSignal.extract_action(prefix, signal)

    if action == 'touch_upper':
        analysis.identify_bollinger_touch_upper()
    if action == 'touch_lower':
        analysis.identify_bollinger_touch_lower()
    if action == 'breakout_upper':
        analysis.identify_bollinger_breakout_upper()
    if action == 'breakout_lower':
        analysis.identify_bollinger_breakout_lower()

    column_name = f'bb_{action}'
    time_check_period_ago = analysis.data['time'].iloc[-1] - timedelta(hours=check_period_hours)
    condition = (analysis.data[column_name]) & (analysis.data['time'] >= time_check_period_ago)
    if not recent_signals.empty:
        recent_signals = recent_signals.reset_index(drop=True)
    recent_signals = analysis.data[condition] if recent_signals.empty else recent_signals[recent_signals.index.isin(analysis.data[condition].index)]
    
    return recent_signals

def process_rsi_signals(analysis, signal, check_period_hours, recent_signals):
    analysis.calculate_rsi()
    prefix = ExtractSignal.extract_prefix(signal)
    action = ExtractSignal.extract_action(prefix, signal)

    if action == 'gt_overbought':
        analysis.identify_rsi_gt_overbought()
    if action == 'lt_overbought':
        analysis.identify_rsi_lt_overbought()
    if action == 'lt_oversold':
        analysis.identify_rsi_lt_oversold()
    if action == 'gt_oversold':
        analysis.identify_rsi_gt_oversold()

    column_name = f'rsi_{action}'
    time_check_period_ago = analysis.data['time'].iloc[-1] - timedelta(hours=check_period_hours)
    condition = (analysis.data[column_name]) & (analysis.data['time'] >= time_check_period_ago)
    if not recent_signals.empty:
        recent_signals = recent_signals.reset_index(drop=True)
    recent_signals = analysis.data[condition] if recent_signals.empty else recent_signals[recent_signals.index.isin(analysis.data[condition].index)]
    
    return recent_signals

def process_price_signals(analysis, signal, check_period_hours, recent_signals):
    prefix = ExtractSignal.extract_prefix(signal)
    window = ExtractSignal.extract_window(prefix, signal)
    action = ExtractSignal.extract_action(prefix, signal)

    if action == 'high_breakout':
        analysis.identify_high_breakout(window)
    if action == 'low_breakout':
        analysis.identify_low_breakout(window)

    column_name = f'price_{action}_{window}'
    time_check_period_ago = analysis.data['time'].iloc[-1] - timedelta(hours=check_period_hours)
    condition = (analysis.data[column_name]) & (analysis.data['time'] >= time_check_period_ago)
    if not recent_signals.empty:
        recent_signals = recent_signals.reset_index(drop=True)
    recent_signals = analysis.data[condition] if recent_signals.empty else recent_signals[recent_signals.index.isin(analysis.data[condition].index)]
    
    return recent_signals

def process_stock_data(stock, symbols, symbols_group_industry, check_period_hours, min_data_length, signals):
    result = []
    rsi_signals = ['rsi_gt_overbought', 'rsi_lt_overbought', 'rsi_gt_oversold', 'rsi_lt_oversold']
    macd_signals = ['macd_cross_up_signal', 'macd_cross_down_signal']
    bb_signals = ['bb_touch_upper', 'bb_touch_lower', 'bb_breakout_upper', 'bb_breakout_lower']
    ma_signals = [
        'ma_cross_up_10', 'ma_cross_down_10', 'ma_above_10', 'ma_below_10',
        'ma_cross_up_20', 'ma_cross_down_20', 'ma_above_20', 'ma_below_20',
        'ma_cross_up_50', 'ma_cross_down_50', 'ma_above_50', 'ma_below_50',
        'ma_cross_up_100', 'ma_cross_down_100', 'ma_above_100', 'ma_below_100',
        'ma_cross_up_200', 'ma_cross_down_200', 'ma_above_200', 'ma_below_200',
    ]
    price_signals = [
        'price_high_breakout_5', 'price_low_breakout_5',
        'price_high_breakout_21', 'price_low_breakout_21',
        'price_high_breakout_63', 'price_low_breakout_63',
        'price_high_breakout_126', 'price_low_breakout_126',
    ]

    end_date = datetime.now()
    start_date = end_date - timedelta(days=min_data_length)

    for symbol in symbols:
        try:
            data = stock.quote.history(symbol=symbol, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), interval="1D")
            if len(data) < min_data_length:
                print(f"Not enough data for {symbol}. Skipping.")
                continue

            analysis = StockAnalysis(data)
            recent_signals = pd.DataFrame()

            for signal in signals:
                if signal in ma_signals:
                    recent_signals = process_ma_signals(analysis, signal, check_period_hours, recent_signals)
                if signal in macd_signals:
                    recent_signals = process_macd_signals(analysis, signal, check_period_hours, recent_signals)
                if signal in bb_signals:
                    recent_signals = process_bb_signals(analysis, signal, check_period_hours, recent_signals)
                if signal in rsi_signals:
                    recent_signals = process_rsi_signals(analysis, signal, check_period_hours, recent_signals)
                if signal in price_signals:
                    recent_signals = process_price_signals(analysis, signal, check_period_hours, recent_signals)

            stock_info = StockInfo(stock)
            company_name = stock_info.get_company_name(symbols_group_industry, symbol)
            industry_name = stock_info.get_industry_name(symbols_group_industry, symbol)

            if not recent_signals.empty:
                last_signal = recent_signals.iloc[-1]
                result.append({
                    "symbol": symbol,
                    "company_name": company_name,
                    "industry_name": industry_name,
                    "date": last_signal['time'].strftime('%Y-%m-%d %H:%M:%S'),
                    "close_price": last_signal['close'],
                    "volume": int(last_signal['volume']),
                })

        except Exception as e:
            print(f"Error processing {symbol}: {e}")

    return result

# Route để hiển thị trang chính
@app.route('/')
def index():
    return render_template('index.html')

# Route để lấy dữ liệu ngành
@app.route('/industries', methods=['GET'])
def get_industries():
    industries = [
        'Bia và đồ uống', 'Bán lẻ', 'Bảo hiểm nhân thọ', 'Bảo hiểm phi nhân thọ',
        'Bất động sản', 'Công nghiệp nặng', 'Du lịch & Giải trí', 'Dược phẩm',
        'Dịch vụ tài chính', 'Hàng cá nhân', 'Hàng công nghiệp', 'Hàng gia dụng',
        'Hàng hóa giải trí', 'Hóa chất', 'Khai khoáng', 'Kim loại',
        'Lâm nghiệp và Giấy', 'Ngân hàng', 'Nước & Khí đốt',
        'Phân phối thực phẩm & dược phẩm', 'Phần mềm & Dịch vụ Máy tính',
        'Sản xuất & Phân phối Điện', 'Sản xuất Dầu khí', 'Sản xuất thực phẩm',
        'Thiết bị và Dịch vụ Y tế', 'Thiết bị và Phần cứng',
        'Thiết bị, Dịch vụ và Phân phối Dầu khí', 'Thuốc lá', 'Truyền thông',
        'Tư vấn & Hỗ trợ Kinh doanh', 'Viễn thông cố định',
        'Viễn thông di động', 'Vận tải', 'Xây dựng và Vật liệu',
        'Ô tô và phụ tùng', 'Điện tử & Thiết bị điện'
    ]
    return jsonify(industries)

# Route để lấy dữ liệu sàn
@app.route('/groups', methods=['GET'])
def get_groups():
    groups = ['HOSE', 'HNX', 'HNX30', 'VN100', 'VN30', 'VNMidCap', 'VNSmallCap', 'UPCOM']
    return jsonify(groups)

# Route để lấy dữ liệu loại tín hiệu
@app.route('/signal_categories', methods=['GET'])
def get_signal_categories():
    categories = ['Bollinger Band (20, 2)', 'Moving Average (MA)', 'MACD (9, 12, 26)', 'RSI (14)', 'Giá']
    return jsonify(categories)

# Route để lấy tên các tín hiệu dựa trên loại tín hiệu đã chọn
@app.route('/signals/<category>', methods=['GET'])
def get_signals(category):
    signals = signals_map.get(category, {})
    return jsonify(signals)

# Route để lọc cổ phiếu dựa trên các tín hiệu đã chọn
@app.route('/stocks', methods=['GET'])
def stocks():
    group = request.args.get('group', 'VN30')
    industry = request.args.get('industry')
    signals = request.args.getlist('signal')

    stock = Vnstock().stock(source='TCBS')
    stock_info = StockInfo(stock)

    symbols_group = stock_info.get_symbols_by_group(group)
    symbols_group_industry = stock_info.get_symbols_by_industry(industry)
    symbols_industry = symbols_group_industry[symbols_group_industry['icb_name3'] == industry] if industry else symbols_group_industry
    symbols = stock_info.get_filtered_symbols(symbols_group, symbols_industry)

    check_period_hours = 24
    min_data_length = 200
    results = process_stock_data(stock, symbols, symbols_group_industry, check_period_hours, min_data_length, signals)

    return jsonify({
        "results": results,
        "total": len(results)
    })

if __name__ == '__main__':
    app.run(debug=True)
