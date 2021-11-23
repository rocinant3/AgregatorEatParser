import asyncio as aio

from decouple import config
from pyppeteer.errors import BrowserError

from eat_parser import AgregatorEatParser

login = config("LOGIN")
password = config("PASSWORD")
inn = config("INN")
price = config("PRICE")
pin_code = config("PIN_CODE")
cert_name = config("CERT_NAME")

parser = AgregatorEatParser(
    login=login,
    password=password,
    inn=inn,
    price=price,
    pin_code=pin_code,
    cert_name=cert_name
)

if __name__ == "__main__":
    loop = aio.get_event_loop()
    try:
        loop.run_until_complete(parser.start())
    except Exception:
        try:
            loop.run_until_complete(parser.browser.stop())
        except BrowserError:
            pass
        loop.close()
