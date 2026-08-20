import yfinance as yf
import requests
import os

# ============在这里修改你的监控配置！！============
watch_list = [
    #格式：["股票代码", 上涨触发价, 下跌触发价]
    ["NVDA", 217, 95],
    ["AAPL", 220, 180]
]
# ==============================================

SENDKEY = os.environ.get("SERVERCHAN_SENDKEY")
server_url = f"https://sctapi.ftqq.com/{SENDKEY}.send"

def send_wechat(title, content):
    data = {"title":title, "desp":content}
    requests.post(server_url, data=data)

for item in watch_list:
    ticker, price_high, price_low = item
    stock = yf.Ticker(ticker)
    info = stock.info
    current_price = info.get("regularMarketPrice")
    if not current_price:
        print(f"{ticker} 获取价格失败")
        continue
    print(f"{ticker} 当前价格：{current_price}")
    #上涨告警
    if current_price >= price_high:
        msg = f"📈 {ticker} 已经涨到 {current_price} 美元！\n触发目标价：{price_high}"
        send_wechat("美股上涨提醒",msg)
    #下跌告警
    if current_price <= price_low:
        msg = f"📉 {ticker} 已经跌到 {current_price} 美元！\n触发目标价：{price_low}"
        send_wechat("美股下跌提醒",msg)
