import yfinance as yf
import requests
import os
from datetime import datetime
import pytz

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
    try:
        data = {"title": title, "desp": content}
        requests.post(server_url, data=data, timeout=10)
    except Exception as e:
        print(f"推送失败：{e}")

def is_us_stock_trading_time() -> bool:
    """自动判断当前是否美股交易时段，自动处理夏令/冬令时"""
    ny_tz = pytz.timezone("America/New_York")
    now_ny = datetime.now(tz=ny_tz)
    # 美股交易日：周一~周五
    if now_ny.weekday() >= 5:
        return False
    # 美股开盘：9:30 ~ 16:00 纽约本地时间
    start = now_ny.replace(hour=9, minute=30, second=0, microsecond=0)
    end = now_ny.replace(hour=16, minute=0, second=0, microsecond=0)
    return start <= now_ny <= end

# 主逻辑
if __name__ == "__main__":
    if not is_us_stock_trading_time():
        print("当前非美股交易时间，直接退出，不请求行情")
    else:
        alert_msg_list = []
        for item in watch_list:
            ticker, price_high, price_low = item
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                current_price = info.get("regularMarketPrice")
                if not current_price:
                    print(f"{ticker} 获取价格失败，无行情数据")
                    continue
                print(f"{ticker} 当前价格：{current_price}")

                if current_price >= price_high:
                    msg = f"📈 {ticker} 现价 {current_price}，上涨触发价：{price_high}"
                    alert_msg_list.append(msg)
                if current_price <= price_low:
                    msg = f"📉 {ticker} 现价 {current_price}，下跌触发价：{price_low}"
                    alert_msg_list.append(msg)
            except Exception as e:
                print(f"{ticker} 执行异常: {str(e)}")

        if alert_msg_list:
            full_content = "\n".join(alert_msg_list)
            send_wechat("美股价格告警汇总", full_content)
        else:
            print("本轮无触发涨跌告警，不推送消息")
