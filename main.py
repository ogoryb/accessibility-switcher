import time
from threading import Thread

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

from jnius import autoclass

AccService = autoclass('org.example.accswitcher.AccService')

# Варианты подписей на плитках (может отличаться в зависимости от оператора)
WIFI_LABELS = ["Wi-Fi", "WLAN", "WiFi"]
MOBILE_LABELS = ["t2", "T2", "Т2", "Мобильные данные", "Мобильный интернет",
                 "Mobile data", "Mobile network"]
HOTSPOT_LABELS = ["Точка доступа Wi-Fi", "Точка доступа", "Hotspot"]


def wait(seconds):
    time.sleep(seconds)


def ensure_state(label_variants, desired, max_attempts=4):
    for attempt in range(max_attempts):
        state = -1
        found_label = None
        for label in label_variants:
            state = AccService.getStateByText(label)
            if state != -1:
                found_label = label
                break
        print("STATE %s = %s (attempt %d)" % (label_variants, state, attempt + 1))
        if state == -1:
            wait(0.8)
            continue
        if state == 1 and desired:
            return True
        if state == 0 and not desired:
            return True
        AccService.clickByText(found_label)
        wait(1.5)
    return False


def switch_to_mobile():
    print("=== SWITCH TO MOBILE ===")
    AccService.openQuickSettings()
    wait(2.0)
    ensure_state(WIFI_LABELS, False)
    wait(0.8)
    ensure_state(MOBILE_LABELS, True)
    wait(0.8)
    ensure_state(HOTSPOT_LABELS, True)
    print("=== DONE ===")


def switch_to_wifi():
    print("=== SWITCH TO WIFI ===")
    AccService.openQuickSettings()
    wait(2.0)
    ensure_state(HOTSPOT_LABELS, False)
    wait(0.8)
    ensure_state(MOBILE_LABELS, False)
    wait(0.8)
    ensure_state(WIFI_LABELS, True)
    print("=== DONE ===")


def dump_all():
    print("=== DUMP ALL TEXTS ===")
    AccService.openQuickSettings()
    wait(2.0)
    AccService.dumpTexts()
    print("=== DUMP SENT — смотрите logcat ===")


class AccSwitcherApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        layout.add_widget(Label(
            text="AccSwitcher\n\nТест через панель быстрых настроек",
            halign='center'
        ))
        btn1 = Button(text="Тест: МОБИЛЬНЫЙ", size_hint=(1, 0.22))
        btn1.bind(on_press=lambda x: Thread(target=switch_to_mobile).start())
        layout.add_widget(btn1)

        btn2 = Button(text="Тест: WI-FI", size_hint=(1, 0.22))
        btn2.bind(on_press=lambda x: Thread(target=switch_to_wifi).start())
        layout.add_widget(btn2)

        btn3 = Button(text="ДИАГНОСТИКА (показать все надписи)", size_hint=(1, 0.22))
        btn3.bind(on_press=lambda x: Thread(target=dump_all).start())
        layout.add_widget(btn3)

        return layout


if __name__ == '__main__':
    AccSwitcherApp().run()
