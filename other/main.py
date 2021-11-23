from sqlite3 import connect
from time import sleep

from requests import post
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException, \
    ElementClickInterceptedException
from selenium.webdriver import Chrome, ChromeOptions, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from pywinauto import application

from Levenshtein import ratio

from config import TRADES_URL, MAIN_URL


DRIVER_WAIT_TIME = 60


options = ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_extension('plugin.crx')
options.add_argument('--start-maximized')
options.add_experimental_option("excludeSwitches", ["enable-logging"])

driver = Chrome(executable_path=ChromeDriverManager().install(), options=options)

waiter = WebDriverWait(driver, DRIVER_WAIT_TIME)

driver.get(MAIN_URL)

login_refresh_button = waiter.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button.btn.btn--yellow.login-btn')))
login_refresh_button.click()
enter_as_refresh = waiter.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, 'a.lk-menu-item.ng-star-inserted:nth-of-type(1)')))
enter_as_refresh[0].click()

form = waiter.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'form#loginForm')))

account_login = input('Введите логин аккаунта: ').strip()

account_password = input('Введите пароль аккаунта: ').strip()

username_input = waiter.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input#Username')))
username_input.clear()
username_input.send_keys(account_login)

password_input = waiter.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input#passwordInput')))
password_input.clear()
password_input.send_keys(account_password)

submit_login = waiter.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'button[type="submit"]')))
submit_login.click()

driver.get(TRADES_URL)

INN = input('Введите ИНН для поиска: ')

cert_name = input('Введите название сертификата: ')

procedure = input('Введите ключевую фразу, номер процедуры или нажмите Enter для выбора всех процедур: ')

code = input('Введите пин: ')

tru_first_message = input('Введите первое ТРУ: ')
tru_second_message = input('Введите второе ТРУ: ')

conn = connect('orders.db')
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS trades '
               '('
               'trade_id INTEGER,'
               'ordered BOOLEAN'
               ')')

