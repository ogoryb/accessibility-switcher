import time
from threading import Thread

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

from jnius import autoclass

AccService = autoclass('org.example.accswitcher.AccService')

WIFI_LABELS = ["Wi-Fi", "WLAN", "WiFi", "wi-fi"]
MOBILE_LABELS = ["t2", "T2", "Т2", "Мобильные данные", "Мобильный интернет", "Mobile data"]
HOTSPOT_LABELS = ["Точка доступа Wi-Fi", "Точка доступа", "Hotspot"]


def wait(seconds):
    time.sleep(seconds)


def open_panel():
    AccService.openQuickSettings()
    wait(2.0)


def toggle_once(label_variants, desired):
    """Открывает шторку, проверяет состояние, при необходимости кликает. Возвращает True/False."""
    for attempt in range(3):
        open_panel()
        state = -1
        found_label = None
        for label in label_variants:
            state = AccService.getStateByText(label)
            if state != -1:
                found_label = label
                break
        print("STATE %s = %s (attempt %d)" % (label_variants, state, attempt + 1))
        if state == -1:
            wait(1.0)
            continue
        if state == 1 and desired:
            return True
        if state == 0 and not desired:
            return True
        AccService.clickByText(found_label)
        wait(2.0)
    return False


def switch_to_mobile():
    print("=== SWITCH TO MOBILE ===")
    toggle_once(WIFI_LABELS, False)
    toggle_once(MOBILE_LABELS, True)
    toggle_once(HOTSPOT_LABELS, True)
    print("=== DONE ===")


def switch_to_wifi():
    print("=== SWITCH TO WIFI ===")
    toggle_once(HOTSPOT_LABELS, False)
    toggle_once(MOBILE_LABELS, False)
    toggle_once(WIFI_LABELS, True)
    print("=== DONE ===")


class AccSwitcherApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(Label(
            text="AccSwitcher\n\nТест через панель быстрых настроек",
            halign='center'
        ))
        btn1 = Button(text="Тест: МОБИЛЬНЫЙ", size_hint=(1, 0.3))
        btn1.bind(on_press=lambda x: Thread(target=switch_to_mobile).start())
        layout.add_widget(btn1)

        btn2 = Button(text="Тест: WI-FI", size_hint=(1, 0.3))
        btn2.bind(on_press=lambda x: Thread(target=switch_to_wifi).start())
        layout.add_widget(btn2)

        return layout


if __name__ == '__main__':
    AccSwitcherApp().run()
