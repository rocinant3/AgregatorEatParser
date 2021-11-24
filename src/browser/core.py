import asyncio
import typing as t
import platform

from pyppeteer import launch
from pyppeteer.element_handle import ElementHandle
from pyppeteer.browser import Browser as Driver
from pyppeteer import connect
from pyppeteer.launcher import executablePath
from pyppeteer.page import Page


class Browser:
    def __init__(self, ):
        self.driver: Driver = None

    async def start(self, ws_endpoint: str = None):
        params = {
            "autoClose": False,
            "headless": False,
            "ignoreHTTPSErrors": True,
            "ignoreDefaultArgs": ["--disable-extensions", "--enable-automation"],
            
            "defaultViewport": None,
            'args': [
                '--enable-automation', '--enable-remote-extensions',
                '--no-sandbox']
        }

        # if platform.system() == "Windows":

        #     executable_path = r"C:\Users\W7\Desktop\chrome-win32\chrome.exe"
        #     params["executablePath"] = executable_path

        if ws_endpoint:
            params["browserWSEndpoint"] = ws_endpoint
            self.driver = await connect(**params)
        else:
            self.driver = await launch(**params)

    async def _close_about_blank_page(self):
        pages = await self.driver.pages()
        if len(pages) > 1 and pages[0].url == 'about:blank':
            await pages[0].close()

    @staticmethod
    async def _set_viewport(page: Page):
        await page.setViewport({'width': 1410, 'height': 1070})

    @staticmethod
    async def disable_dynamic_content(page: Page):
        await page.setRequestInterception(True)

        async def intercept(request):
            if any(request.resourceType == _ for _ in ('image',)):
                await request.abort()
            else:
                await request.continue_()

        page.on('request', lambda req: asyncio.ensure_future(intercept(req)))

    async def new_page(self, url: str = None):
        page = await self.driver.newPage()
        page.setDefaultNavigationTimeout(0)
        # await self.disable_dynamic_content(page)
        if url:
            await self.go_to(page, url)
        # await self._set_viewport(page)
        return page

    @staticmethod
    async def wait(seconds: t.Union[int, float]):
        await asyncio.sleep(seconds)

    @staticmethod
    async def go_to(page: Page, url: str) -> None:

        options = {'waitUntil': 'domcontentloaded', "timeout": 0}
        await page.goto(url, options)

    async def get_current_page(self) -> t.Optional[Page]:
        pages = await self.driver.pages()
        for page in pages:
            is_hidden = await page.evaluate("()=> document.hidden")
            if not is_hidden:
                return page
        return None

    async def switch_page(self, page: Page) -> None:
        await page.bringToFront()
        # await self._set_viewport(page)

    @staticmethod
    async def get_text(el: "HandledType") -> t.Optional[str]:
        content = await el.getProperty('textContent')
        value = await content.jsonValue()
        if isinstance(value, dict):
            return None
        return str(value)

    @staticmethod
    async def get_input_value(el: "HandledType") -> t.Optional[str]:
        content = await el.getProperty('value')
        value = await content.jsonValue()
        if isinstance(value, dict):
            return None
        return str(value)

    @staticmethod
    async def reload_page(page: Page):
        await page.reload()

    @staticmethod
    async def get_element(el: "HandledType", expression: str):
        return await el.querySelector(expression)

    @staticmethod
    async def wait_element(el: "HandledType", expression: str, timeout: int = 30000):
        return await el.waitForSelector(expression, timeout=timeout)

    @staticmethod
    async def get_elements(el: "HandledType", expression: str):
        return await el.querySelectorAll(expression)

    @staticmethod
    async def get_elements_by_xpath(el: "HandledType", expression: str):
        return await el.xpath(expression)

    @staticmethod
    async def send_text(page: Page, el: ElementHandle, text: str):
        await el.type(text)

    @staticmethod
    async def click_on(page: Page, el: ElementHandle):
        await page.evaluate('(element) => element.click()', el)

    async def stop(self):
        await self.driver.close()



HandledType = t.Union[Page, ElementHandle]
