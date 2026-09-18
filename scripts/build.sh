#!/bin/bash

cd /home/user/hostcwd

# Создаём папку и файл конфигурации сервиса, встраивая строку напрямую
mkdir -p res/xml

cat > res/xml/accessibility_service_config.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<accessibility-service xmlns:android="http://schemas.android.com/apk/res/android"
    android:description="Переключает Wi-Fi и точку доступа по команде приложения"
    android:accessibilityEventTypes="typeWindowStateChanged|typeWindowContentChanged"
    android:accessibilityFeedbackType="feedbackGeneric"
    android:accessibilityFlags="flagDefault|flagRetrieveInteractiveWindows"
    android:canRetrieveWindowContent="true"
    android:notificationTimeout="100" />
EOF

echo "=========================================="
echo "PASS 1: скачиваем SDK и NDK"
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
echo "PASS 2: сборка APK"
echo "=========================================="
echo y | buildozer android debug
