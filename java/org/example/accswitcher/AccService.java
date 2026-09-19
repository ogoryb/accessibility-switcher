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
        if (instance == null) {
            Log.e(TAG, "openQuickSettings: instance null");
            return false;
        }
        boolean r = instance.performGlobalAction(GLOBAL_ACTION_QUICK_SETTINGS);
        Log.d(TAG, "openQuickSettings -> " + r);
        return r;
    }

    public static int getStateByText(String text) {
        if (instance == null) {
            Log.e(TAG, "getState: instance null");
            return -1;
        }
        AccessibilityNodeInfo root = instance.getRootInActiveWindow();
        if (root == null) {
            Log.e(TAG, "getState " + text + ": root null");
            return -1;
        }
        AccessibilityNodeInfo node = findNode(root, text);
        if (node == null) {
            Log.d(TAG, "getState " + text + ": not found");
            return -1;
        }
        AccessibilityNodeInfo checkable = node;
        while (checkable != null && !checkable.isCheckable()) {
            checkable = checkable.getParent();
        }
        if (checkable == null) {
            Log.d(TAG, "getState " + text + ": no checkable parent");
            return -1;
        }
        int state = checkable.isChecked() ? 1 : 0;
        Log.d(TAG, "getState " + text + " -> " + state);
        return state;
    }

    public static boolean clickByText(String text) {
        if (text == null) {
            Log.e(TAG, "click: text null");
            return false;
        }
        if (instance == null) {
            Log.e(TAG, "click " + text + ": instance null");
            return false;
        }
        AccessibilityNodeInfo root = instance.getRootInActiveWindow();
        if (root == null) {
            Log.e(TAG, "click " + text + ": root null");
            return false;
        }
        boolean r = findAndClick(root, text);
        Log.d(TAG, "click " + text + " -> " + r);
        return r;
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

    private static boolean findAndClick(AccessibilityNodeInfo node, String text) {
        if (node == null || text == null) return false;
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
        return clickable.performAction(AccessibilityNodeInfo.ACTION_CLICK);
    }
}
