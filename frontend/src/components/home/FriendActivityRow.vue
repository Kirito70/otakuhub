<template>
  <section class="friend-activity-section">
    <div v-if="loading" class="activity-skeleton">
      <div v-for="n in 3" :key="n" class="skeleton-row">
        <div class="skeleton-avatar"></div>
        <div class="skeleton-text">
          <div class="skeleton-line short"></div>
          <div class="skeleton-line"></div>
        </div>
      </div>
    </div>
    <div v-else-if="error" class="activity-error">{{ error }}</div>
    <div v-else-if="items.length === 0" class="activity-error">
      No friend activity yet. Add some friends or watch something!
    </div>
    <div v-else class="activity-list">
      <div
        v-for="item in items"
        :key="item.id"
        class="activity-item"
        @click="$emit('item-click', item.mediaId)"
      >
        <div class="activity-avatar">
          <img
            v-if="item.avatarUrl"
            :src="item.avatarUrl"
            :alt="item.username"
            loading="lazy"
          />
          <div v-else class="avatar-fallback">{{ item.username.charAt(0).toUpperCase() }}</div>
        </div>
        <div class="activity-content">
          <p class="activity-text">
            <strong>{{ item.displayName || item.username }}</strong>
            {{ describeEvent(item) }}
            <span class="activity-media-title">{{ item.mediaTitle }}</span>
          </p>
          <span class="activity-time">{{ relativeTime(item.createdAt) }}</span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import type { FriendActivityItem } from 'src/types/home'

defineProps<{
  items: FriendActivityItem[]
  loading: boolean
  error: string | null
}>()

defineEmits<{
  'item-click': [mediaId: string]
}>()

function describeEvent(item: FriendActivityItem): string {
  switch (item.eventType) {
    case 'status_changed':
      return item.newStatus ? `marked ${item.mediaTitle} as` : 'updated'
    case 'progress_updated':
      return item.newProgress ? `watched up to episode ${item.newProgress} of` : 'updated progress on'
    case 'score_set':
      return 'rated'
    case 'added':
      return 'started tracking'
    case 'removed':
      return 'removed from list'
    default:
      return 'interacted with'
  }
}

function relativeTime(dateStr: string): string {
  try {
    const now = Date.now()
    const then = new Date(dateStr).getTime()
    const diffSeconds = Math.floor((now - then) / 1000)
    if (diffSeconds < 60) return 'just now'
    const diffMinutes = Math.floor(diffSeconds / 60)
    if (diffMinutes < 60) return `${diffMinutes}m ago`
    const diffHours = Math.floor(diffMinutes / 60)
    if (diffHours < 24) return `${diffHours}h ago`
    const diffDays = Math.floor(diffHours / 24)
    if (diffDays < 7) return `${diffDays}d ago`
    return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  } catch {
    return dateStr
  }
}
</script>

<style scoped lang="scss">
@use 'src/css/tokens' as *;

.friend-activity-section {
  .activity-list {
    display: flex;
    flex-direction: column;
    gap: $space-2;
  }

  .activity-item {
    display: flex;
    gap: $space-3;
    padding: $space-3;
    border-radius: $radius-md;
    cursor: pointer;
    transition: background $transition;

    &:hover {
      background: $bg-hover;
    }
  }

  .activity-avatar {
    flex-shrink: 0;
    width: 40px;
    height: 40px;
    border-radius: $radius-full;
    overflow: hidden;
    background: $bg-elevated;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    .avatar-fallback {
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      color: $accent-primary;
      background: rgba($accent-primary, 0.15);
    }
  }

  .activity-content {
    flex: 1;
    min-width: 0;

    .activity-text {
      margin: 0;
      font-size: $font-size-sm;
      color: $text-primary;
      line-height: 1.4;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;

      .activity-media-title {
        color: $accent-primary;
        font-weight: 600;
      }
    }

    .activity-time {
      font-size: $font-size-xs;
      color: $text-muted;
    }
  }

  .activity-error {
    color: $text-muted;
    font-size: $font-size-sm;
    padding: $space-6 0;
    text-align: center;
  }

  // Skeleton styles
  .activity-skeleton {
    display: flex;
    flex-direction: column;
    gap: $space-3;

    .skeleton-row {
      display: flex;
      gap: $space-3;
      padding: $space-3;

      .skeleton-avatar {
        width: 40px;
        height: 40px;
        border-radius: $radius-full;
        background: linear-gradient(90deg, $bg-elevated 25%, $bg-hover 50%, $bg-elevated 75%);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
      }

      .skeleton-text {
        flex: 1;

        .skeleton-line {
          height: 12px;
          background: $bg-elevated;
          border-radius: $radius-sm;
          margin-bottom: 6px;

          &.short {
            width: 60%;
          }
        }
      }
    }
  }
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
