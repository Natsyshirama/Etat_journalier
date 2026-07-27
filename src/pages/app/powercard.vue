<template>
  <div class="power-card-page">
    <v-tabs v-model="activeTab" class="mb-4">
      <v-tab value="import">
        <v-icon start>mdi-upload</v-icon>
        Import Power Card
      </v-tab>
      <v-tab value="stats">
        <v-icon start>mdi-chart-box</v-icon>
        Statistiques
      </v-tab>
      <v-tab value="transactions">
        <v-icon start>mdi-table</v-icon>
        Transactions
      </v-tab>
      <v-tab value="processing">
        <v-icon start>mdi-sync</v-icon>
        Processing
      </v-tab>
    </v-tabs>

    <v-window v-model="activeTab">
      <!-- Import Tab -->
      <v-window-item value="import">
        <PowerCardUpload />
      </v-window-item>

      <!-- Stats Tab -->
      <v-window-item value="stats">
        <PowerCardStats />
      </v-window-item>

      <!-- Transactions Tab -->
      <v-window-item value="transactions">
        <PowerCardTransactions />
      </v-window-item>

      <!-- Processing Tab -->
      <v-window-item value="processing">
        <PowerProcessing />
      </v-window-item>
    </v-window>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import PowerCardUpload from '../../components/powercard/PowerCardUpload.vue'
import PowerCardStats from '../../components/powercard/PowerCardStats.vue'
import PowerCardTransactions from '../../components/powercard/PowerCardTransactions.vue'
import PowerProcessing from '../../components/powercard/PowerProcessing.vue'

const activeTab = ref('import')
</script>

<style scoped>
.power-card-page {
  padding: 16px;
}
</style>
