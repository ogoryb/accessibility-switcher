package org.example.accswitcher;

import android.accessibilityservice.AccessibilityService;
import android.app.KeyguardManager;
import android.content.Context;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;
import android.util.Log;

public class AccService extends AccessibilityService {
    private static final String TAG = "AccService";
    private static AccService instance;

    @Override
    public void onServiceConnected() {
        super.onServiceConnected();
        instance = this;
        Log.d(TAG, "Service connected");
    }

    @Override
    public void onAccessibilityEvent(AccessibilityEvent event) {}

    @Override
    public void onInterrupt() {}

    @Override
    public void onDestroy() {
        instance = null;
        Log.d(TAG, "Service destroyed");
        super.onDestroy();
    }

    public static void log(String msg) {
        Log.d(TAG, "PY: " + msg);
    }

    public static boolean isConnected() {
        return instance != null;
    }

    // Разблокирован ли экран (PIN введён)
    public static boolean isScreenUnlocked() {
        if (instance == null) return false;
        try {
            KeyguardManager km = (KeyguardManager)
                instance.getSystemService(Context.KEYGUARD_SERVICE);
            if (km == null) return false;
            boolean locked = km.isKeyguardLocked();
            Log.d(TAG, "isScreenUnlocked -> " + (!locked));
            return !locked;
        } catch (Exception e) {
            Log.e(TAG, "isScreenUnlocked error: " + e);
            return false;
        }
    }

    public static void closePanel() {
        if (instance == null) {
            Log.e(TAG, "closePanel: instance null");
            return;
        }
        Log.d(TAG, "closePanel: pressing BACK");
        instance.performGlobalAction(GLOBAL_ACTION_BACK);
        try {
            Thread.sleep(700);
        } catch (InterruptedException e) {}
        Log.d(TAG, "closePanel: pressing BACK again");
        instance.performGlobalAction(GLOBAL_ACTION_BACK);
    }

    public static boolean openQuickSettings() {
        if (instance == null) {
            Log.e(TAG, "openQuickSettings: instance null");
            return false;
        }
        boolean r = instance.performGlobalAction(GLOBAL_ACTION_QUICK_SETTINGS);
        Log.d(TAG, "openQuickSettings -> " + r);
        return r;
    }

    public static boolean clickByPrefix(String prefix) {
        if (prefix == null || instance == null) return false;
        AccessibilityNodeInfo root = instance.getRootInActiveWindow();
        if (root == null) return false;
        AccessibilityNodeInfo node = findNodePrefix(root, prefix);
        if (node == null) {
            Log.d(TAG, "prefix " + prefix + ": not found");
            return false;
        }
        return performClick(node, "prefix " + prefix);
    }

    public static boolean clickBySubstring(String sub) {
        if (sub == null || instance == null) return false;
        AccessibilityNodeInfo root = instance.getRootInActiveWindow();
        if (root == null) return false;
        AccessibilityNodeInfo node = findNodeSubstring(root, sub);
        if (node == null) {
            Log.d(TAG, "sub " + sub + ": not found");
            return false;
        }
        return performClick(node, "sub " + sub);
    }

    public static boolean clickByExact(String text) {
        if (text == null || instance == null) return false;
        AccessibilityNodeInfo root = instance.getRootInActiveWindow();
        if (root == null) return false;
        AccessibilityNodeInfo node = findNodeExact(root, text);
        if (node == null) {
            Log.d(TAG, "exact " + text + ": not found");
            return false;
        }
        return performClick(node, "exact " + text);
    }

    private static boolean performClick(AccessibilityNodeInfo node, String tag) {
        AccessibilityNodeInfo clickable = node;
        while (clickable != null && !clickable.isClickable()) {
            clickable = clickable.getParent();
        }
        if (clickable != null) {
            boolean r = clickable.performAction(AccessibilityNodeInfo.ACTION_CLICK);
            Log.d(TAG, "click " + tag + " ancestor -> " + r);
            if (r) return true;
        }
        boolean r2 = node.performAction(AccessibilityNodeInfo.ACTION_CLICK);
        Log.d(TAG, "click " + tag + " self -> " + r2);
        return r2;
    }

    private static AccessibilityNodeInfo findNodePrefix(AccessibilityNodeInfo node, String prefix) {
        if (node == null) return null;
        CharSequence t = node.getText();
        if (t != null && t.toString().startsWith(prefix)) return node;
        CharSequence d = node.getContentDescription();
        if (d != null && d.toString().startsWith(prefix)) return node;
        for (int i = 0; i < node.getChildCount(); i++) {
            AccessibilityNodeInfo c = node.getChild(i);
            if (c != null) {
                AccessibilityNodeInfo f = findNodePrefix(c, prefix);
                if (f != null) return f;
            }
        }
        return null;
    }

    private static AccessibilityNodeInfo findNodeSubstring(AccessibilityNodeInfo node, String sub) {
        if (node == null) return null;
        CharSequence t = node.getText();
        if (t != null && t.toString().contains(sub)) return node;
        CharSequence d = node.getContentDescription();
        if (d != null && d.toString().contains(sub)) return node;
        for (int i = 0; i < node.getChildCount(); i++) {
            AccessibilityNodeInfo c = node.getChild(i);
            if (c != null) {
                AccessibilityNodeInfo f = findNodeSubstring(c, sub);
                if (f != null) return f;
            }
        }
        return null;
    }

    private static AccessibilityNodeInfo findNodeExact(AccessibilityNodeInfo node, String text) {
        if (node == null) return null;
        CharSequence t = node.getText();
        if (t != null && t.toString().equals(text)) return node;
        CharSequence d = node.getContentDescription();
        if (d != null && d.toString().equals(text)) return node;
        for (int i = 0; i < node.getChildCount(); i++) {
            AccessibilityNodeInfo c = node.getChild(i);
            if (c != null) {
                AccessibilityNodeInfo f = findNodeExact(c, text);
                if (f != null) return f;
            }
        }
        return null;
    }
}
