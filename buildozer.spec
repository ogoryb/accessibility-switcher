[app]
title = Рисование круга
package.name = circleapp
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0

requirements = python3,kivy

orientation = portrait
fullscreen = 0

# Android specific
android.permissions =
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
# Собираем только одну архитектуру: сборка сразу нескольких (arm64-v8a +
# armeabi-v7a) переиспользует общую временную venv-папку между ними и
# натыкается на известный баг python-for-android (issue #3339 / PR #3360),
# который ломает pip внутри неё. arm64-v8a покрывает подавляющее
# большинство современных Android-устройств.
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
