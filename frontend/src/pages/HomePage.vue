<template>
  <q-page class="home-page">
    <!-- Hero / Spotlight Carousel -->
    <section class="section hero-section" v-if="showHero">
      <div class="hero-carousel-wrapper">
        <div
          v-for="(item, idx) in store.spotlight.items"
          :key="item.id"
          class="hero-slide"
          :class="{ active: idx === heroIndex }"
        >
          <div
            class="hero-bg"
            :style="{ backgroundImage: `url(${item.coverImageLarge || item.coverImage})` }"
          >
            <div class="hero-gradient"></div>
            <div class="hero-gradient-right"></div>
          </div>
          <div class="hero-content">
            <h1 class="hero-title">{{ item.title }}</h1>
            <p v-if="item.titleEnglish && item.titleEnglish !== item.title" class="hero-alt-title">
              {{ item.titleEnglish }}
            </p>
            <div class="hero-meta">
              <span class="hero-tag tag-type">{{ item.mediaType }}</span>
              <span v-if="item.format" class="hero-tag">{{ item.format }}</span>
              <span v-if="item.score" class="hero-score">
                <ScoreRing :score="item.score" :size="36" :show-label="true" />
              </span>
            </div>
            <p v-if="item.synopsis" class="hero-synopsis">{{ truncate(item.synopsis, 200) }}</p>
            <div class="hero-actions">
              <button class="btn-primary" @click="goToMedia(item.id)">
                ▶ Watch Now
              </button>
              <button class="btn-secondary" @click="goToMedia(item.id)">
                + Details
              </button>
            </div>
          </div>
        </div>
        <!-- Dots navigation -->
        <div v-if="store.spotlight.items.length > 1" class="hero-dots">
          <button
            v-for="(item, idx) in store.spotlight.items"
            :key="item.id"
            class="hero-dot"
            :class="{ active: idx === heroIndex }"
            @click="heroIndex = idx"
          ></button>
        </div>
      </div>
    </section>

    <div class="home-content">
      <!-- Continue Watching -->
      <section class="section" v-if="showContinueWatching">
        <SectionHeader title="Continue Watching">
          <template #actions>
            <button class="see-all-btn" @click="goToList">See All</button>
          </template>
        </SectionHeader>
        <div class="carousel-horizontal">
          <AnimeCard
            v-for="item in store.continueWatching.items"
            :key="item.id"
            :id="item.id"
            :title="item.title"
            :coverImage="item.coverImage"
            :mediaType="item.mediaType"
            :format="item.format"
            :score="item.score"
            :year="item.year"
            :episodeCount="item.episodeCount"
            :status="item.status"
            :progress="item.progress"
            :totalEpisodes="item.totalEpisodes"
            :isNew="false"
            @click="goToMedia(item.id)"
          />
        </div>
      </section>

      <!-- Trending Now -->
      <section class="section">
        <SectionHeader title="Trending Now" />
        <TrendingCarousel
          :items="store.trending.items"
          :loading="store.trending.isLoading"
          :error="store.trending.error"
          @item-click="goToMedia"
          @retry="store.fetchTrending()"
        />
      </section>

      <!-- Recently Updated -->
      <section class="section" v-if="showRecentUpdates">
        <SectionHeader title="Recently Updated" />
        <TrendingCarousel
          :items="store.recentUpdates.items"
          :loading="store.recentUpdates.isLoading"
          :error="store.recentUpdates.error"
          title=""
          @item-click="goToMedia"
          @retry="store.fetchRecentUpdates()"
        />
      </section>

      <!-- New Releases -->
      <section class="section">
        <SectionHeader title="New Releases" />
        <AnimeGrid
          :items="store.newReleases.items"
          :loading="store.newReleases.isLoading"
          :error="store.newReleases.error"
          title=""
          empty-message="No new releases available."
          :columns="{ default: 2, sm: 3, md: 4, lg: 4 }"
          @item-click="goToMedia"
          @retry="store.fetchNewReleases()"
        />
      </section>

      <!-- Friends Activity -->
      <section class="section">
        <SectionHeader title="Friends Watching" />
        <FriendActivityRow
          :items="store.friendActivity.items"
          :loading="store.friendActivity.isLoading"
          :error="store.friendActivity.error"
          :activeFilter="store.friendActivityFilter"
          :hasMore="store.friendActivityHasMore"
          :filterLoading="store.friendActivity.isLoading"
          @item-click="goToMedia"
          @filter-change="store.setFriendActivityFilter($event)"
          @load-more="store.loadMoreFriendActivity()"
        />
      </section>

      <!-- Popular Genres -->
      <section class="section">
        <SectionHeader title="Popular Genres" />
        <GenrePills
          :items="store.genres.items"
          :loading="store.genres.isLoading"
          :error="store.genres.error"
          @select="searchByGenre"
        />
      </section>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'

import { useHomeStore } from 'src/stores/home'
import AnimeCard from 'src/components/anime/AnimeCard.vue'
import AnimeGrid from 'src/components/anime/AnimeGrid.vue'
import TrendingCarousel from 'src/components/anime/TrendingCarousel.vue'
import ScoreRing from 'src/components/anime/ScoreRing.vue'
import FriendActivityRow from 'src/components/home/FriendActivityRow.vue'
import GenrePills from 'src/components/home/GenrePills.vue'
import SectionHeader from 'src/components/home/SectionHeader.vue'

const router = useRouter()
const store = useHomeStore()

// Hero carousel state
const heroIndex = ref(0)
let heroTimer: ReturnType<typeof setInterval> | undefined

