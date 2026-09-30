<template>
  <div class="gestion-import-page">
    <v-card class="main-card">

      <v-card-text>
       
        <v-window v-model="activeTab">
          <v-window-item value="t24">
            <ImportDatesStats />
          </v-window-item>

          <v-window-item value="powercard">
            <PowerCardUpload />
          </v-window-item>
        </v-window>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import T24Upload from '../../components/t24/t24Upload.vue'
import PowerCardUpload from '../../components/powercard/PowerCardUpload.vue'
import ImportDatesStats from '../../components/t24/ImportDatesStats.vue'

const activeTab = ref('t24')
</script>

<style scoped>
.gestion-import-page {
  padding: 16px;
}

.main-card {
  border-radius: 12px;
}

.page-title {
  font-size: 1.25rem;
  font-weight: 600;
  padding: 20px 24px;
}
</style>