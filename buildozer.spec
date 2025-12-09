[app]
# (str) Title of your application
title = Forest Fighter 2

# (str) Package name
package.name = forestfighter2

# (str) Package domain (needed for android/ios packaging)
package.domain = org.fightinggame

# (str) Source code where the main.py live
source.dir = .

# (str) Application entry point (now main.py is the Kivy mobile version)
source.main = main.py

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ogg,wav,mp3,ttf,otf

# (list) List of inclusions using pattern matching
source.include_patterns = assets/*,assets/**/*,screens/*,components/*,utils/*

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_patterns = 

# (list) List of directory to exclude (let empty to not exclude anything)
source.exclude_dirs = tests, bin, venv, __pycache__, web, .github, .git, buildozer_venv, buildozer_venv2, buildozer_env, .buildozer

# (str) Application versioning
version = 1.0

# (list) Application requirements
# Using latest pyjnius from github master for Python 3.11 compatibility (fixes 'long' issue)
requirements = python3,kivy,pillow,https://github.com/kivy/pyjnius/archive/master.zip

# (str) Custom source folders for requirements
#requirements.source.kivy = ../../kivy

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (one of landscape, portrait, all or auto)
orientation = landscape

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 31

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Accept SDK license automatically
android.accept_sdk_license = True

# (str) Android SDK dir (if empty, will be automatically downloaded)
android.sdk_path = .buildozer/android/platform/android-sdk

# (str) Android NDK dir (if empty, will be automatically downloaded)
android.ndk_path = .buildozer/android/platform/android-ndk-r25b

# (str) python-for-android branch to use, defaults to master
#p4a.branch = master

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (str) Android entry point, default is ok for Kivy-based app
#android.entrypoint = org.kivy.android.PythonActivity

# (str) Full name including package path of the Java class that implements Android Activity
#android.activity_class_name = org.kivy.android.PythonActivity

# (list) Android application meta-data to set (key=value format)
#android.meta_data =

# (list) Android library project to add (will be added in the project.properties automatically.)
#android.library_references =

# (list) Android shared libraries which will be added to AndroidManifest.xml using <uses-library> tag
#android.uses_library =

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (bool) Android logcat only display log for activity's pid
android.logcat_pid_only = False

# (str) Android additional adb arguments
#android.adb_args = -H host.docker.internal

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (str) The format used to package the app for release mode (aab or apk or aar).
android.release_artifact = apk

# (str) The format used to package the app for debug mode (apk or aar).
android.debug_artifact = apk

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab, .ipa) storage
bin_dir = ./bin
