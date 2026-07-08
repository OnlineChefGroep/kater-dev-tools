## 2025-05-15 - [ARIA Tabs Implementation]
**Learning:** Implementing the WAI-ARIA Tabs pattern (role="tablist", role="tab", role="tabpanel") significantly improves keyboard navigation and screen reader support for single-page dashboard interfaces. It provides a standard way for users to understand and interact with navigable sections.
**Action:** Always use the full WAI-ARIA Tabs pattern when building tabbed interfaces to ensure accessibility standards are met.

## 2026-07-08 - [Dynamic ARIA Labels for State Transitions]
**Learning:** Tunnel control buttons and dynamic switches require state-aware ARIA labels (e.g., 'Start', 'Starting', 'Stop') to clearly communicate both current status and active transitions to screen reader users. Standard text updates alone are often insufficient for accessibility if the element's purpose or state changes.
**Action:** Implement dynamic `aria-label` updates within the JavaScript state management logic for any interactive element that undergoes a multi-stage transition.