while True:
    driver.get(TRADES_URL)
    try:
        log = waiter.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.login-btn__caption')))
        if log.text.strip().lower() == 'личный кабинет':
            login_refresh_button = waiter.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'button.btn.btn--yellow.login-btn')))
            login_refresh_button.click()
            enter_as_refresh = waiter.until(
                EC.visibility_of_all_elements_located(
                    (By.CSS_SELECTOR, 'a.lk-menu-item.ng-star-inserted:nth-of-type(1)')))
            try:
                enter_as_refresh[0].click()
            except Exception as e:
                continue
            continue
    except TimeoutException:
        continue
    try:
        inn_input = waiter.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input#filterField-13-autocomplete')))
    except TimeoutException:
        continue
    inn_input.clear()
    inn_input.send_keys(INN)
    try:
        only_eat = waiter.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ui-inputswitch.ui-widget')))
    except TimeoutException:
        continue
    ActionChains(driver).move_to_element(only_eat).click().perform()

    if procedure.isdigit():
        try:
            procedure_num_input = waiter.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input#filterField-2-input')))
        except TimeoutException:
            continue
        procedure_num_input.clear()
        procedure_num_input.send_keys(procedure)
    elif not len(procedure):
        pass
    else:
        try:
            filters_input = waiter.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input#filterField-1-input')))
        except TimeoutException:
            continue
        filters_input.clear()
        filters_input.send_keys(procedure)
    try:
        apply_filters_button = waiter.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button#applyFilterButton')))
    except TimeoutException:
        continue
    ActionChains(driver).move_to_element_with_offset(apply_filters_button, 0, -300).perform()
    apply_filters_button.click()

    try:
        cards = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.registry-cards')))
        all_cards = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'app-purchase-card.ng-star-inserted')))
    except TimeoutException:
        continue
    except NoSuchElementException:
        continue
    except Exception as e:
        continue
    if not len(all_cards):
        continue
    for card in all_cards:
        trade_number = card.find_element(By.CSS_SELECTOR, 'h3.trade-number.pointer.ng-star-inserted > a').text
        cursor.execute(f'SELECT * FROM trades WHERE trade_id = {trade_number}')
        res = cursor.fetchone()
        if res is None:
            cursor.execute(f'INSERT INTO trades (trade_id, ordered) VALUES ({trade_number}, {False})')
            conn.commit()
            continue
        if not bool(res[1]):
            card.find_element(By.CSS_SELECTOR, 'button#applicationSendButton').click()
            items = waiter.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'tr.ng-star-inserted')))
            sleep(2)
            try:
                driver.find_element(By.CSS_SELECTOR, 'svg-icon.modal-window__close').click()
            except NoSuchElementException:
                pass
            try:
                tru_button = driver.find_element(By.CSS_SELECTOR, 'svg-icon.select-tru__icon.ng-star-inserted')
                tru_button.click()
            except NoSuchElementException:
                pass
            else:
                create_new_tru_button = waiter.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.tru-description-modal__action:nth-of-type(3)')))
                ActionChains(driver).move_to_element(create_new_tru_button).perform()
                create_new_tru_button.click()
                name = waiter.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input#name')))
                name.send_keys(tru_first_message)
                desc = waiter.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'textarea#description')))
                desc.send_keys(tru_second_message)
                save_tru_button = waiter.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".modal-window__buttons-container > button:nth-of-type(2)")))
                save_tru_button.click()
            num = 0
            for item in items:
                sleep(2)
                try:
                    price_nds = waiter.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.ui-chkbox-box.ui-widget.ui-corner-all.ui-state-default.ui-state-active')))
                    price_nds.click()
                except TimeoutException:
                    pass
                try:
                    item_price = waiter.until(EC.visibility_of_element_located((By.CSS_SELECTOR, f'input#lotItemPriceInput-{num}')))
                    item_price.send_keys(Keys.BACKSPACE * 20)
                    item_price.send_keys('0,0001')
                except Exception as e:
                    pass
                try:
                    nds_dropdown = item.find_element(By.CSS_SELECTOR, 'div.ui-dropdown-trigger')
                    nds_dropdown.click()
                    nds_dropdown_option = item.find_elements(By.CSS_SELECTOR, 'li.ui-dropdown-item.ui-corner-all')[0]
                    nds_dropdown_option.click()
                except Exception as e:
                    pass
                num += 1
            submit_order_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.c-btn-group > button')))
            ActionChains(driver).move_to_element(driver.find_element(By.CSS_SELECTOR, 'footer.footer')).perform()
            try:
                submit_order_button.click()
            except Exception as e:
                items = waiter.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'tr.ng-star-inserted')))
                num = 0
                for item in items:
                    sleep(2)
                    try:
                        price_nds = waiter.until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                                 '.ui-chkbox-box.ui-widget.ui-corner-all.ui-state-default.ui-state-active')))
                        price_nds.click()
                    except TimeoutException:
                        pass
                    try:
                        item_price = waiter.until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, f'input#lotItemPriceInput-{num}')))
                        item_price.send_keys(Keys.BACKSPACE * 20)
                        item_price.send_keys('0,01')
                    except Exception as e:
                        pass
                    try:
                        nds_dropdown = item.find_element(By.CSS_SELECTOR, 'div.ui-dropdown-trigger')
                        nds_dropdown.click()
                        nds_dropdown_option = item.find_elements(By.CSS_SELECTOR, 'li.ui-dropdown-item.ui-corner-all')[
                            0]
                        nds_dropdown_option.click()
                    except Exception as e:
                        pass
                    num += 1
            confirm_button = waiter.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.dynamic-modal-window__buttons-container > button:nth-of-type(2)')))
            confirm_button.click()
            sign_button = waiter.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button#signButton')))
            sign_button.click()
            try:
                app = application.Application(backend="uia").connect(title="Подтверждение доступа", timeout=5)
                confirmWin = app.window(title_re=u'Подтверждение доступа')
                if confirmWin.exists(timeout=10, retry_interval=1):
                    confirmWin.set_focus()
                    yesBtn = confirmWin[u'&Да']
                    yesBtn.click()
            except Exception as e:
                sleep(2)
                try:
                    app = application.Application(backend="uia").connect(title="Подтверждение доступа", timeout=5)
                    confirmWin = app.window(title_re=u'Подтверждение доступа')
                    if confirmWin.exists(timeout=10, retry_interval=1):
                        confirmWin.set_focus()
                        yesBtn = confirmWin[u'&Да']
                        yesBtn.click()
                except Exception as e:
                    break
            popup = waiter.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.cert-modal.ui-dialog.ui-dynamicdialog.ui-widget.ui-widget-content.ui-corner-all.ui-shadow.ng-star-inserted')))
            certs = waiter.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'span.fullname')))
            for certificate in certs:
                if cert_name.strip().lower() == certificate.text.strip().lower():
                    certificate.click()
                    break
            popup.find_element(By.CSS_SELECTOR, 'button.c-btn.c-btn--primary').click()
            sleep(1)
            try:
                app = application.Application(backend="uia").connect(title_re=r"Аутентификация - КриптоПро CSP",
                                                                     timeout=5)
                win = app.window(title_re=r'Аутентификация - КриптоПро CSP')
                win.print_control_identifiers()
                win.set_focus()
                win.Edit.set_text(code)
                win.OK.click()
            except Exception as e:
                sleep(2)
                try:
                    app = application.Application(backend="uia").connect(title_re=r"Аутентификация - КриптоПро CSP",
                                                                         timeout=5)
                    win = app.window(title_re=r'Аутентификация - КриптоПро CSP')
                    win.print_control_identifiers()
                    win.set_focus()
                    win.Edit.set_text(code)
                    win.OK.click()
                except Exception as e:
                    break
            try:
                app = application.Application(backend="uia").connect(title_re=r"Аутентификация - КриптоПро CSP",
                                                                     timeout=5)
                win = app.window(title_re=r'Аутентификация - КриптоПро CSP')
                win.print_control_identifiers()
                win.set_focus()
                win.Edit.set_text(code)
                win.OK.click()
            except Exception as e:
                sleep(2)
                try:
                    app = application.Application(backend="uia").connect(title_re=r"Аутентификация - КриптоПро CSP",
                                                                         timeout=5)
                    win = app.window(title_re=r'Аутентификация - КриптоПро CSP')
                    win.print_control_identifiers()
                    win.set_focus()
                    win.Edit.set_text(code)
                    win.OK.click()
                except Exception as e:
                    break
