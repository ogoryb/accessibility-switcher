import os
import time
from datetime import datetime
from threading import Thread

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.scrollview import ScrollView

from kivy.core.window import Window
Window.softinput_mode = 'pan'

from jnius import autoclass

AccService = autoclass('org.example.accswitcher.AccService')

SCHEDULE_FILE = None


def log(msg):
    try:
        AccService.log(str(msg))
    except Exception:
        pass


# ============ Переключение плиток ============

def wait(seconds):
    time.sleep(seconds)


def check_service():
    if not AccService.isConnected():
        raise RuntimeError("Служба отключена")


def click_wifi():
    AccService.openQuickSettings()
    wait(2.5)
    for prefix in ["Wi-Fi,", "WiFi,", "WLAN,", "Wi-Fi", "WiFi"]:
        if AccService.clickByPrefix(prefix):
            return True
    return False


def click_mobile():
    AccService.openQuickSettings()
    wait(2.5)
    for sub in ["Сигнал телефонной сети", "t2,", "T2,", "Т2,"]:
        if AccService.clickBySubstring(sub):
            return True
    return False


def click_hotspot():
    AccService.openQuickSettings()
    wait(2.5)
    return AccService.clickByExact("Точка доступа")


def click_confirm_if_appears():
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
    wait(1.5)
    AccService.closePanel()


def switch_to_wifi():
    check_service()
    click_hotspot()
    click_confirm_if_appears()
    wait(1.0)
    click_mobile()
    wait(1.0)
    click_wifi()
    wait(1.5)
    AccService.closePanel()


# ============ Время ============

def normalize_time(raw):
    s = raw.strip().replace(":", "").replace(".", "").replace(" ", "")
    if not s.isdigit():
        return None
    if len(s) == 3:
        s = "0" + s
    if len(s) != 4:
        return None
    h, m = int(s[:2]), int(s[2:])
    if not (0 <= h <= 23 and 0 <= m <= 59):
        return None
    return "%02d:%02d" % (h, m)


# ============ Файл расписания ============

def load_schedule():
    records = []
    enabled = False
    if SCHEDULE_FILE and os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if line == "enabled=1":
                    enabled = True
                elif line.startswith("enabled="):
                    enabled = False
                else:
                    parts = line.split()
                    if len(parts) == 2:
                        records.append((parts[0], parts[1]))
    return records, enabled


def save_schedule(records, enabled):
    if not SCHEDULE_FILE:
        return
    try:
        with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
            f.write("enabled=%d\n" % (1 if enabled else 0))
            for t, a in records:
                f.write("%s %s\n" % (t, a))
    except Exception as e:
        log("save error: %s" % e)


# ============ Планировщик ============

class Scheduler(Thread):
    def __init__(self, app):
        super().__init__(daemon=True)
        self.app = app
        self.done_today = {}

    def run(self):
        log("Scheduler started")
        while True:
            time.sleep(20)
            try:
                records, enabled = load_schedule()
                if not enabled:
                    log("sched: disabled")
                    continue

                now = datetime.now()
                now_hhmm = now.strftime("%H:%M")
                today = now.strftime("%Y-%m-%d")
                log("sched tick %s, records=%d" % (now_hhmm, len(records)))

                for t, action in records:
                    if t != now_hhmm:
                        continue
                    key = (t, action)
                    if self.done_today.get(key) == today:
                        log("sched skip done %s %s" % (t, action))
                        continue
                    self.done_today[key] = today
                    log("SCHEDULE trigger: %s %s" % (t, action))
                    try:
                        if action == "mobile":
                            switch_to_mobile()
                        elif action == "wifi":
                            switch_to_wifi()
                        log("sched done %s %s" % (t, action))
                    except Exception as e:
                        log("sched run error: %s" % e)
            except Exception as e:
                log("scheduler loop error: %s" % e)


# ============ Элемент списка ============

