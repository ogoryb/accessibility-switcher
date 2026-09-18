#!/bin/bash

cd /home/user/hostcwd

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
