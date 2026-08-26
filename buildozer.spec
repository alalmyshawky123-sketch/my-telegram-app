[app]
title = Telegram Monitor
package.name = telegrammonitor
package.domain = com.telebot
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,requests
orientation = portrait
fullscreen = 0
android.permissions = INTERNET

# إعدادات أندرويد المستقرة لتجنب أخطاء الإصدار 37
android.api = 33
android.minapi = 21
android.sdk = 33
android.accept_sdk_license = True
