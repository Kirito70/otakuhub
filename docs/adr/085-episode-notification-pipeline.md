# ADR 085 — Episode Notification Pipeline (Complete)

**Status**: Proposed
**Date**: 2026-06-08

## Context

The `process_new_episodes_task` in `sync_tasks.py` already queries for recently-aired episodes and chapters, identifies watching/reading users, and creates `Notification` DB rows. However, it is **never scheduled** in the daily refresh composition, and there is **no delivery mechanism** beyond creating DB rows. Users never actually receive notifications.

The complete notification pipeline needs:
1. A scheduled task that runs after daily refresh to detect new episodes
2. An Apprise delivery task that sends user notifications via their configured channels
3. A cleanup task that purges old read notifications

## Current state

```python
# process_new_episodes_task exists but is NOT in:
# 1. daily_refresh_compose
# 2. weekly_refresh_compose
# 3. Celery beat schedule
# 4. Any cron/scheduler
```

## Notification table stores rows → users read via inbox → but nothing pushes them out

## Decision

### 1. Hook `process_new_episodes` into daily refresh

Modify `daily_refresh_compose_task` to append `process_new_episodes_task` after everything else:

```python
# Current:
signatures = [backfill_anilist, mangadex_detail, anikoto_recent, megaplay_verify]

# New:
signatures = [
    backfill_anilist,
    mangadex_detail,
    anikoto_recent,          # if enabled
    megaplay_verify,         # if enabled
    process_new_episodes,    # ← NEW
]
```

### 2. Add `notify_users` task

New task that reads unprocessed notifications and delivers them via Apprise:

```python
@celery_app.task(bind=True, name="sync.notify_users", max_retries=3)
def notify_users_task(self, *, limit: int = 50, dry_run: bool = False) -> dict[str, Any]:
    """Deliver pending notifications to users via their configured channels.

    1. Query notifications where sent_at IS NULL (not yet delivered)
    2. For each user, group notifications by type
    3. Load user's notification_preferences
    4. For each configured channel (discord, telegram, email, push):
       - Call AppriseClient with formatted message
       - Mark notification.sent_at = NOW() on success
    5. On delivery failure, log error but do NOT block (user can still see in inbox)
    """
```

### 3. Add notification cleanup task

```python
@celery_app.task(name="sync.cleanup_notifications")
def cleanup_notifications_task() -> dict[str, Any]:
    """Purge read notifications older than 90 days.

    Uses the existing index `idx_notifications_cleanup` on (created_at) WHERE is_read = TRUE.
    """
```

### 4. Beat schedule updates

Add to Celery beat schedule:

```python
beat_schedule = {
    # Existing...
    "sync-daily-refresh-compose": {
        "task": "sync.daily_refresh_compose",
        "schedule": crontab(hour=1, minute=0),
    },
    # New: notify users after daily refresh completes
    "sync-notify-users": {
        "task": "sync.notify_users",
        "schedule": crontab(hour=2, minute=30),  # 90 min after daily refresh
    },
    # New: weekly notification cleanup
    "sync-cleanup-notifications": {
        "task": "sync.cleanup_notifications",
        "schedule": crontab(hour=3, minute=0, day_of_week=0),  # Sunday 3 AM
    },
}
```

### 5. Apprise client enhancement

The existing `external/apprise_client.py` currently does basic notification. Enhance it to:

```python
class AppriseClient:
    async def send_notification(
        self,
        *,
        user_id: UUID,
        title: str,
        body: str,
        notification_type: NotificationType,
        channels: NotificationChannels,
    ) -> bool:
        """Send a notification to a user via their configured channels.

        channels.discord_webhook → Apprise discord:// URL
        channels.telegram_chat_id → Apprise tgram:// URL
        channels.email_enabled → Apprise mailto:// URL (from user email)
        channels.push_enabled → Apprise pushover:// or similar
        """
```

### 6. Frontend notification badge

The notification icon in the nav bar should show an unread count:

```typescript
// composables/useNotificationBadge.ts
export function useNotificationBadge() {
  const { items, fetchNotifications } = useNotificationsStore()
  const unreadCount = computed(() => items.filter(n => !n.is_read).length)

  // Poll every 60 seconds for fresh count
  let interval: ReturnType<typeof setInterval> | null = null

  function startPolling() {
    fetchNotifications({ limit: 1 }) // just get count
    interval = setInterval(() => fetchNotifications({ limit: 1 }), 60_000)
  }

  function stopPolling() {
    if (interval) clearInterval(interval)
  }

  return { unreadCount, startPolling, stopPolling }
}
```

### 7. Testing contract

- `process_new_episodes_task.test.py`: mock episodes, verify notification creation, verify user matching, verify duplicates are not re-created
- `notify_users_task.test.py`: mock AppriseClient, verify delivery to each channel, verify sent_at is set, verify failure is logged
- `cleanup_notifications_task.test.py`: verify old read notifications are deleted, unread notifications are preserved

## Consequences

**Good**:
- Completes the notification pipeline from detection → delivery → cleanup
- Users receive push notifications for new episodes of shows they're watching
- No changes to frontend notification inbox (already built in Phase 21)

**Bad**:
- Apprise URLs must be configured per-user (Discord webhooks, Telegram chat IDs)
- Email/push delivery requires additional Apprise configuration in deployment
- Notifications for new chapters will only work for manga with chapter data in our DB

**Neutral**:
- Notification preferences UI (Phase 21.3/21.4) already exists for users to configure channels
- Daily refresh now includes notification processing as a dependency step
