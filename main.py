from dash import html
import dash
import pandas as pd
import numpy as np
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


# def ema(data, window):
#     ema = data.ewm(span=window, adjust=False).mean()
#     return ema


# def rsi_tradingview(ohlc: pd.DataFrame, period: int = 14, round_rsi: bool = True):
#     delta = ohlc["close"].diff()

#     up = delta.copy()
#     up[up < 0] = 0
#     up = pd.Series.ewm(up, alpha=1/period).mean()

#     down = delta.copy()
#     down[down > 0] = 0
#     down *= -1
#     down = pd.Series.ewm(down, alpha=1/period).mean()

#     rsi = np.where(up == 0, 0, np.where(
#         down == 0, 100, 100 - (100 / (1 + up / down))))

#     return np.round(rsi, 2) if round_rsi else rsi


# def fetch_data(symbol):
#     # print(f"Processing {symbol}")
#     params = {"symbol": symbol, "interval": interval, "limit": limit}
#     response = requests.get(endpoint, params=params)
#     data = response.json()

#     symbol_df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume", "close_time",
#                              "quote_asset_volume", "number_of_trades", "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"])

#     symbol_df["timestamp"] = pd.to_datetime(symbol_df["timestamp"], unit="ms")
#     symbol_df = symbol_df.set_index("timestamp")

#     symbol_df = symbol_df.astype(float)

#     symbol_df["EMA4"] = symbol_df["close"].ewm(span=4).mean()
#     symbol_df["MA8"] = symbol_df["close"].rolling(8).mean()
#     symbol_df["MA20"] = symbol_df["close"].rolling(20).mean()
#     symbol_df["MA50"] = symbol_df["close"].rolling(50).mean()

#     symbol_df["RSI14"] = rsi_tradingview(symbol_df)

#     symbol_df = symbol_df.tail(2)
#     # symbol_df = symbol_df.tail(5).iloc[:-3]

#     symbol_df.index = pd.MultiIndex.from_product(
#         [[symbol], symbol_df.index], names=["symbol", "timestamp"])

#     return symbol_df


# exchange_info_endpoint = "https://api.binance.com/api/v3/exchangeInfo"
# endpoint = "https://api.binance.com/api/v3/klines"


