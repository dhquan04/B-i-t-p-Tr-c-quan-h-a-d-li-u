#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Select, Slider, CheckboxGroup
from bokeh.layouts import row, column
from bokeh.plotting import figure

# Đọc dữ liệu từ file CSV
data = pd.read_csv('all_stocks_5yr.csv')

data['date'] = pd.to_datetime(data['date'])

data['open'] = data['open']
data['close'] = data['close']
data['high'] = data['high']
data['low'] = data['low']
data['volume'] = data['volume']

# Tạo ColumnDataSource
source = ColumnDataSource(data={})
source_rsi = ColumnDataSource(data={})
source_volume = ColumnDataSource(data={})

# Tạo menu chọn mã chứng khoán
stock_select = Select(title="Chọn mã chứng khoán:", value="MMM", options=data['Name'].unique().tolist())

# Tạo slider cho năm
year_slider = Slider(start=2012, end=2017, value=2017, step=1, title="Năm")

# Tạo slider cho Simple Moving Average (SMA)
sma_slider = Slider(start=10, end=100, value=20, step=10, title="Số ngày SMA")

# Tạo slider cho RSI
rsi_slider = Slider(start=5, end=50, value=14, step=1, title="Số ngày RSI")

# Tạo checkbox cho các trường dữ liệu
checkbox_group = CheckboxGroup(labels=["Open", "Close", "High", "Low"], active=[0, 1, 2, 3])

# Tạo figure chính
p = figure(title="Biểu đồ Chứng khoán", x_axis_label='Ngày', y_axis_label='Giá', x_axis_type='datetime')

# Tạo figure cho RSI
p_rsi = figure(title="Chỉ số RSI", x_axis_label='Ngày', y_axis_label='RSI', x_axis_type='datetime', height=200)
p_rsi.line(x='date', y='rsi', source=source_rsi, legend_label='RSI', line_width=2, color='purple')
p_rsi.line(x='date', y=30, source=source_rsi, legend_label='RSI 30', line_width=1, color='red', line_dash='dashed')
p_rsi.line(x='date', y=70, source=source_rsi, legend_label='RSI 70', line_width=1, color='green', line_dash='dashed')

# Tạo figure cho Volume
p_volume = figure(title="Khối lượng giao dịch", x_axis_label='Ngày', y_axis_label='Volume', x_axis_type='datetime', height=200)
p_volume.vbar(x='date', top='volume', source=source_volume, width=0.5, color='blue')

# Màu cho các trường dữ liệu
colors = {
    "Open": "yellow",
    "Close": "orange",
    "High": "green",
    "Low": "red",
}

# Hàm tính Simple Moving Average (SMA)
def simple_moving_average(values, window):
    """
    Tính Simple Moving Average (SMA) cho một chuỗi giá trị.
    
    Args:
        values (pd.Series): Chuỗi giá trị đầu vào (ví dụ: giá đóng cửa).
        window (int): Số ngày để tính SMA.
    
    Returns:
        pd.Series: Chuỗi SMA.
    """
    return values.rolling(window=window, min_periods=1).mean()

# Hàm tính RSI
def compute_rsi(data, window):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Hàm cập nhật biểu đồ
def update():
    selected_stock = stock_select.value
    selected_year = year_slider.value
    sma_days = sma_slider.value
    rsi_days = rsi_slider.value
    
    filtered_data = data[(data['Name'] == selected_stock) & (data['date'].dt.year == selected_year)].copy()
    filtered_data['sma'] = simple_moving_average(filtered_data['close'], sma_days)
    filtered_data['rsi'] = compute_rsi(filtered_data['close'], rsi_days)
    
    # Cập nhật ColumnDataSource
    source.data = {
        'date': filtered_data['date'],
        'open': filtered_data['open'],
        'close': filtered_data['close'],
        'high': filtered_data['high'],
        'low': filtered_data['low'],
        'sma': filtered_data['sma'],
    }
    
    source_rsi.data = {
        'date': filtered_data['date'],
        'rsi': filtered_data['rsi'],
    }
    
    source_volume.data = {
        'date': filtered_data['date'],
        'volume': filtered_data['volume'],
    }
    
    p.renderers = []  # Xóa các renderer cũ
    selected_fields = [checkbox_group.labels[i] for i in checkbox_group.active]
    
    for field in selected_fields:
        p.line(x='date', y=field.lower(), source=source, legend_label=field, line_width=2, color=colors[field])
    
    # Thêm đường SMA
    p.line(x='date', y='sma', source=source, line_width=2, color='black', line_dash='dashed')

# Gắn callback cho các widget
checkbox_group.on_change('active', lambda attr, old, new: update())
stock_select.on_change('value', lambda attr, old, new: update())
year_slider.on_change('value', lambda attr, old, new: update())
sma_slider.on_change('value', lambda attr, old, new: update())
rsi_slider.on_change('value', lambda attr, old, new: update())

# Sắp xếp layout
controls = column(stock_select, year_slider, sma_slider, rsi_slider, checkbox_group)
plots = column(p, p_volume, p_rsi)
layout = row(controls, plots)

# Thêm layout vào curdoc
curdoc().add_root(layout)

# Gọi hàm update ban đầu
update()


# In[ ]:




