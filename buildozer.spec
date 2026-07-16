[app]
title = CryptoApp
package.name = cryptoapp
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 0
buildozer.num_workers = 1

# --- Applied Build Bug Fixes ---
requirements = python3,kivy
android.permissions = INTERNET, ACCESS_NETWORK_STATE
android.accept_sdk_license = True
android.skip_update = False
p4a.branch = develop

# --- Pinning Stable SDK and Build Tools ---
android.api = 34
android.minapi = 21
android.build_tools_version = 34.0.0
