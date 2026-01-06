# Attack Plan: Optimization Implementation Checklist

This document serves as a living checklist to track the implementation of optimization suggestions for the FaithUp Discord Bot. Each item is categorized by priority, effort, and status.

## Legend

- **Priority**: High, Medium, Low
- **Effort**: Low (hours), Medium (days), High (weeks)
- **Status**: Not Started, In Progress, Completed, Blocked

## Checklist

### 1. API Call Performance

| ID | Suggestion | Priority | Effort | Status | Notes |
|----|------------|----------|--------|--------|-------|
| 1.1 | Reuse HTTP Sessions (YouVersionClient) | High | Low | Completed | Instantiate client once in cog `__init__`. Implemented. |
| 1.2 | Migrate to Async HTTP Requests (aiohttp/httpx) | High | Medium | Not Started | Replace `requests` with async client; requires refactoring of API calls. |
| 1.3 | Add Retry with Exponential Backoff | Medium | Low | Not Started | Use `tenacity` or custom decorator for YouVersion and NVIDIA APIs. |

### 2. Memory Management

| ID | Suggestion | Priority | Effort | Status | Notes |
|----|------------|----------|--------|--------|-------|
| 2.1 | Cache Expiration Cleanup (VOTD cache) | Medium | Low | Not Started | Implement periodic cleanup or LRU eviction. |
| 2.2 | Conversation Inactivity Timeout (AI conversations) | Medium | Low | Not Started | Add last‑activity timestamp and prune old entries. |
| 2.3 | Pre‑compile Regex Patterns | Low | Low | Not Started | Move regex compilation to module level. |

### 3. CPU & Code Efficiency

| ID | Suggestion | Priority | Effort | Status | Notes |
|----|------------|----------|--------|--------|-------|
| 3.1 | Optimize HTML Parsing (lightweight parser) | Low | Medium | Not Started | Evaluate `html.parser` vs regex for verse extraction. |
| 3.2 | Improve Random Key Removal (uniform random) | Low | Low | Not Started | Use `random.choice(list(keys))` or maintain separate list. |
| 3.3 | Precompute Combined Response Lists (bingbong) | Low | Low | Not Started | Compute once in cog `__init__`. |

### 4. Network Optimization

| ID | Suggestion | Priority | Effort | Status | Notes |
|----|------------|----------|--------|--------|-------|
| 4.1 | Connection Pooling (shared session) | High | Low | Not Started | Share a single `requests.Session` across the application. |
| 4.2 | Adjust Timeouts (10s for Discord commands) | Medium | Low | Not Started | Reduce timeout and add fallback to cached response. |
| 4.3 | Use Async OpenAI Client (NVIDIA API) | High | Medium | Not Started | Upgrade `openai` package and use async methods. |

### 5. Logging & Monitoring

| ID | Suggestion | Priority | Effort | Status | Notes |
|----|------------|----------|--------|--------|-------|
| 5.1 | Adjust Log Levels (INFO → DEBUG for commands) | Medium | Low | Not Started | Change log levels in `mycog.py` and other cogs. |
| 5.2 | Implement Structured Logging | Low | Medium | Not Started | Introduce JSON logging for easier monitoring. |
| 5.3 | Add Performance Metrics (response times, cache hits) | Low | Medium | Not Started | Use `prometheus_client` or simple counters. |

### 6. Configuration & Environment

| ID | Suggestion | Priority | Effort | Status | Notes |
|----|------------|----------|--------|--------|-------|
| 6.1 | Validate Environment Variables at Startup | Medium | Low | Not Started | Check required vars in cog `__init__` and log warnings. |
| 6.2 | Hot‑reload Configuration (announcements) | Low | Medium | Not Started | Leverage `redbot.core.config` for dynamic updates. |

### 7. Latency Improvements

| ID | Suggestion | Priority | Effort | Status | Notes |
|----|------------|----------|--------|--------|-------|
| 7.1 | Parallelize API Calls (VOTD + chapter) | Medium | Low | Not Started | Use `asyncio.gather` after migrating to async HTTP. |
| 7.2 | Offload CPU‑intensive Tasks to Thread Pool | Low | Low | Not Started | Use `asyncio.to_thread` for regex parsing. |

### 8. Security & Robustness

| ID | Suggestion | Priority | Effort | Status | Notes |
|----|------------|----------|--------|--------|-------|
| 8.1 | Implement Rate Limiting (AI conversations) | Medium | Low | Not Started | Add per‑user token‑bucket or sliding‑window limit. |
| 8.2 | Sanitize User Input (AI prompt) | Low | Low | Not Started | Truncate length and escape special characters. |

## Implementation Strategy

1. **Phase 1 (Quick Wins)** – Items with High priority and Low effort:
   - 1.1 Reuse HTTP Sessions
   - 4.1 Connection Pooling
   - - 2.3 Pre‑compile Regex Patterns
   - - 5.1 Adjust Log Levels

2. **Phase 2 (Core Async Migration)** – Items with High priority but Medium effort:
   - 1.2 Migrate to Async HTTP Requests
   - 4.3 Use Async OpenAI Client
   - - 7.1 Parallelize API Calls (depends on async migration)

3. **Phase 3 (Enhanced Resilience)** – Medium priority items:
   - 1.3 Retry with Exponential Backoff
   - 2.1 Cache Expiration Cleanup
   - 2.2 Conversation Inactivity Timeout
   - 8.1 Rate Limiting

4. **Phase 4 (Monitoring & Maintenance)** – Remaining items:
   - 5.2 Structured Logging
   - 5.3 Performance Metrics
   - 6.2 Hot‑reload Configuration
   - 3.1 Optimize HTML Parsing (if performance issues observed)

## Tracking Progress

- Update the **Status** column as work progresses.
- Add a **Date Completed** column when marking an item as Completed.
- Use pull requests or commits to link to specific changes.

## Notes

- This plan is flexible; items may be re‑prioritized based on new findings.
- All changes should be tested in a development environment before deploying to production.
- Consider creating a separate branch for each phase to keep changes organized.

---
*Document created: 2026‑01‑06*
*Last updated: 2026‑01‑06*