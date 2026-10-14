import time
from threading import Thread

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

from jnius import autoclass

AccService = autoclass('org.example.accswitcher.AccService')

WIFI_LABELS = ["Wi-Fi", "WLAN", "WiFi"]
MOBILE_LABELS = ["t2", "T2", "Т2", "Мобильные данные", "Мобильный интернет", "Mobile data"]
HOTSPOT_LABELS = ["Точка доступа Wi-Fi", "Точка доступа", "Hotspot"]
CONFIRM_LABELS = ["Отключить", "Выключить", "ОК", "OK", "Да", "Turn off", "Disable"]


def wait(seconds):
    time.sleep(seconds)


def check_service():
    """Проверяем, подключена ли служба. Если нет — бросаем исключение."""
    if not AccService.isConnected():
        raise RuntimeError("Служба доступности не подключена. Включите AccSwitcher в Специальных возможностях.")


def click_tile(label_variants):
    check_service()
    AccService.openQuickSettings()
    wait(2.5)
    for label in label_variants:
        if AccService.hasText(label):
            return AccService.clickByText(label)
    return False


def click_confirm_if_appears():
    check_service()
    wait(1.5)
    for label in CONFIRM_LABELS:
        if AccService.hasText(label):
            if AccService.clickByText(label):
                return True
    return False


def switch_to_mobile():
    check_service()
    click_tile(WIFI_LABELS)
    wait(1.5)
    click_tile(MOBILE_LABELS)
    wait(1.5)
    click_tile(HOTSPOT_LABELS)


def switch_to_wifi():
    check_service()
    click_tile(HOTSPOT_LABELS)
    click_confirm_if_appears()
    wait(1.5)
    click_tile(MOBILE_LABELS)
    wait(1.5)
    click_tile(WIFI_LABELS)


class AccSwitcherApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(Label(
            text="AccSwitcher\n\nКнопка не работает? Включите службу в Специальных возможностях.",
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
