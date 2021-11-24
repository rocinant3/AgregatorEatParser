import asyncio as aio
from re import L

from pyppeteer.errors import TimeoutError

from browser.core import Browser, Page
from crypto_win import CryptoWin


class StopAppError(Exception):
    pass

class AgregatorEatParser:

    def __init__(
        self, 
        login: str,
        password: str, 
        inn: str, 
        price: str,
        cert_name: str,
        pin_code: str,
        keywoard: str
    ):
        self.login = login
        self.password = password
        self.inn = inn
        self.price = price
        self.cert_name = cert_name
        self.pin_code = pin_code
        self.keywoard = keywoard
        self.browser = Browser()

    
    async def load_crypto_pro_extension(self):
        page = await self.browser.new_page(
            "https://chrome.google.com/webstore/detail/cryptopro-extension-for-c/iifchhfnnmpdbibifmljnfjhpififfog?hl=ru"
        )
        await self.browser.wait(2)
        install_btn =  await self.browser.get_elements_by_xpath(page, "//div[contains(text(),'Установить')]")
        await self.browser.click_on(page, install_btn[0])
        while not page.isClosed():
            await self.browser.wait(1)
        

    async def auth(self, page: Page):
        await self.browser.go_to(page, 'https://agregatoreat.ru/')
        login_btn = await self.browser.wait_element(page, '.login-btn')
        await self.browser.click_on(page, login_btn)
        lk_menu = await self.browser.get_element(page, '.lk-menu')
        lk_menu_items = await self.browser.get_elements(lk_menu, 'a.lk-menu-item')
        login_as_provider_btn = lk_menu_items[0]
        await self.browser.click_on(page, login_as_provider_btn)

        login_form = await self.browser.wait_element(page, 'fieldset')
        login_input = await self.browser.get_element(login_form, "#Username")
        password_input = await self.browser.get_element(login_form, "#passwordInput")
        approve_btn = await self.browser.get_element(login_form, '.btn-success')

        await self.browser.send_text(page, login_input, self.login)
        await self.browser.send_text(page, password_input, self.password)
        await self.browser.click_on(page, approve_btn)

    async def monitor_order(self, page: Page):
        await self.browser.go_to(page, 'https://agregatoreat.ru/purchases/new')
        filter_sidebar = await self.browser.wait_element(page, '#filter_sidebar')
        inn_input = await self.browser.wait_element(page, '#filterField-13-autocomplete')
        keywoard_input = await self.browser.wait_element(page, "#filterField-1-input")
        apply_filter_btn = await self.browser.get_element(filter_sidebar, '#applyFilterButton')

        await self.browser.send_text(page, inn_input, self.inn)
        await self.browser.send_text(page, keywoard_input, self.keywoard)

        purchases_list = await self.browser.wait_element(page, 'app-purchase-registry')
        is_not_found = True

        async def find_purchase_items():
            nonlocal is_not_found, self
            try:
                await self.browser.wait_element(page, 'app-not-found', timeout=1000)
            except TimeoutError:
                is_not_found = False

        while is_not_found:
            await self.browser.click_on(page, apply_filter_btn)
            await self.browser.wait(1)
            await find_purchase_items()

        purchase_items = await self.browser.get_elements(purchases_list, 'app-purchase-card')
        for purchase_item in purchase_items:
            approve_purchase_btn = await self.browser.get_element(purchase_item, '#applicationSendButton')
            if not approve_purchase_btn:
                continue
            await self.browser.click_on(page, approve_purchase_btn)
            await self.make_purchase(page)
            break

    async def make_purchase(self, page: Page):
        main_container = await self.browser.wait_element(page, 'app-purchase-application')
        price_input = await self.browser.wait_element(page, '#lotItemPriceInput-0')
        for sym in self.price:
            await self.browser.send_text(page, price_input, sym)

        tax_select = await self.browser.get_elements_by_xpath(main_container, "//*[@inputid='lotItemTaxPercentInput']")
        tax_select = await self.browser.get_element(tax_select[0], ".ui-dropdown")

        await self.browser.click_on(page, tax_select)
        await self.browser.wait(1)
        tax_items = await self.browser.get_elements(tax_select, 'p-dropdownitem')
        tax_item = await self.browser.get_element(tax_items[0], '.ui-dropdown-item')
        await self.browser.click_on(page, tax_item)

        approve_btn = await self.browser.get_elements_by_xpath(
            main_container,
            "//button[contains(text(),'Подать предложение')]"
        )
        approve_btn = approve_btn[0]
        await self.browser.click_on(page, approve_btn)

        confirm_popup = await self.browser.wait_element(page, 'app-confirm-application-window')
        confirm_btn = await self.browser.get_elements_by_xpath(
            confirm_popup,
            "//button[contains(text(),'Подтвердить')]"
        )
        confirm_btn = confirm_btn[0]
        await self.browser.click_on(page, confirm_btn)

        dynamic_dialog = await self.browser.wait_element(page, 'p-dynamicdialog')
        sign_button = await self.browser.wait_element(page, '#signButton')
        await self.browser.click_on(page, sign_button)
        crypto_win = CryptoWin()
        try:
            crypto_win.approve_access()
        except Exception:
            await self.browser.wait(2)     
            crypto_win.approve_access()


        cert_modal = await self.browser.wait_element(
            page, 
            'p-dynamicdialog'
        )

        await self.browser.wait(1)
        certs = await self.browser.get_elements(cert_modal, '.cert-form__row')
        for cert in certs:
            cert_name = await self.browser.get_element(cert, ".cert-form__name")
            cert_name = await self.browser.get_text(cert_name)
            if self.cert_name.strip().lower() == cert_name.strip().lower():
                await self.browser.click_on(page, cert)
                break
        
        cert_modal_approve_button = await self.browser.get_element(cert_modal,'button.c-btn.c-btn--primary')
        await self.browser.click_on(page, cert_modal_approve_button)

        try:
            crypto_win.auth_crypto_pro(self.pin_code)
        except Exception:
            await self.browser.wait(2)
            crypto_win.auth_crypto_pro(self.pin_code)

    async def start(self):
        await self.browser.start()
        await self.load_crypto_pro_extension()
        page = await self.browser.new_page()
        await self.auth(page)
        await self.monitor_order(page)
        raise StopAppError
