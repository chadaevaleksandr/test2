import websocket, orjson, time, threading, math

priceLog = []

def on_message(ws, message):
    data = orjson.loads(message)
    btcPrice = False
    ethPrice = False
    # выбираю цены по btc и eth
    for i in range(len(data)):
        if data[i]['s'] == 'BTCUSDT':
            btcPrice = float(data[i]['p'])
            curTime = data[i]['E']
        if data[i]['s'] == 'ETHUSDT':
            ethPrice = float(data[i]['p'])
    if btcPrice and ethPrice:
        if len(priceLog) > 0 and curTime - priceLog[0]['time'] > 3600000:
            # выбираю цену, которая была час назад и удаляю лишние данные из priceLog
            while curTime - priceLog[0]['time'] > 3600000:
                btcPricePast = priceLog[0]['btc']
                ethPricePast = priceLog[0]['eth']
                priceLog.pop(0)
            # логика расчётов
            btcPriceDelta = (btcPrice - btcPricePast)/btcPricePast
            ethPriceDelta = (ethPrice - ethPricePast)/ethPricePast
            ethPriceDelta_real = ethPriceDelta - (btcPriceDelta * 1.192)

            if math.fabs(ethPriceDelta_real) > 0.01:
                #if time.time() - curTime * 1000 < 1500:        #тут можно проверять временные задержки (данные с биржи не старее 1.5 секунд)
                print('Цена ETH изменилась на 1%')
        # добавляю новые данные в priceLog
        priceLog.append(
            {
                'btc': btcPrice,
                'eth': ethPrice,
                'time': curTime
            }
        )


def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    print("Opened connection")

# сенеджер потоков обеспечивает переподключение к вебсокетам в случае возникновения любых ошибок
def ws_manager():
    while True:
        try:
            ws = websocket.WebSocketApp(
                "wss://fstream.binance.com/ws/!markPrice@arr@1s",
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            ws.run_forever()
        except Exception as ex:
            print(ex)
            time.sleep(1)

ws_manager_thread = threading.Thread(target=ws_manager, daemon=True)
ws_manager_thread.start()
ws_manager_thread.join()