import { defineStore } from 'pinia'
import { ref, type Ref } from 'vue'

import { api } from 'src/boot/axios'
import type {
  FeedActivityItem,
  SocialFeedResponse,
  Recommendation,
  RecommendationInboxResponse,
  RecommendationSentResponse,
  Discussion,
  DiscussionListResponse,
  DiscussionReply,
  DiscussionReplyListResponse,
  DiscussionCreateRequest,
  DiscussionReplyCreateRequest,
} from 'src/types/social'

export const useSocialStore = defineStore('social', () => {
  // --- Feed state ---
  const feedItems = ref<FeedActivityItem[]>([]) as Ref<FeedActivityItem[]>
  const feedIsLoading = ref(false)
  const feedError = ref<string | null>(null)
  const feedTotal = ref(0)
  const feedOffset = ref(0)
  const feedHasMore = ref(true)

  // --- Recs state ---
  const inboxItems = ref<Recommendation[]>([]) as Ref<Recommendation[]>
  const inboxIsLoading = ref(false)
  const inboxError = ref<string | null>(null)
  const inboxTotal = ref(0)
  const inboxOffset = ref(0)
  const inboxHasMore = ref(true)

  const sentItems = ref<Recommendation[]>([]) as Ref<Recommendation[]>
  const sentIsLoading = ref(false)
  const sentError = ref<string | null>(null)
  const sentTotal = ref(0)
  const sentOffset = ref(0)
  const sentHasMore = ref(true)

  // --- Discussion state ---
  const discussions = ref<Discussion[]>([]) as Ref<Discussion[]>
  const discussionsIsLoading = ref(false)
  const discussionsError = ref<string | null>(null)
  const discussionsTotal = ref(0)
  const discussionsOffset = ref(0)
  const discussionsHasMore = ref(true)

  const currentDiscussion = ref<Discussion | null>(null)
  const replies = ref<DiscussionReply[]>([]) as Ref<DiscussionReply[]>
  const repliesIsLoading = ref(false)
  const repliesError = ref<string | null>(null)
  const repliesTotal = ref(0)
  const repliesOffset = ref(0)
  const repliesHasMore = ref(true)

  // --- Action state ---
  const acknowledgeStatus = ref<Record<string, 'idle' | 'loading' | 'error' | 'success'>>({})
  const replyActionStatus = ref<'idle' | 'loading' | 'error' | 'success'>('idle')
  const createDiscussionStatus = ref<'idle' | 'loading' | 'error' | 'success'>('idle')

  // ===== Feed actions =====

  async function fetchFeed(limit = 50, offset = 0): Promise<void> {
    if (feedIsLoading.value || (!feedHasMore.value && offset > 0)) return
    feedIsLoading.value = true
    feedError.value = null
    try {
      const { data } = await api.get<SocialFeedResponse>('/api/v1/social/feed', { params: { limit, offset } })
      if (offset === 0) {
        feedItems.value = data.items
      } else {
        feedItems.value = [...feedItems.value, ...data.items]
      }
      feedTotal.value = data.total
      feedOffset.value = offset + data.items.length
      feedHasMore.value = feedItems.value.length < data.total
    } catch (e) {
      feedError.value = e instanceof Error ? e.message : 'Failed to load feed'
    } finally {
      feedIsLoading.value = false
    }
  }

  function resetFeed(): void {
    feedItems.value = []
    feedOffset.value = 0
    feedTotal.value = 0
    feedHasMore.value = true
    feedError.value = null
  }

  // ===== Recommendation actions =====

  async function fetchInbox(limit = 50, offset = 0, includeAcknowledged = true): Promise<void> {
    if (inboxIsLoading.value || (!inboxHasMore.value && offset > 0)) return
    inboxIsLoading.value = true
    inboxError.value = null
    try {
      const { data } = await api.get<RecommendationInboxResponse>('/api/v1/social/recommendations/inbox', {
        params: { limit, offset, include_acknowledged: includeAcknowledged },
      })
      if (offset === 0) {
        inboxItems.value = data.items
      } else {
        inboxItems.value = [...inboxItems.value, ...data.items]
      }
      inboxTotal.value = data.total
      inboxOffset.value = offset + data.items.length
      inboxHasMore.value = inboxItems.value.length < data.total
    } catch (e) {
      inboxError.value = e instanceof Error ? e.message : 'Failed to load inbox'
    } finally {
      inboxIsLoading.value = false
    }
  }

  function resetInbox(): void {
    inboxItems.value = []
    inboxOffset.value = 0
    inboxTotal.value = 0
    inboxHasMore.value = true
    inboxError.value = null
  }

  async function fetchSent(limit = 50, offset = 0): Promise<void> {
    if (sentIsLoading.value || (!sentHasMore.value && offset > 0)) return
    sentIsLoading.value = true
    sentError.value = null
    try {
      const { data } = await api.get<RecommendationSentResponse>('/api/v1/social/recommendations/sent', {
        params: { limit, offset },
      })
      if (offset === 0) {
        sentItems.value = data.items
      } else {
        sentItems.value = [...sentItems.value, ...data.items]
      }
      sentTotal.value = data.total
      sentOffset.value = offset + data.items.length
      sentHasMore.value = sentItems.value.length < data.total
    } catch (e) {
      sentError.value = e instanceof Error ? e.message : 'Failed to load sent recommendations'
    } finally {
      sentIsLoading.value = false
    }
  }

  function resetSent(): void {
    sentItems.value = []
    sentOffset.value = 0
    sentTotal.value = 0
    sentHasMore.value = true
    sentError.value = null
  }

  async function acknowledgeRecommendation(id: string): Promise<boolean> {
    acknowledgeStatus.value[id] = 'loading'
    try {
      await api.patch(`/api/v1/social/recommendations/${id}/acknowledge`)
      acknowledgeStatus.value[id] = 'success'
      // Update local state
      const idx = inboxItems.value.findIndex((r) => r.id === id)
      if (idx !== -1) {
        inboxItems.value[idx].is_acknowledged = true
        inboxItems.value[idx].acknowledged_at = new Date().toISOString()
      }
      return true
    } catch {
      acknowledgeStatus.value[id] = 'error'
      return false
    }
  }

  // ===== Discussion actions =====

  async function fetchDiscussions(mediaId: string, limit = 50, offset = 0): Promise<void> {
    if (discussionsIsLoading.value || (!discussionsHasMore.value && offset > 0)) return
    discussionsIsLoading.value = true
    discussionsError.value = null
    try {
      const { data } = await api.get<DiscussionListResponse>(`/api/v1/social/discussions/${mediaId}`, {
        params: { limit, offset },
      })
      if (offset === 0) {
        discussions.value = data.items
      } else {
        discussions.value = [...discussions.value, ...data.items]
      }
      discussionsTotal.value = data.total
      discussionsOffset.value = offset + data.items.length
      discussionsHasMore.value = discussions.value.length < data.total
    } catch (e) {
      discussionsError.value = e instanceof Error ? e.message : 'Failed to load discussions'
    } finally {
      discussionsIsLoading.value = false
    }
  }

  function resetDiscussions(): void {
    discussions.value = []
    discussionsOffset.value = 0
    discussionsTotal.value = 0
    discussionsHasMore.value = true
    discussionsError.value = null
  }

  async function fetchDiscussionReplies(discussionId: string, limit = 50, offset = 0): Promise<void> {
    if (repliesIsLoading.value || (!repliesHasMore.value && offset > 0)) return
    repliesIsLoading.value = true
    repliesError.value = null
    try {
      const { data } = await api.get<DiscussionReplyListResponse>(
        `/api/v1/social/discussions/${discussionId}/replies`,
        { params: { limit, offset } },
      )
      if (offset === 0) {
        replies.value = data.items
      } else {
        replies.value = [...replies.value, ...data.items]
      }
      repliesTotal.value = data.total
      repliesOffset.value = offset + data.items.length
      repliesHasMore.value = replies.value.length < data.total
    } catch (e) {
      repliesError.value = e instanceof Error ? e.message : 'Failed to load replies'
    } finally {
      repliesIsLoading.value = false
    }
  }

  function resetReplies(): void {
    replies.value = []
    repliesOffset.value = 0
    repliesTotal.value = 0
    repliesHasMore.value = true
    repliesError.value = null
  }

  async function createDiscussionReply(
    discussionId: string,
    payload: DiscussionReplyCreateRequest,
  ): Promise<boolean> {
    replyActionStatus.value = 'loading'
    try {
      await api.post(`/api/v1/social/discussions/${discussionId}/replies`, payload)
      replyActionStatus.value = 'success'
      // Refresh replies after creating one
      await fetchDiscussionReplies(discussionId, 50, 0)
      return true
    } catch {
      replyActionStatus.value = 'error'
      return false
    } finally {
      replyActionStatus.value = 'idle'
    }
  }

  async function createDiscussion(payload: DiscussionCreateRequest): Promise<Discussion | null> {
    createDiscussionStatus.value = 'loading'
    try {
      const { data } = await api.post<Discussion>('/api/v1/social/discussions', payload)
      createDiscussionStatus.value = 'success'
      return data
    } catch {
      createDiscussionStatus.value = 'error'
      return null
    } finally {
      createDiscussionStatus.value = 'idle'
    }
  }

  return {
    // Feed
    feedItems,
    feedIsLoading,
    feedError,
    feedTotal,
    feedOffset,
    feedHasMore,
    fetchFeed,
    resetFeed,
    // Inbox
    inboxItems,
    inboxIsLoading,
    inboxError,
    inboxTotal,
    inboxOffset,
    inboxHasMore,
    fetchInbox,
    resetInbox,
    // Sent
    sentItems,
    sentIsLoading,
    sentError,
    sentTotal,
    sentOffset,
    sentHasMore,
    fetchSent,
    resetSent,
    acknowledgeRecommendation,
    acknowledgeStatus,
    // Discussions
    discussions,
    discussionsIsLoading,
    discussionsError,
    discussionsTotal,
    discussionsOffset,
    discussionsHasMore,
    fetchDiscussions,
    resetDiscussions,
    // Replies
    currentDiscussion,
    replies,
    repliesIsLoading,
    repliesError,
    repliesTotal,
    repliesOffset,
    repliesHasMore,
    fetchDiscussionReplies,
    resetReplies,
    createDiscussionReply,
    replyActionStatus,
    createDiscussionStatus,
    createDiscussion,
  }
})
