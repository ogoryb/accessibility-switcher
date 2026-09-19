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
        super.onDestroy();
    }

    public static boolean openQuickSettings() {
        if (instance == null) return false;
        return instance.performGlobalAction(GLOBAL_ACTION_QUICK_SETTINGS);
    }

    public static int getStateByText(String text) {
        if (instance == null) return -1;
        AccessibilityNodeInfo root = instance.getRootInActiveWindow();
        if (root == null) return -1;
        AccessibilityNodeInfo node = findNode(root, text);
        if (node == null) return -1;
        AccessibilityNodeInfo checkable = node;
        while (checkable != null && !checkable.isCheckable()) {
            checkable = checkable.getParent();
        }
        if (checkable == null) return -1;
        return checkable.isChecked() ? 1 : 0;
    }

    public static boolean clickByText(String text) {
        if (instance == null) return false;
        AccessibilityNodeInfo root = instance.getRootInActiveWindow();
        if (root == null) return false;
        return findAndClick(root, text);
    }

    // Диагностика: вывести все тексты и описания в лог
    public static void dumpTexts() {
        if (instance == null) {
            Log.d(TAG, "DUMP instance == null");
            return;
        }
        AccessibilityNodeInfo root = instance.getRootInActiveWindow();
        if (root == null) {
            Log.d(TAG, "DUMP root == null");
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
                    + "] checkable=" + node.isCheckable()
                    + " checked=" + node.isChecked());
        }
        for (int i = 0; i < node.getChildCount(); i++) {
            dumpRecursive(node.getChild(i), depth + 1);
        }
    }

    private static AccessibilityNodeInfo findNode(AccessibilityNodeInfo node, String text) {
        if (node == null) return null;
        CharSequence t = node.getText();
        if (t != null && t.toString().contains(text)) return node;
        CharSequence d = node.getContentDescription();
        if (d != null && d.toString().contains(text)) return node;
        for (int i = 0; i < node.getChildCount(); i++) {
            AccessibilityNodeInfo child = node.getChild(i);
            if (child != null) {
                AccessibilityNodeInfo found = findNode(child, text);
                if (found != null) return found;
            }
        }
        return null;
    }

    private static boolean findAndClick(AccessibilityNodeInfo node, String text) {
        if (node == null) return false;
        CharSequence t = node.getText();
        if (t != null && t.toString().contains(text)) {
            if (performClick(node)) return true;
        }
        CharSequence d = node.getContentDescription();
        if (d != null && d.toString().contains(text)) {
            if (performClick(node)) return true;
        }
        for (int i = 0; i < node.getChildCount(); i++) {
            AccessibilityNodeInfo child = node.getChild(i);
            if (child != null) {
                if (findAndClick(child, text)) return true;
            }
        }
        return false;
    }

    private static boolean performClick(AccessibilityNodeInfo node) {
        AccessibilityNodeInfo clickable = node;
        while (clickable != null && !clickable.isClickable()) {
            clickable = clickable.getParent();
        }
        if (clickable == null) return false;
        boolean result = clickable.performAction(AccessibilityNodeInfo.ACTION_CLICK);
        Log.d(TAG, "Clicked: " + clickable.getText() + " -> " + result);
        return result;
    }
}
