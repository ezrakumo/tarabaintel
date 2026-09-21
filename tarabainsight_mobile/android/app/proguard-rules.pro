# ✅ FLUTTER WRAPPER (Prevents app from crashing)
-keep class io.flutter.app.** { *; }
-keep class io.flutter.plugin.** { *; }
-keep class io.flutter.util.** { *; }
-keep class io.flutter.view.** { *; }
-keep class io.flutter.** { *; }
-keep class io.flutter.plugins.** { *; }

# ✅ MAGIC FIX: IGNORE MISSING PLAY CORE CLASSES (Deferred Components)
-dontwarn com.google.android.play.core.**
-keep class com.google.android.play.core.** { *; }

# ✅ SECURE STORAGE (Prevents encryption keys from being scrambled)
-keep class com.it_nomads.fluttersecurestorage.** { *; }

# ✅ HTTP CLIENT & NETWORKING
-keep class io.netty.** { *; }
-keep class org.codehaus.** { *; }

# ✅ REMOVE DEBUG LOGS IN RELEASE (Prevents data leakage)
-assumenosideeffects class android.util.Log {
    public static *** d(...);
    public static *** v(...);
    public static *** i(...);
}