class ScheduleItem(BoxLayout):
    def __init__(self, time_str, action, on_delete, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=50, **kwargs)
        name = "МОБИЛЬНЫЙ" if action == "mobile" else "WI-FI"
        lbl = Label(text="%s → %s" % (time_str, name), size_hint_x=0.75)
        self.add_widget(lbl)
        btn = Button(text="✕", size_hint_x=0.25)
        btn.bind(on_press=lambda x: on_delete(time_str, action))
        self.add_widget(btn)


# ============ Приложение ============

class AccSwitcherApp(App):
    def build(self):
        global SCHEDULE_FILE
        SCHEDULE_FILE = os.path.join(self.user_data_dir, "schedule.txt")
        self.records, self.schedule_enabled = load_schedule()

        root = BoxLayout(orientation='vertical', padding=10, spacing=6)

        root.add_widget(Label(text="AccSwitcher — расписание", size_hint_y=None, height=30))

        top = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        top.add_widget(Label(text="Включить расписание:"))
        self.enabled_cb = CheckBox(active=self.schedule_enabled)
        self.enabled_cb.bind(active=self.on_enabled)
        top.add_widget(self.enabled_cb)
        root.add_widget(top)

        self.list_box = BoxLayout(orientation='vertical', size_hint_y=None, spacing=4)
        self.list_box.bind(minimum_height=self.list_box.setter('height'))
        scroll = ScrollView()
        scroll.add_widget(self.list_box)
        root.add_widget(scroll)

        add_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=5)
        self.time_input = TextInput(
            text="0700",
            multiline=False,
            input_filter='int',
            hint_text="ЧЧММ",
            size_hint_x=0.3
        )
        add_row.add_widget(self.time_input)
        b1 = Button(text="+ Мобильный", size_hint_x=0.35)
        b1.bind(on_press=self.add_mobile)
        add_row.add_widget(b1)
        b2 = Button(text="+ Wi-Fi", size_hint_x=0.35)
        b2.bind(on_press=self.add_wifi)
        add_row.add_widget(b2)
        root.add_widget(add_row)

        bsave = Button(text="СОХРАНИТЬ", size_hint_y=None, height=50)
        bsave.bind(on_press=self.save_all)
        root.add_widget(bsave)

        btm = Button(text="Тест: МОБИЛЬНЫЙ", size_hint_y=None, height=50)
        btm.bind(on_press=lambda x: Thread(target=switch_to_mobile).start())
        root.add_widget(btm)

        btw = Button(text="Тест: WI-FI", size_hint_y=None, height=50)
        btw.bind(on_press=lambda x: Thread(target=switch_to_wifi).start())
        root.add_widget(btw)

        self.refresh_list()
        Scheduler(self).start()
        return root

    def refresh_list(self):
        self.list_box.clear_widgets()
        for t, action in sorted(self.records, key=lambda r: r[0]):
            self.list_box.add_widget(ScheduleItem(t, action, self.delete_record))

    def delete_record(self, t, action):
        self.records = [r for r in self.records if r != (t, action)]
        self.refresh_list()
        save_schedule(self.records, self.schedule_enabled)

    def on_enabled(self, instance, value):
        self.schedule_enabled = value
        save_schedule(self.records, self.schedule_enabled)

    def _add(self, action):
        norm = normalize_time(self.time_input.text)
        if norm is None:
            log("Некорректное время: %s" % self.time_input.text)
            return
        if len(self.records) >= 12:
            log("Слишком много записей")
            return
        self.records.append((norm, action))
        self.time_input.text = ""
        self.refresh_list()
        save_schedule(self.records, self.schedule_enabled)

    def add_mobile(self, *args):
        self._add("mobile")

    def add_wifi(self, *args):
        self._add("wifi")

    def save_all(self, *args):
        save_schedule(self.records, self.schedule_enabled)
        log("SAVED: %s enabled=%s" % (self.records, self.schedule_enabled))


if __name__ == '__main__':
    AccSwitcherApp().run()
