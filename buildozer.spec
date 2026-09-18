[app]
title = AccSwitcher
package.name = accswitcher
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,xml,java
version = 0.1
requirements = python3,kivy,jnius
orientation = portrait
fullscreen = 0
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.permissions = BIND_ACCESSIBILITY_SERVICE, SYSTEM_ALERT_WINDOW
android.add_src = java
android.extra_manifest_application = %(source.dir)s/manifest_application.xml
android.res_xml = res/xml
android.res_values = res/values
[buildozer]
log_level = 2
