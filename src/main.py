import asyncio as aio

from decouple import config

from parser import AgregatorEatParser

login = config("LOGIN")
password = config("PASSWORD")
inn = config("INN")
price = config("PRICE")

parser = AgregatorEatParser(
    login=login,
    password=password,
    inn=inn,
    price=price
)

if __name__ == "__main__":
    loop = aio.get_event_loop()
    loop.run_until_complete(parser.start())
