<template>
  <q-page class="q-pa-md">
    <q-banner v-if="error" class="bg-red-1 text-red-9" rounded>{{ error }}</q-banner>

    <div v-if="isLoading" class="row justify-center q-my-xl">
      <q-spinner color="primary" size="42px" />
    </div>

    <template v-else-if="media">
      <q-card flat bordered>
        <q-img v-if="media.banner_image" :src="media.banner_image" :ratio="21 / 8" />
        <q-card-section class="row q-col-gutter-lg">
          <div class="col-12 col-md-3">
            <q-img :src="media.cover_image_large ?? undefined" :ratio="2 / 3">
              <template #error>
                <div class="absolute-full flex flex-center bg-grey-3 text-grey-7">No Cover</div>
              </template>
            </q-img>
          </div>
          <div class="col-12 col-md-9">
            <div class="text-h5">{{ media.title_english || media.title_romaji }}</div>
            <div class="text-subtitle2 text-grey-7">{{ media.title_native || media.title_romaji }}</div>

            <div class="q-mt-md text-body2">
              <div><strong>Type:</strong> {{ media.media_type || 'Unknown' }}</div>
              <div><strong>Format:</strong> {{ media.format || 'Unknown' }}</div>
              <div><strong>Status:</strong> {{ media.status || 'Unknown' }}</div>
              <div><strong>Score:</strong> {{ media.average_score ?? 'N/A' }}</div>
            </div>

            <q-btn class="q-mt-md" color="primary" label="Add to List" @click="showAddSheet = true" />
          </div>
        </q-card-section>

        <q-separator />
        <q-card-section>
          <div class="text-subtitle1 q-mb-sm">Synopsis</div>
          <div class="text-body2" style="white-space: pre-line">{{ media.synopsis || 'No synopsis available.' }}</div>
        </q-card-section>
      </q-card>

      <add-to-list-sheet
        v-model="showAddSheet"
        :media-id="media.id"
        :title="media.title_english || media.title_romaji"
      />
    </template>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import AddToListSheet from 'src/components/tracking/AddToListSheet.vue'
import { useMediaDetail } from 'src/composables/useMediaDetail'

const route = useRoute()
const showAddSheet = ref(false)

const { data: media, isLoading, error, fetchById } = useMediaDetail()

onMounted(async () => {
  const id = route.params.id
  if (typeof id === 'string' && id.length > 0) {
    await fetchById(id)
  }
})
</script>