# symbol_list = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "BCCUSDT", "NEOUSDT", "LTCUSDT", "QTUMUSDT", "ADAUSDT", "XRPUSDT", "EOSUSDT", "TUSDUSDT", "IOTAUSDT", "XLMUSDT", "ONTUSDT", "TRXUSDT", "ETCUSDT", "ICXUSDT", "VENUSDT", "NULSUSDT", "VETUSDT", "PAXUSDT", "BCHABCUSDT", "BCHSVUSDT", "USDCUSDT", "LINKUSDT", "WAVESUSDT", "BTTUSDT", "USDSUSDT", "ONGUSDT", "HOTUSDT", "ZILUSDT", "ZRXUSDT", "FETUSDT", "BATUSDT", "XMRUSDT", "ZECUSDT", "IOSTUSDT", "CELRUSDT", "DASHUSDT", "NANOUSDT", "OMGUSDT", "THETAUSDT", "ENJUSDT", "MITHUSDT", "MATICUSDT", "ATOMUSDT", "TFUELUSDT", "ONEUSDT", "FTMUSDT", "ALGOUSDT", "USDSBUSDT", "GTOUSDT", "ERDUSDT", "DOGEUSDT", "DUSKUSDT", "ANKRUSDT", "WINUSDT", "COSUSDT", "NPXSUSDT", "COCOSUSDT", "MTLUSDT", "TOMOUSDT", "PERLUSDT", "DENTUSDT", "MFTUSDT", "KEYUSDT", "STORMUSDT", "DOCKUSDT", "WANUSDT", "FUNUSDT", "CVCUSDT", "CHZUSDT", "BANDUSDT", "BUSDUSDT", "BEAMUSDT", "XTZUSDT", "RENUSDT", "RVNUSDT", "HCUSDT", "HBARUSDT", "NKNUSDT", "STXUSDT", "KAVAUSDT", "ARPAUSDT", "IOTXUSDT", "RLCUSDT", "MCOUSDT", "CTXCUSDT", "BCHUSDT", "TROYUSDT", "VITEUSDT", "FTTUSDT", "EURUSDT", "OGNUSDT", "DREPUSDT", "BULLUSDT", "BEARUSDT", "ETHBULLUSDT", "ETHBEARUSDT", "TCTUSDT", "WRXUSDT", "BTSUSDT", "LSKUSDT", "BNTUSDT", "LTOUSDT", "EOSBULLUSDT", "EOSBEARUSDT", "XRPBULLUSDT", "XRPBEARUSDT", "STRATUSDT", "AIONUSDT", "MBLUSDT", "COTIUSDT", "BNBBULLUSDT", "BNBBEARUSDT", "STPTUSDT", "WTCUSDT", "DATAUSDT", "XZCUSDT", "SOLUSDT", "CTSIUSDT", "HIVEUSDT", "CHRUSDT", "BTCUPUSDT", "BTCDOWNUSDT", "GXSUSDT", "ARDRUSDT", "LENDUSDT", "MDTUSDT", "STMXUSDT", "KNCUSDT", "REPUSDT", "LRCUSDT", "PNTUSDT", "COMPUSDT", "BKRWUSDT", "SCUSDT", "ZENUSDT", "SNXUSDT", "ETHUPUSDT", "ETHDOWNUSDT", "ADAUPUSDT", "ADADOWNUSDT", "LINKUPUSDT", "LINKDOWNUSDT", "VTHOUSDT", "DGBUSDT", "GBPUSDT", "SXPUSDT", "MKRUSDT", "DAIUSDT", "DCRUSDT", "STORJUSDT", "BNBUPUSDT", "BNBDOWNUSDT", "XTZUPUSDT", "XTZDOWNUSDT", "MANAUSDT", "AUDUSDT", "YFIUSDT", "BALUSDT", "BLZUSDT", "IRISUSDT", "KMDUSDT", "JSTUSDT", "SRMUSDT", "ANTUSDT", "CRVUSDT", "SANDUSDT", "OCEANUSDT", "NMRUSDT", "DOTUSDT", "LUNAUSDT", "RSRUSDT", "PAXGUSDT", "WNXMUSDT", "TRBUSDT", "BZRXUSDT", "SUSHIUSDT", "YFIIUSDT", "KSMUSDT", "EGLDUSDT", "DIAUSDT", "RUNEUSDT", "FIOUSDT", "UMAUSDT", "EOSUPUSDT", "EOSDOWNUSDT", "TRXUPUSDT", "TRXDOWNUSDT", "XRPUPUSDT", "XRPDOWNUSDT", "DOTUPUSDT", "DOTDOWNUSDT", "BELUSDT", "WINGUSDT", "LTCUPUSDT", "LTCDOWNUSDT", "UNIUSDT", "NBSUSDT", "OXTUSDT", "SUNUSDT", "AVAXUSDT", "HNTUSDT", "FLMUSDT", "UNIUPUSDT", "UNIDOWNUSDT", "ORNUSDT", "UTKUSDT", "XVSUSDT", "ALPHAUSDT", "AAVEUSDT", "NEARUSDT", "SXPUPUSDT", "SXPDOWNUSDT", "FILUSDT", "FILUPUSDT", "FILDOWNUSDT", "YFIUPUSDT", "YFIDOWNUSDT", "INJUSDT", "AUDIOUSDT", "CTKUSDT", "BCHUPUSDT", "BCHDOWNUSDT", "AKROUSDT", "AXSUSDT", "HARDUSDT", "DNTUSDT", "STRAXUSDT", "UNFIUSDT", "ROSEUSDT", "AVAUSDT", "XEMUSDT", "AAVEUPUSDT", "AAVEDOWNUSDT", "SKLUSDT", "SUSDUSDT", "SUSHIUPUSDT", "SUSHIDOWNUSDT", "XLMUPUSDT", "XLMDOWNUSDT", "GRTUSDT", "JUVUSDT", "PSGUSDT", "1INCHUSDT", "REEFUSDT", "OGUSDT", "ATMUSDT", "ASRUSDT", "CELOUSDT", "RIFUSDT", "BTCSTUSDT", "TRUUSDT", "CKBUSDT", "TWTUSDT", "FIROUSDT", "LITUSDT", "SFPUSDT", "DODOUSDT", "CAKEUSDT", "ACMUSDT", "BADGERUSDT", "FISUSDT", "OMUSDT", "PONDUSDT", "DEGOUSDT", "ALICEUSDT", "LINAUSDT", "PERPUSDT", "RAMPUSDT", "SUPERUSDT", "CFXUSDT", "EPSUSDT", "AUTOUSDT", "TKOUSDT", "PUNDIXUSDT", "TLMUSDT", "1INCHUPUSDT", "1INCHDOWNUSDT", "BTGUSDT", "MIRUSDT", "BARUSDT", "FORTHUSDT", "BAKEUSDT", "BURGERUSDT", "SLPUSDT", "SHIBUSDT", "ICPUSDT", "ARUSDT", "POLSUSDT", "MDXUSDT", "MASKUSDT", "LPTUSDT", "NUUSDT", "XVGUSDT", "ATAUSDT", "GTCUSDT", "TORNUSDT", "KEEPUSDT", "ERNUSDT", "KLAYUSDT", "PHAUSDT", "BONDUSDT", "MLNUSDT", "DEXEUSDT", "C98USDT", "CLVUSDT", "QNTUSDT", "FLOWUSDT", "TVKUSDT", "MINAUSDT", "RAYUSDT", "FARMUSDT", "ALPACAUSDT", "QUICKUSDT", "MBOXUSDT", "FORUSDT", "REQUSDT", "GHSTUSDT", "WAXPUSDT", "TRIBEUSDT", "GNOUSDT", "XECUSDT", "ELFUSDT", "DYDXUSDT", "POLYUSDT", "IDEXUSDT", "VIDTUSDT", "USDPUSDT", "GALAUSDT", "ILVUSDT", "YGGUSDT", "SYSUSDT", "DFUSDT", "FIDAUSDT", "FRONTUSDT", "CVPUSDT", "AGLDUSDT", "RADUSDT", "BETAUSDT", "RAREUSDT", "LAZIOUSDT", "CHESSUSDT", "ADXUSDT", "AUCTIONUSDT", "DARUSDT", "BNXUSDT", "RGTUSDT", "MOVRUSDT", "CITYUSDT", "ENSUSDT", "KP3RUSDT", "QIUSDT", "PORTOUSDT", "POWRUSDT", "VGXUSDT", "JASMYUSDT", "AMPUSDT", "PLAUSDT", "PYRUSDT", "RNDRUSDT", "ALCXUSDT", "SANTOSUSDT", "MCUSDT", "ANYUSDT", "BICOUSDT", "FLUXUSDT", "FXSUSDT", "VOXELUSDT", "HIGHUSDT", "CVXUSDT", "PEOPLEUSDT", "OOKIUSDT", "SPELLUSDT", "USTUSDT", "JOEUSDT", "ACHUSDT", "IMXUSDT", "GLMRUSDT", "LOKAUSDT", "SCRTUSDT", "API3USDT", "BTTCUSDT", "ACAUSDT", "ANCUSDT", "XNOUSDT", "WOOUSDT", "ALPINEUSDT", "TUSDT", "ASTRUSDT", "GMTUSDT", "KDAUSDT", "APEUSDT", "BSWUSDT", "BIFIUSDT", "MULTIUSDT", "STEEMUSDT", "MOBUSDT", "NEXOUSDT", "REIUSDT", "GALUSDT", "LDOUSDT", "EPXUSDT", "OPUSDT", "LEVERUSDT", "STGUSDT", "LUNCUSDT", "GMXUSDT", "NEBLUSDT", "POLYXUSDT", "APTUSDT", "OSMOUSDT", "HFTUSDT", "PHBUSDT", "HOOKUSDT", "MAGICUSDT", "HIFIUSDT", "RPLUSDT", "PROSUSDT", "AGIXUSDT", "GNSUSDT", "SYNUSDT", "VIBUSDT", "SSVUSDT", "LQTYUSDT", "AMBUSDT", "BETHUSDT", "USTCUSDT", "GASUSDT", "GLMUSDT", "PROMUSDT", "QKCUSDT", "UFTUSDT", "IDUSDT", "ARBUSDT", "LOOMUSDT", "OAXUSDT", "RDNTUSDT"]


