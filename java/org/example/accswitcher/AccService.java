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
        Log.d(TAG, "Accessibility Service connected");
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

    public static boolean clickByText(String text) {
        if (instance == null) {
            Log.e(TAG, "Service not connected");
            return false;
        }
        AccessibilityNodeInfo root = instance.getRootInActiveWindow();
        if (root == null) {
            Log.e(TAG, "Root window is null");
            return false;
        }
        return findAndClick(root, text);
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
