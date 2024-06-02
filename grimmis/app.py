import dotenv
import polygon
from alpaca_trade_api.rest import REST, TimeFrame

ALPACA_SECRET: str = str(dotenv.get_key(key_to_get='ALPACA_SECRET', dotenv_path='.env'))
ALPACA_KEY: str = str(dotenv.get_key(key_to_get='ALPACA_KEY', dotenv_path='.env'))
api = REST(secret_key=ALPACA_SECRET, key_id=ALPACA_KEY)
result = api.get_bars("TSLA", TimeFrame.Hour, "2021-06-08", "2021-06-08", adjustment='raw').df


POLYGON_TOKEN: str = str(dotenv.get_key(key_to_get='POLYGON_TOKEN', dotenv_path='.env'))

stocks_client = polygon.StocksClient(POLYGON_TOKEN)

previous_close = stocks_client.get_previous_close('TSLA')

def main():
    print(previous_close)
    print(result)
    print(f"that was {len(result)} bars and the ticker is {result.iloc[0]}")

if __name__ == '__main__':
    main()