# interval = "4h"
# limit = 100

# max_threads = 10
# data_list = []

# with ThreadPoolExecutor(max_workers=max_threads) as executor:
#     futures = [executor.submit(fetch_data, symbol) for symbol in symbol_list]

#     for future in as_completed(futures):
#         symbol_df = future.result()
#         data_list.append(symbol_df)

# data_df = pd.concat(data_list, axis=0)

# print(data_df)
# data_df.to_excel("crypto_data.xlsx")
FOD_list = ["BTCUSDT","BTCUSDT","BTCUSDT","BTCUSDT"]
FOB_list = ["BTCUSDT","BTCUSDT","BTCUSDT","BTCUSDT"]
# for symbol in symbol_list:

#     rows = data_df.loc[symbol]
#     prev = rows.iloc[-2]
#     cur = rows.iloc[-1]
#     close = rows.iloc[-1].close
#     prevema4 = prev.EMA4
#     curema4 = cur.EMA4
#     prevma8 = prev.MA8
#     curma8 = cur.MA8
#     prevma20 = prev.MA20
#     curma20 = cur.MA20
#     prevma50 = prev.MA50
#     curma50 = cur.MA50
#     rsi14 = cur.RSI14

#     ema4x8cross = prevema4 < prevma8 and curema4 > curma8
#     strongtrend = curma8 > curma20 > curma50
#     retracetrend = curma20 > curma8 > curma50
#     if ema4x8cross:
#         if strongtrend and rsi14 >= 60:
#             FOD_list.append(symbol)
#         elif retracetrend and rsi14 >= 50:
#             FOB_list.append(symbol)

# print(f"{interval} FOB LIST:")
# print(FOB_list)
# print(f"{interval} FOD LIST:")
# print(FOD_list)
# print("DONE")

application = dash.Dash(__name__)
server = application.server

# Define the layout of the website
application.layout = html.Div(
    [
        html.H1('My Lists'),
        html.Div(
            [
                html.H4('15m FOB LIST'),
                html.Ul(
                    [html.Li(symbol) for symbol in FOB_list]
                )
            ],
            style={'margin-bottom': '10px'}
        ),
        html.Div(
            [
                html.H4('15m FOD LIST'),
                html.Ul(
                    [html.Li(symbol) for symbol in FOD_list]
                )
            ]
        )
    ]
)

if __name__ == '__main__':
    # application.run_server(debug=True)
    application.debug = True
    application.run()
