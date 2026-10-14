package org.example.accswitcher;

import android.accessibilityservice.AccessibilityService;
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

    public static boolean isConnected() {
        return instance != null;
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

    // Проверка: есть ли на экране ТОЧНАЯ надпись (equals)
    public static boolean hasTextExact(String text) {
        if (text == null || instance == null) return false;
        AccessibilityNodeInfo root = instance.getRootInActiveWindow();
        if (root == null) return false;
        boolean found = findNode(root, text, true) != null;
        Log.d(TAG, "hasTextExact " + text + " -> " + found);
        return found;
    }

    // Проверка: есть ли на экране подстрока (contains)
    public static boolean hasText(String text) {
        if (text == null || instance == null) return false;
        AccessibilityNodeInfo root = instance.getRootInActiveWindow();
        if (root == null) return false;
        boolean found = findNode(root, text, false) != null;
        Log.d(TAG, "hasText " + text + " -> " + found);
        return found;
    }

    // Клик по ТОЧНОЙ надписи
    public static boolean clickByTextExact(String text) {
        return clickInternal(text, true);
    }

    // Клик по подстроке
    public static boolean clickByText(String text) {
        return clickInternal(text, false);
    }

    private static boolean clickInternal(String text, boolean exact) {
        if (text == null || instance == null) {
            Log.e(TAG, "click " + text + ": instance null");
            return false;
        }
        AccessibilityNodeInfo root = instance.getRootInActiveWindow();
        if (root == null) {
            Log.e(TAG, "click " + text + ": root null");
            return false;
        }
        AccessibilityNodeInfo node = findNode(root, text, exact);
        if (node == null) {
            Log.d(TAG, "click " + (exact ? "exact " : "") + text + ": not found");
            return false;
        }
        AccessibilityNodeInfo clickable = node;
        while (clickable != null && !clickable.isClickable()) {
            clickable = clickable.getParent();
        }
        if (clickable != null) {
            boolean r = clickable.performAction(AccessibilityNodeInfo.ACTION_CLICK);
            Log.d(TAG, "click ancestor " + text + " -> " + r);
            if (r) return true;
        }
        boolean r2 = node.performAction(AccessibilityNodeInfo.ACTION_CLICK);
        Log.d(TAG, "click self " + text + " -> " + r2);
        return r2;
    }

    // Диагностика: вывести все тексты и описания на экране
    public static void dumpTexts() {
        if (instance == null) {
            Log.d(TAG, "DUMP instance null");
            return;
        }
        AccessibilityNodeInfo root = instance.getRootInActiveWindow();
        if (root == null) {
            Log.d(TAG, "DUMP root null");
            return;
        }
        Log.d(TAG, "DUMP START");
        dumpRecursive(root, 0);
        Log.d(TAG, "DUMP END");
    }

    private static void dumpRecursive(AccessibilityNodeInfo node, int depth) {
        if (node == null) return;
        CharSequence t = node.getText();
        CharSequence d = node.getContentDescription();
        if (t != null || d != null) {
            StringBuilder indent = new StringBuilder();
            for (int i = 0; i < depth; i++) indent.append("  ");
            Log.d(TAG, "DUMP " + indent + "text=[" + t + "] desc=[" + d
                    + "] clickable=" + node.isClickable());
        }
        for (int i = 0; i < node.getChildCount(); i++) {
            dumpRecursive(node.getChild(i), depth + 1);
        }
    }

    private static AccessibilityNodeInfo findNode(AccessibilityNodeInfo node, String text, boolean exact) {
        if (node == null || text == null) return null;
        CharSequence t = node.getText();
        if (t != null) {
            if (exact ? t.toString().equals(text) : t.toString().contains(text)) return node;
        }
        CharSequence d = node.getContentDescription();
        if (d != null) {
            if (exact ? d.toString().equals(text) : d.toString().contains(text)) return node;
        }
        for (int i = 0; i < node.getChildCount(); i++) {
            AccessibilityNodeInfo child = node.getChild(i);
            if (child != null) {
                AccessibilityNodeInfo found = findNode(child, text, exact);
                if (found != null) return found;
            }
        }
        return null;
    }
}
