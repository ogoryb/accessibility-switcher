import time
from threading import Thread

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

from jnius import autoclass

PythonActivity = autoclass('org.kivy.android.PythonActivity')
Intent = autoclass('android.content.Intent')
Settings = autoclass('android.provider.Settings')

AccService = autoclass('org.example.accswitcher.AccService')


def open_screen(action_name):
    activity = PythonActivity.mActivity
    intent = Intent(action_name)
    intent.addFlags(0x10000000)
    activity.startActivity(intent)


def click(text, delay=2.0):
    time.sleep(delay)
    try:
        result = AccService.clickByText(text)
        print("CLICK '%s' -> %s" % (text, result))
        return result
    except Exception as e:
        print("ERROR click '%s': %s" % (text, e))
        return False


def switch_to_mobile():
    print("=== SWITCH TO MOBILE ===")
    open_screen(Settings.ACTION_WIFI_SETTINGS)
    click("Wi-Fi", delay=3.0)

    time.sleep(1)
    open_screen(Settings.ACTION_DATA_ROAMING_SETTINGS)
    click("Мобильные данные", delay=3.0)
    click("Mobile data", delay=1.0)

    time.sleep(1)
    open_screen(Settings.ACTION_WIRELESS_SETTINGS)
    click("Точка доступа", delay=3.0)
    click("Hotspot", delay=1.0)

    print("=== DONE ===")


def switch_to_wifi():
    print("=== SWITCH TO WIFI ===")
    open_screen(Settings.ACTION_WIRELESS_SETTINGS)
    click("Точка доступа", delay=3.0)
    click("Hotspot", delay=1.0)

    time.sleep(1)
    open_screen(Settings.ACTION_DATA_ROAMING_SETTINGS)
    click("Мобильные данные", delay=3.0)
    click("Mobile data", delay=1.0)

    time.sleep(1)
    open_screen(Settings.ACTION_WIFI_SETTINGS)
    click("Wi-Fi", delay=3.0)

    print("=== DONE ===")


class AccSwitcherApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        layout.add_widget(Label(
            text="AccSwitcher\n\nНажмите кнопку, чтобы проверить работу.\n"
                 "Расписание добавим позже.",
            halign='center'
        ))
        btn1 = Button(text="Тест: переключить на МОБИЛЬНЫЙ", size_hint=(1, 0.3))
        btn1.bind(on_press=lambda x: Thread(target=switch_to_mobile).start())
        layout.add_widget(btn1)

        btn2 = Button(text="Тест: переключить на WI-FI", size_hint=(1, 0.3))
        btn2.bind(on_press=lambda x: Thread(target=switch_to_wifi).start())
        layout.add_widget(btn2)

        return layout


if __name__ == '__main__':
    AccSwitcherApp().run()
