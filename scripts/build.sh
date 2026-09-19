#!/bin/bash

cd /home/user/hostcwd
rm -rf .buildozer

SERVICE_XML='<service android:name="org.example.accswitcher.AccService" android:permission="android.permission.BIND_ACCESSIBILITY_SERVICE" android:exported="true"><intent-filter><action android:name="android.accessibilityservice.AccessibilityService" /></intent-filter><meta-data android:name="android.accessibilityservice" android:resource="@xml/accessibility_service_config" /></service>'

echo "=========================================="
echo "PASS 1: скачиваем SDK, NDK и создаём шаблон манифеста"
echo "=========================================="
echo y | buildozer android debug || true

echo "=========================================="
echo "Принимаем лицензии Android SDK"
echo "=========================================="
SDKMANAGER=/root/.buildozer/android/platform/android-sdk/tools/bin/sdkmanager
if [ -f "$SDKMANAGER" ]; then
  yes | "$SDKMANAGER" --sdk_root=/root/.buildozer/android/platform/android-sdk --licenses || true
fi

echo "=========================================="
echo "Патчим шаблоны и манифесты p4a, добавляя наш сервис"
echo "=========================================="
find .buildozer -name "AndroidManifest.tmpl.xml" -o -name "AndroidManifest.xml" | while read f; do
  if ! grep -q "AccService" "$f"; then
    sed -i "s|</application>|${SERVICE_XML}</application>|" "$f"
    echo "Патч применён: $f"
  fi
done

echo "=========================================="
echo "PASS 2: сборка APK"
echo "=========================================="
echo y | buildozer android debug
