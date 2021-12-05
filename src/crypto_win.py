from pywinauto import application



class CryptoWin:

    @staticmethod
    def approve_access():

        app = application.Application(backend="uia").connect(title="Подтверждение доступа", timeout=10)
    
        confirmWin = app.window(title_re=u'Подтверждение доступа')

        if confirmWin.exists(timeout=10, retry_interval=1):
        
            confirmWin.set_focus()
            yesBtn = confirmWin[u'&Да']
            yesBtn.click()
    
    @staticmethod
    def auth_crypto_pro(code: str):
        app = application.Application(backend="uia").connect(
            title_re=r"Аутентификация - КриптоПро CSP",
            timeout=5
        )
        win = app.window(title_re=r'Аутентификация - КриптоПро CSP')
        win.print_control_identifiers()
        win.set_focus()
        win.Edit.set_text(code)
        win.OK.click()