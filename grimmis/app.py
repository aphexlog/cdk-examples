import polygon
import dotenv

POLYGON_TOKEN: str = str(dotenv.get_key(key_to_get='POLYGON_TOKEN', dotenv_path='.env'))

stocks_client = polygon.StocksClient(POLYGON_TOKEN)

previous_close = stocks_client.get_previous_close('TSLA')

def main():
    print(previous_close)

if __name__ == '__main__':
    main()
