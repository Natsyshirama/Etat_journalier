<template>
  <div class="power-card-page">
    <v-tabs v-model="activeTab" class="mb-4">
      <v-tab value="import">
        <v-icon start>mdi-upload</v-icon>
        Import
      </v-tab>
      <v-tab value="transactions">
        <v-icon start>mdi-table</v-icon>
        Transactions
      </v-tab>
    </v-tabs>

    <v-window v-model="activeTab">
      <v-window-item value="import">
        <T24Upload />
      </v-window-item>
      <v-window-item value="transactions">
        <T24TransactCard />
      </v-window-item>
    </v-window>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import T24Upload from '../../components/t24/t24Upload.vue'
import T24TransactCard from '../../components/t24/t24TransactCard.vue'

const activeTab = ref('import')
</script>

<style scoped>
.power-card-page {
  padding: 16px;
}
</style>