// Computed visibility for optional sections
const showHero = computed(() => store.spotlight.items.length > 0)
const showContinueWatching = computed(() => store.continueWatching.items.length > 0)
const showRecentUpdates = computed(() => store.recentUpdates.items.length > 0)

// Auto-rotate hero every 6 seconds
function startHeroRotation(): void {
  stopHeroRotation()
  if (store.spotlight.items.length > 1) {
    heroTimer = setInterval(() => {
      heroIndex.value = (heroIndex.value + 1) % store.spotlight.items.length
    }, 6000)
  }
}

function stopHeroRotation(): void {
  if (heroTimer !== undefined) {
    clearInterval(heroTimer)
    heroTimer = undefined
  }
}

function goToMedia(id: string): void {
  router.push({ name: 'media-detail', params: { id } })
}

function searchByGenre(slug: string): void {
  router.push({ name: 'discover', query: { genre: slug } })
}

function goToList(): void {
  router.push('/list')
}

function truncate(text: string, max: number): string {
  if (text.length <= max) return text
  return text.slice(0, max).trimEnd() + '...'
}

onMounted(async () => {
  await store.fetchHome()
  startHeroRotation()
})

onBeforeUnmount(() => {
  stopHeroRotation()
})
</script>

<style scoped lang="scss">
@use 'src/css/tokens' as *;

.home-page {
  background: $bg-primary;
  min-height: 100vh;
}

// ── Hero / Spotlight ─────────────────────────────────────────────────────────

.hero-section {
  margin-bottom: $space-8;
}

.hero-carousel-wrapper {
  position: relative;
  height: 420px;
  overflow: hidden;
  border-radius: $radius-lg;

  @include respond-below(sm) {
    height: 300px;
    border-radius: 0;
    margin: 0 -16px;
  }
}

.hero-slide {
  position: absolute;
  inset: 0;
  opacity: 0;
  transition: opacity 0.8s ease;

  &.active {
    opacity: 1;
  }
}

.hero-bg {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center top;
  background-color: $bg-primary;

  .hero-gradient {
    position: absolute;
    inset: 0;
    background: linear-gradient(to top, $bg-primary 0%, transparent 60%);
  }

  .hero-gradient-right {
    position: absolute;
    inset: 0;
    background: linear-gradient(to right, $bg-primary 0%, transparent 50%);
  }
}

.hero-content {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: $space-8;
  z-index: 2;

  .hero-title {
    font-size: $font-size-2xl;
    font-weight: 800;
    color: $text-primary;
    margin: 0 0 $space-1;
    max-width: 600px;

    @include respond-below(sm) {
      font-size: $font-size-xl;
    }
  }

  .hero-alt-title {
    font-size: $font-size-sm;
    color: $text-muted;
    margin: 0 0 $space-2;
  }

  .hero-meta {
    display: flex;
    align-items: center;
    gap: $space-2;
    margin-bottom: $space-3;

    .hero-tag {
      padding: 2px 8px;
      border-radius: $radius-sm;
      font-size: $font-size-xs;
      font-weight: 600;
      text-transform: uppercase;
      background: rgba(255, 255, 255, 0.1);
      color: $text-secondary;

      &.tag-type {
        color: $accent-primary;
        border: 1px solid $accent-primary;
      }
    }

    .hero-score {
      display: flex;
      align-items: center;
    }
  }

  .hero-synopsis {
    font-size: $font-size-sm;
    color: $text-secondary;
    line-height: 1.5;
    max-width: 500px;
    margin: 0 0 $space-4;
    display: none;

    @include respond-above(sm) {
      display: block;
    }
  }

  .hero-actions {
    display: flex;
    gap: $space-3;
  }
}

.btn-primary {
  padding: $space-2 $space-6;
  border-radius: $radius-md;
  border: none;
  background: $accent-primary;
  color: white;
  font-weight: 700;
  font-size: $font-size-sm;
  cursor: pointer;
  transition: background $transition, transform $transition;

  &:hover {
    background: $accent-glow;
    transform: scale(1.05);
  }
}

.btn-secondary {
  padding: $space-2 $space-6;
  border-radius: $radius-md;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: transparent;
  color: $text-primary;
  font-weight: 600;
  font-size: $font-size-sm;
  cursor: pointer;
  transition: all $transition;

  &:hover {
    border-color: $text-primary;
    background: rgba(255, 255, 255, 0.1);
  }
}

// ── Hero dots ────────────────────────────────────────────────────────────────

.hero-dots {
  position: absolute;
  bottom: $space-4;
  right: $space-8;
  display: flex;
  gap: $space-2;
  z-index: 3;
}

.hero-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.3);
  cursor: pointer;
  transition: background $transition;

  &.active {
    background: $accent-primary;
    box-shadow: 0 0 6px rgba($accent-primary, 0.6);
  }
}

// ── Content sections ─────────────────────────────────────────────────────────

.home-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 $space-6 $space-10;

  @include respond-below(sm) {
    padding: 0 $space-4 $space-8;
  }
}

.section {
  margin-bottom: $space-8;
}

.see-all-btn {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: $text-secondary;
  font-size: $font-size-xs;
  font-weight: 600;
  padding: $space-1 $space-3;
  border-radius: $radius-md;
  cursor: pointer;
  transition: all $transition;

  &:hover {
    border-color: $accent-primary;
    color: $accent-primary;
    background: rgba($accent-primary, 0.1);
  }
}

.carousel-horizontal {
  display: flex;
  gap: $space-4;
  overflow-x: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
  padding: $space-2 0;

  &::-webkit-scrollbar {
    display: none;
  }
}
</style>
