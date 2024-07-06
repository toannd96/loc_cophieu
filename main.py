import pandas as pd
import pandas_ta as ta
import json
import re
from flask import Flask, request, jsonify, render_template
from vnstock3 import Vnstock
from datetime import datetime, timedelta

app = Flask(__name__)

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
        self.data['macd_cross_up'] = (self.data['macd'] > self.data['signal_line']) & (self.data['macd'].shift(1) <= self.data['signal_line'].shift(1))
        return self

    # MACD cắt xuống đường tín hiệu
    def identify_macd_cross_down(self):
        self.data['macd_cross_down'] = (self.data['macd'] < self.data['signal_line']) & (self.data['macd'].shift(1) >= self.data['signal_line'].shift(1))
        return self

    # Tính toán chỉ báo Bollinger Band
    def calculate_bollinger_bands(self, window=20, std_dev=2):
        bollinger = ta.bbands(self.data['close'], length=window, std=std_dev)
        self.data = pd.concat([self.data, bollinger], axis=1)
        return self

    # Giá chạm dải biên trên dải Bollinger Band
    def identify_bollinger_upper(self):
        self.data['bb_upper'] = self.data['close'] >= self.data['BBU_20_2.0']
        return self

    # Giá chạm dải biên dưới dải Bollinger Band
    def identify_bollinger_lower(self):
        self.data['bb_lower'] = self.data['close'] <= self.data['BBL_20_2.0']
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
        self.data[f'ma{window}_cross_up'] = (self.data['close'] > ma) & (self.data['close'].shift(1) <= ma.shift(1))
        return self

    # Giá cắt xuống đường MA_N
    def identify_ma_cross_down(self, window):
        ma = self.calculate_ma(window)
        self.data[f'ma{window}_cross_down'] = (self.data['close'] < ma) & (self.data['close'].shift(1) >= ma.shift(1))
        return self

    # Giá nằm trên đường MA_N
    def identify_ma_above(self, window):
        ma = self.calculate_ma(window)
        self.data[f'ma{window}_above'] = self.data['close'] > ma
        return self
    
    # Giá nằm dưới đường MA_N
    def identify_ma_below(self, window):
        ma = self.calculate_ma(window)
        self.data[f'ma{window}_below'] = self.data['close'] < ma
        return self

    # Tính toán chỉ báo RSI
    def calculate_rsi(self, window=14):
        rsi = ta.rsi(self.data['close'], length=window)
        self.data = pd.concat([self.data, rsi.rename('rsi')], axis=1)
        return self

    # RSI >= 70
    def identify_rsi_overbought(self):
        self.data['rsi_overbought'] = self.data['rsi'] >= 70
        return self

    # RSI <= 30
    def identify_rsi_oversold(self):
        self.data['rsi_oversold'] = self.data['rsi'] <= 30
        return self

    # Giá vượt đỉnh theo khoảng thời gian (window)
    def identify_high_breakout(self, window):
        self.data[f'price{window}_high'] = self.data['high'].rolling(window=window).max()
        self.data[f'price{window}_high_breakout'] = self.data['close'] > self.data[f'price{window}_high'].shift(1)
        return self

    # Giá thủng đáy theo khoảng thời gian (window)
    def identify_low_breakout(self, window):
        self.data[f'price{window}_low'] = self.data['low'].rolling(window=window).min()
        self.data[f'price{window}_low_breakout'] = self.data['close'] < self.data[f'price{window}_low'].shift(1)
        return self

# Lấy thông tin về mã chứng khoán
class StockInfo:
    def __init__(self, stock):
        self.stock = stock

    # Danh sách mã chứng khoán theo nhóm
    def get_symbols_by_group(self, group='VN30'):
        return self.stock.listing.symbols_by_group(group)

    # Danh sách mã chứng khoán theo ngành
    def get_symbols_by_sector(self, sector_name=None):
        industry_symbols = self.stock.listing.symbols_by_industries()
        if sector_name:
            return industry_symbols[industry_symbols['icb_name3'] == sector_name]
        else:
            return industry_symbols

    # Danh sách thuộc nhóm và ngành
    def get_filtered_symbols(self, symbols_group, symbols_sector):
        sector_symbols_list = symbols_sector['symbol'].tolist()
        return list(set(symbols_group) & set(sector_symbols_list))

    def get_company_name(self, industry_symbols, symbol):
        return industry_symbols[industry_symbols['symbol'] == symbol]['organ_name'].values[0]

    def get_industry_name(self, industry_symbols, symbol):
        return industry_symbols[industry_symbols['symbol'] == symbol]['icb_name3'].values[0]

