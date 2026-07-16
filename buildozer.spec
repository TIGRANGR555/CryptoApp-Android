[app]
title = CryptoApp
package.name = cryptoapp
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3==3.11.9,hostpython3==3.11.9,kivy,requests,urllib3,chardet,idna,certifi

orientation = portrait
fullscreen = 0
android.api = 34
android.minapi = 24
android.build_tools_version = 34.0.0
android.ndk_api = 24
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 0
buildozer.num_workers = 1
