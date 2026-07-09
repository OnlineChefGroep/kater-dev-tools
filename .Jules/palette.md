## 2025-05-15 - [ARIA Tabs Implementation]
**Learning:** Implementing the WAI-ARIA Tabs pattern (role="tablist", role="tab", role="tabpanel") significantly improves keyboard navigation and screen reader support for single-page dashboard interfaces. It provides a standard way for users to understand and interact with navigable sections.
**Action:** Always use the full WAI-ARIA Tabs pattern when building tabbed interfaces to ensure accessibility standards are met.

## 2025-05-22 - [Dynamic ARIA Labels for State Transitions]
**Learning:** For control elements with asynchronous state transitions (like starting/stopping tunnels), static ARIA labels are insufficient. Using dynamic, state-aware `aria-label` attributes (e.g., transitioning from 'Start' to 'Starting...' to 'Stop') provides essential context to screen reader users about both the current status and active background processes.
**Action:** Implement state-aware `aria-label` updates in JavaScript for all asynchronous UI controls to maintain accessibility during state transitions.
