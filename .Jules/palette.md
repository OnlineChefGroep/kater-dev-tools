## 2026-06-28 - [ARIA Tabs Pattern implementation]
**Learning:** Modern developer tool dashboards often rely on simple button lists for navigation, which can be difficult for screen reader users to navigate efficiently. Implementing the WAI-ARIA Tabs pattern significantly improves the semantic structure and keyboard navigation of the interface.
**Action:** Always implement `role="tablist"`, `role="tab"`, and `role="tabpanel"` when building multi-view dashboards. Ensure `aria-selected` and `aria-controls` are dynamically managed.

## 2026-06-28 - [Visual Feedback for Copy-to-Clipboard]
**Learning:** Toast notifications are great, but immediate in-place visual feedback (like changing a button's label) provides a more direct confirmation of a successful micro-interaction. It's important to guard against rapid double-clicks to prevent the UI state from getting stuck.
**Action:** Use temporary text changes for actionable elements and include logic to avoid state collisions during the "revert" timeout.
