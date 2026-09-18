#!/bin/bash

cd /home/user/hostcwd

# Создаём папки и файлы ресурсов, если их нет
mkdir -p res/xml res/values

cat > res/xml/accessibility_service_config.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<accessibility-service xmlns:android="http://schemas.android.com/apk/res/android"
    android:description="@string/accessibility_service_description"
    android:accessibilityEventTypes="typeWindowStateChanged|typeWindowContentChanged"
    android:accessibilityFeedbackType="feedbackGeneric"
    android:accessibilityFlags="flagDefault|flagRetrieveInteractiveWindows"
    android:canRetrieveWindowContent="true"
    android:notificationTimeout="100" />
EOF

cat > res/values/strings.xml << 'EOF'
<resources>
    <string name="accessibility_service_label">AccSwitcher</string>
    <string name="accessibility_service_description">Переключает Wi-Fi и точку доступа по команде приложения</string>
</resources>
EOF

echo "=========================================="
echo "PASS 1: скачиваем SDK и NDK (упадёт на лицензиях — это ОК)"
echo "=========================================="
echo y | buildozer android debug || true

echo "=========================================="
echo "Принимаем лицензии Android SDK"
echo "=========================================="
SDKMANAGER=/root/.buildozer/android/platform/android-sdk/tools/bin/sdkmanager
if [ -f "$SDKMANAGER" ]; then
  echo "Найден sdkmanager: $SDKMANAGER"
  yes | "$SDKMANAGER" --sdk_root=/root/.buildozer/android/platform/android-sdk --licenses || true
else
  echo "sdkmanager не найден по пути $SDKMANAGER"
  echo "Содержимое /root/.buildozer/android/platform/:"
  ls -la /root/.buildozer/android/platform/ 2>/dev/null || true
  find /root/.buildozer -name sdkmanager 2>/dev/null || true
fi

echo "=========================================="
echo "PASS 2: сборка APK"
echo "=========================================="
echo y | buildozer android debug
