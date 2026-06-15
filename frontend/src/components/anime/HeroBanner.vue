<template>
  <div class="hero-banner">
    <div class="hero-bg" :style="bgStyle">
      <div class="hero-gradient"></div>
      <div class="hero-gradient-right"></div>
    </div>
    <div class="hero-content">
      <div class="hero-poster">
        <img
          v-if="posterSrc"
          :src="posterSrc"
          :alt="title"
          @error="onPosterError"
        />
        <div v-else class="poster-placeholder" />
      </div>
      <div class="hero-info">
        <h1 class="hero-title">{{ title }}</h1>
        <p v-if="titleEnglish && titleEnglish !== title" class="hero-title-alt">
          {{ titleEnglish }}
        </p>
        <div class="hero-tags">
          <span class="tag tag-type">{{ mediaType }}</span>
          <span v-if="format" class="tag tag-format">{{ format }}</span>
          <span v-if="status" class="tag tag-status">{{ status }}</span>
          <span v-if="year" class="tag tag-year">{{ year }}</span>
          <span v-if="episodeCount" class="tag tag-eps">{{ episodeCount }} eps</span>
        </div>
        <div v-if="genres.length > 0" class="hero-genres">
          <span v-for="g in genres" :key="g" class="genre-chip">{{ g }}</span>
        </div>
        <div v-if="score !== null" class="hero-score-row">
          <ScoreRing :score="score" :size="56" />
        </div>
        <div class="hero-actions">
          <button class="btn-play" @click="$emit('play')">
            <span class="play-icon">▶</span>
            Play
          </button>
          <button class="btn-secondary" @click="$emit('add-list')">
            + List
          </button>
          <button class="btn-icon" @click="$emit('like')" title="Like">
            ♡
          </button>
          <button class="btn-icon" @click="$emit('share')" title="Share">
            ↗
          </button>
        </div>
        <div class="hero-synopsis">
          <p
            :class="{
              expanded: isSynopsisExpanded,
              clamped: Boolean(synopsis && synopsis.length > 300 && !isSynopsisExpanded),
            }"
          >
            {{ synopsis || 'No synopsis available.' }}
          </p>
          <button
            v-if="synopsis && synopsis.length > 300"
            class="synopsis-toggle"
            @click="$emit('synopsis-toggle')"
          >
            {{ isSynopsisExpanded ? 'Show less' : 'Read more' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import ScoreRing from './ScoreRing.vue'

interface HeroBannerProps {
  title: string
  titleEnglish: string | null
  bannerImage: string | null
  synopsis: string | null
  score: number | null
  year: number | null
  mediaType: string
  format: string | null
  status: string | null
  episodeCount: number | null
  genres?: string[]
  isSynopsisExpanded?: boolean
}

const props = withDefaults(defineProps<HeroBannerProps>(), {
  titleEnglish: null,
  bannerImage: null,
  synopsis: null,
  score: null,
  year: null,
  format: null,
  status: null,
  episodeCount: null,
  genres: () => [],
  isSynopsisExpanded: false,
})

defineEmits<{
  'synopsis-toggle': []
  play: []
  'add-list': []
  like: []
  share: []
}>()

const posterError = ref(false)

const bgStyle = computed(() => {
  if (props.bannerImage) {
    return { backgroundImage: `url(${props.bannerImage})` }
  }
  return {}
})

const posterSrc = computed(() => {
  if (props.bannerImage && !posterError.value) {
    return props.bannerImage
  }
  return null
})

function onPosterError() {
  posterError.value = true
}
</script>

<style lang="scss">
@use 'src/css/tokens' as *;
@use 'sass:color';

.hero-banner {
  position: relative;
  min-height: 420px;
  display: flex;
  align-items: flex-end;
  overflow: hidden;
  border-radius: $radius-lg;
  margin-bottom: $space-6;

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
    position: relative;
    display: flex;
    gap: $space-6;
    padding: $space-8;
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    z-index: 2;

    .hero-poster {
      flex-shrink: 0;
      width: 180px;
      height: 270px;
      border-radius: $radius-md;
      overflow: hidden;
      box-shadow: $shadow-lg;

      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }

      .poster-placeholder {
        width: 100%;
        height: 100%;
        background: $bg-elevated;
      }
    }

    .hero-info {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: $space-3;
      padding-top: $space-6;

      .hero-title {
        font-size: $font-size-3xl;
        font-weight: 800;
        color: $text-primary;
        margin: 0;
        line-height: 1.1;
      }

      .hero-title-alt {
        font-size: $font-size-md;
        color: $text-muted;
        margin: 0;
      }

      .hero-tags {
        display: flex;
        flex-wrap: wrap;
        gap: $space-2;

        .tag {
          padding: 2px 8px;
          border-radius: $radius-sm;
          font-size: $font-size-xs;
          font-weight: 600;
          text-transform: uppercase;
          background: rgba(255, 255, 255, 0.1);
          color: $text-secondary;
          border: 1px solid rgba(255, 255, 255, 0.15);

          &.tag-type {
            color: $accent-primary;
            border-color: $accent-primary;
          }
        }
      }

      .hero-genres {
        display: flex;
        flex-wrap: wrap;
        gap: $space-2;

        .genre-chip {
          padding: 4px 12px;
          border-radius: 999px;
          font-size: $font-size-xs;
          font-weight: 500;
          background: rgba($accent-primary, 0.15);
          color: $accent-primary;
        }
      }

      .hero-score-row {
        margin: $space-2 0;
      }

      .hero-actions {
        display: flex;
        gap: $space-3;
        align-items: center;
        margin: $space-3 0;

        .btn-play {
          display: flex;
          align-items: center;
          gap: $space-2;
          padding: $space-3 $space-6;
          border-radius: $radius-md;
          border: none;
          background: $accent-primary;
          color: white;
          font-size: $font-size-md;
          font-weight: 700;
          cursor: pointer;
          transition: all $transition;

          .play-icon {
            font-size: $font-size-lg;
          }

          &:hover {
            background: color.adjust($accent-primary, $lightness: 8%);
            box-shadow: 0 0 16px rgba($accent-primary, 0.4);
          }
        }

        .btn-secondary {
          padding: $space-3 $space-4;
          border-radius: $radius-md;
          border: $border-subtle;
          background: rgba(255, 255, 255, 0.08);
          color: $text-primary;
          font-size: $font-size-sm;
          font-weight: 600;
          cursor: pointer;
          transition: all $transition;

          &:hover {
            background: rgba(255, 255, 255, 0.15);
            border-color: $accent-primary;
          }
        }

        .btn-icon {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          border: $border-subtle;
          background: rgba(255, 255, 255, 0.08);
          color: $text-secondary;
          font-size: $font-size-lg;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all $transition;

          &:hover {
            background: rgba(255, 255, 255, 0.15);
            color: $text-primary;
          }
        }
      }

      .hero-synopsis {
        p {
          font-size: $font-size-sm;
          color: $text-secondary;
          line-height: 1.6;
          margin: 0;
          max-width: 700px;

          &.clamped {
            display: -webkit-box;
            -webkit-line-clamp: 4;
            -webkit-box-orient: vertical;
            overflow: hidden;
          }
        }

        .synopsis-toggle {
          background: none;
          border: none;
          color: $accent-primary;
          cursor: pointer;
          font-size: $font-size-sm;
          font-weight: 600;
          padding: $space-1 0;

          &:hover {
            text-decoration: underline;
          }
        }
      }
    }
  }

  @include respond-below(sm) {
    min-height: 300px;

    .hero-content {
      flex-direction: column;
      padding: $space-4;

      .hero-poster {
        width: 120px;
        height: 180px;
      }

      .hero-title {
        font-size: $font-size-xl;
      }
    }
  }
}
</style>