class ExtractSignal:
    @staticmethod
    def extract_window(prefix, signal):
        match = re.search(fr'{prefix}(\d+)', signal)
        if match:
            return int(match.group(1))
        return None

    @staticmethod
    def extract_action(prefix, signal):
        match = re.search(fr'{prefix}(?:\d+)?_(\w+)', signal)
        if match:
            return match.group(1)
        return None

def process_ma_signals(analysis, signal, check_period_hours, recent_signals):
    window = ExtractSignal.extract_window('ma', signal)
    action = ExtractSignal.extract_action('ma', signal)

    if action == 'cross_up':
        analysis.identify_ma_cross_up(window)
    if action == 'cross_down':
        analysis.identify_ma_cross_down(window)
    if action == 'above':
        analysis.identify_ma_above(window)
    if action == 'below':
        analysis.identify_ma_below(window)

    column_name = f'ma{window}_{action}'
    time_check_period_ago = analysis.data['time'].iloc[-1] - timedelta(hours=check_period_hours)
    recent_signals = pd.concat([recent_signals, analysis.data[(analysis.data[column_name]) & (analysis.data['time'] >= time_check_period_ago)]], ignore_index=True)
    return recent_signals

def process_macd_signals(analysis, signal, check_period_hours, recent_signals):
    analysis.calculate_macd()
    action = ExtractSignal.extract_action('macd', signal)

    if action == 'cross_up':
        analysis.identify_macd_cross_up()
    if action == 'cross_down':
        analysis.identify_macd_cross_down()

    column_name = f'macd_{action}'
    time_check_period_ago = analysis.data['time'].iloc[-1] - timedelta(hours=check_period_hours)
    recent_signals = pd.concat([recent_signals, analysis.data[(analysis.data[column_name]) & (analysis.data['time'] >= time_check_period_ago)]], ignore_index=True)
    
    return recent_signals

def process_bb_signals(analysis, signal, check_period_hours, recent_signals):
    analysis.calculate_bollinger_bands()
    action = ExtractSignal.extract_action('bb', signal)

    if action == 'upper':
        analysis.identify_bollinger_upper()
    if action == 'lower':
        analysis.identify_bollinger_lower()
    if action == 'breakout_upper':
        analysis.identify_bollinger_breakout_upper()
    if action == 'breakout_lower':
        analysis.identify_bollinger_breakout_lower()

    column_name = f'bb_{action}'
    time_check_period_ago = analysis.data['time'].iloc[-1] - timedelta(hours=check_period_hours)
    recent_signals = pd.concat([recent_signals, analysis.data[(analysis.data[column_name]) & (analysis.data['time'] >= time_check_period_ago)]], ignore_index=True)
    return recent_signals

def process_rsi_signals(analysis, signal, check_period_hours, recent_signals):
    analysis.calculate_rsi()
    action = ExtractSignal.extract_action('rsi', signal)

    if action == 'overbought':
        analysis.identify_rsi_overbought()
    if action == 'oversold':
        analysis.identify_rsi_oversold()

    column_name = f'rsi_{action}'
    time_check_period_ago = analysis.data['time'].iloc[-1] - timedelta(hours=check_period_hours)
    recent_signals = pd.concat([recent_signals, analysis.data[(analysis.data[column_name]) & (analysis.data['time'] >= time_check_period_ago)]], ignore_index=True)
    return recent_signals

def process_price_signals(analysis, signal, check_period_hours, recent_signals):
    window = ExtractSignal.extract_window('price', signal)
    action = ExtractSignal.extract_action('price', signal)

    if action == 'high_breakout':
        analysis.identify_high_breakout(window)
    if action == 'low_breakout':
        analysis.identify_low_breakout(window)

    column_name = f'price{window}_{action}'
    time_check_period_ago = analysis.data['time'].iloc[-1] - timedelta(hours=check_period_hours)
    recent_signals = pd.concat([recent_signals, analysis.data[(analysis.data[column_name]) & (analysis.data['time'] >= time_check_period_ago)]], ignore_index=True)
    return recent_signals

