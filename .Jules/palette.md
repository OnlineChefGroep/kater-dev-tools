## 2025-05-15 - [ARIA Tabs Implementation]
**Learning:** Implementing the WAI-ARIA Tabs pattern (role="tablist", role="tab", role="tabpanel") significantly improves keyboard navigation and screen reader support for single-page dashboard interfaces. It provides a standard way for users to understand and interact with navigable sections.
**Action:** Always use the full WAI-ARIA Tabs pattern when building tabbed interfaces to ensure accessibility standards are met.

## 2025-05-16 - [Empty State Recovery Pattern]
**Learning:** Providing a functional "Clear search" or recovery link in zero-result states significantly improves user experience by offering a clear path back to a valid state. Coupling this with `aria-live` and `aria-describedby` on the result counter ensures that the state change is also accessible to screen reader users.
**Action:** Always include a recovery mechanism (like a "Clear" link) in empty search or filter states, and link it to an accessible counter.
