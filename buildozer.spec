[app]
title = CryptoApp
package.name = cryptoapp
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy

# Icon and splash screen (optional)
# icon.filename = %(source.dir)s/icon.png

# Supported platforms
orientation = portrait

# OSX / iOS / Android specific sections
osx.kivy_version = 2.3.0

# Android specific configurations
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_path = 
android.sdk = 33
android.build_tools_version = 33.0.2
android.cmdline_tools_version = 11.0
android.accept_sdk_license = True
android.skip_update = False
android.permissions = INTERNET, ACCESS_NETWORK_STATE

# Build options
p4a.branch = develop

[buildozer]
log_level = 2
warn_on_root = 1