def process_stock_data(stock, symbols, industry_symbols, check_period_hours, min_data_length, signals):
    result = []
    rsi_signals = ['rsi_overbought', 'rsi_oversold']
    macd_signals = ['macd_cross_up', 'macd_cross_down']
    bb_signals = ['bb_upper', 'bb_lower', 'bb_breakout_upper', 'bb_breakout_lower']
    ma_signals = [
        'ma5_cross_up', 'ma5_cross_down', 'ma5_above', 'ma5_below',
        'ma10_cross_up', 'ma10_cross_down', 'ma10_above', 'ma10_below',
        'ma20_cross_up', 'ma20_cross_down', 'ma20_above', 'ma20_below',
        'ma50_cross_up', 'ma50_cross_down', 'ma50_above', 'ma50_below',
        'ma100_cross_up', 'ma100_cross_down', 'ma100_above', 'ma100_below',
        'ma200_cross_up', 'ma200_cross_down', 'ma200_above', 'ma200_below',
    ]
    price_signals = [
        'price5_high_breakout', 'price5_low_breakout',
        'price21_high_breakout', 'price21_low_breakout',
        'price63_high_breakout', 'price63_low_breakout',
        'price126_high_breakout', 'price126_low_breakout',
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
            company_name = stock_info.get_company_name(industry_symbols, symbol)
            industry_name = stock_info.get_industry_name(industry_symbols, symbol)

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

def paginate_results(results, page, limit):
    total = len(results)
    if total == 0:
        return [], {
            "page": page,
            "limit": limit,
            "from": 0,
            "to": 0,
            "total": 0,
            "total_page": 0
        }

    total_page = (total + limit - 1) // limit

    if page > total_page:
        page = total_page
    elif page < 1:
        page = 1

    from_ = (page - 1) * limit
    to = from_ + limit

    paginated_results = results[from_:to]

    paging_info = {
        "page": page,
        "limit": limit,
        "from": from_ + 1,
        "to": to if to < total else total,
        "total": total,
        "total_page": total_page
    }

    return paginated_results, paging_info

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stocks', methods=['GET'])
def stocks():
    group = request.args.get('group', 'VN30')
    sector_name = request.args.get('sector_name')
    signals = request.args.getlist('signal')

    stock = Vnstock().stock(source='TCBS')
    stock_info = StockInfo(stock)

    symbols_group = stock_info.get_symbols_by_group(group)
    industry_symbols = stock_info.get_symbols_by_sector(sector_name)
    symbols_sector = industry_symbols[industry_symbols['icb_name3'] == sector_name] if sector_name else industry_symbols
    symbols = stock_info.get_filtered_symbols(symbols_group, symbols_sector)

    check_period_hours = 24
    min_data_length = 200
    all_results = process_stock_data(stock, symbols, industry_symbols, check_period_hours, min_data_length, signals)

    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 100))
    paginated_results, paging_info = paginate_results(all_results, page, limit)

    return jsonify({
        "results": paginated_results,
        "paging": paging_info
    })

if __name__ == '__main__':
    app.run(debug=True)

# {'Bia và đồ uống',
#  'Bán lẻ',
#  'Bảo hiểm nhân thọ',
#  'Bảo hiểm phi nhân thọ',
#  'Bất động sản',
#  'Công nghiệp nặng',
#  'Du lịch & Giải trí',
#  'Dược phẩm',
#  'Dịch vụ tài chính',
#  'Hàng cá nhân',
#  'Hàng công nghiệp',
#  'Hàng gia dụng',
#  'Hàng hóa giải trí',
#  'Hóa chất',
#  'Khai khoáng',
#  'Kim loại',
#  'Lâm nghiệp và Giấy',
#  'Ngân hàng',
#  'Nước & Khí đốt',
#  'Phân phối thực phẩm & dược phẩm',
#  'Phần mềm & Dịch vụ Máy tính',
#  'Sản xuất & Phân phối Điện',
#  'Sản xuất Dầu khí',
#  'Sản xuất thực phẩm',
#  'Thiết bị và Dịch vụ Y tế',
#  'Thiết bị và Phần cứng',
#  'Thiết bị, Dịch vụ và Phân phối Dầu khí',
#  'Thuốc lá',
#  'Truyền thông',
#  'Tư vấn & Hỗ trợ Kinh doanh',
#  'Viễn thông cố định',
#  'Viễn thông di động',
#  'Vận tải',
#  'Xây dựng và Vật liệu',
#  'Ô tô và phụ tùng',
#  'Điện tử & Thiết bị điện'
#  }

# HOSE, VN30, VNMidCap, VNSmallCap, VNAllShare, VN100, ETF, HNX, HNX30, HNXCon, HNXFin, HNXLCap, HNXMSCap, HNXMan, UPCOM, FU_INDEX
