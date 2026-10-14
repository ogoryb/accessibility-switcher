import time
from threading import Thread

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

from jnius import autoclass

AccService = autoclass('org.example.accswitcher.AccService')


def wait(seconds):
    time.sleep(seconds)


def check_service():
    if not AccService.isConnected():
        raise RuntimeError("Служба отключена")


def click_wifi():
    """Wi-Fi плитка: desc начинается с 'Wi-Fi,' или 'WiFi,' (не 'Вызовы по Wi-Fi')."""
    AccService.openQuickSettings()
    wait(2.5)
    for prefix in ["Wi-Fi,", "WiFi,", "WLAN,", "Wi-Fi", "WiFi"]:
        if AccService.clickByPrefix(prefix):
            return True
    return False


def click_mobile():
    """Мобильная плитка: desc содержит 'Сигнал телефонной сети'."""
    AccService.openQuickSettings()
    wait(2.5)
    for sub in ["Сигнал телефонной сети", "t2,", "T2,", "Т2,"]:
        if AccService.clickBySubstring(sub):
            return True
    return False


def click_hotspot():
    """Точка доступа: desc равно 'Точка доступа' (exact)."""
    AccService.openQuickSettings()
    wait(2.5)
    return AccService.clickByExact("Точка доступа")


def click_confirm_if_appears():
    """Диалог 'Отключить точку доступа?' — ищем ТОЧНОЕ 'Отключить' (без точки).
    Уведомления типа 'Нажмите, чтобы отключить.' не сработают (там подстрока)."""
    wait(1.2)
    for label in ["Отключить", "Выключить", "ОК", "OK"]:
        if AccService.clickByExact(label):
            return True
    return False


def switch_to_mobile():
    check_service()
    click_wifi()
    wait(1.0)
    click_mobile()
    wait(1.0)
    click_hotspot()


def switch_to_wifi():
    check_service()
    click_hotspot()
    click_confirm_if_appears()
    wait(1.0)
    click_mobile()
    wait(1.0)
    click_wifi()


class AccSwitcherApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(Label(
            text="AccSwitcher v2\n\nВключите службу в Специальных возможностях.",
            halign='center'
        ))
        btn1 = Button(text="Переключить на МОБИЛЬНЫЙ", size_hint=(1, 0.3))
        btn1.bind(on_press=lambda x: Thread(target=switch_to_mobile).start())
        layout.add_widget(btn1)

        btn2 = Button(text="Переключить на WI-FI", size_hint=(1, 0.3))
        btn2.bind(on_press=lambda x: Thread(target=switch_to_wifi).start())
        layout.add_widget(btn2)

        return layout


if __name__ == '__main__':
    AccSwitcherApp().run()
