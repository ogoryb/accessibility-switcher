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

    public static boolean openQuickSettings() {
        if (instance == null) return false;
        boolean r = instance.performGlobalAction(GLOBAL_ACTION_QUICK_SETTINGS);
        Log.d(TAG, "openQuickSettings -> " + r);
        return r;
    }

    public static boolean hasText(String text) {
        if (text == null || instance == null) return false;
        AccessibilityNodeInfo root = instance.getRootInActiveWindow();
        if (root == null) return false;
        boolean found = findNode(root, text) != null;
        Log.d(TAG, "hasText " + text + " -> " + found);
        return found;
    }

    public static boolean clickByText(String text) {
        if (text == null || instance == null) return false;
        AccessibilityNodeInfo root = instance.getRootInActiveWindow();
        if (root == null) {
            Log.e(TAG, "click " + text + ": root null");
            return false;
        }
        AccessibilityNodeInfo node = findNode(root, text);
        if (node == null) {
            Log.d(TAG, "click " + text + ": not found");
            return false;
        }
        // кликаем сам узел или его кликабельного предка
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

    private static AccessibilityNodeInfo findNode(AccessibilityNodeInfo node, String text) {
        if (node == null || text == null) return null;
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
}
