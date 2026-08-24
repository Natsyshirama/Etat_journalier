<template>
  <div class="power-card-page">
    <v-tabs v-model="activeTab" class="mb-4">
      <v-tab v-if="isAdmin" value="import">
        <v-icon start>mdi-upload</v-icon>
        Import
      </v-tab>
      <v-tab value="transactions">
        <v-icon start>mdi-table</v-icon>
        Transactions
      </v-tab>
      <v-tab value="diff">
        <v-icon start>mdi-shape-outline</v-icon>
        Différences
      </v-tab>
    </v-tabs>

    <v-window v-model="activeTab">
      <v-window-item v-if="isAdmin" value="import">
        <T24Upload />
      </v-window-item>
      <v-window-item value="transactions">
        <T24TransactCard />
      </v-window-item>
      <v-window-item value="diff">
        <T24DiffCard />
      </v-window-item>
    </v-window>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { usePopupStore } from '../../stores'
import T24Upload from '../../components/t24/t24Upload.vue'
import T24TransactCard from '../../components/t24/t24TransactCard.vue'
import T24DiffCard from '../../components/t24/t24DiffCard.vue'

const activeTab = ref('transactions')
const popupStore = usePopupStore()

const isAdmin = computed(() => popupStore.user_access.access === 'admin')
</script>

<style scoped>
.power-card-page {
  padding: 16px;
}
</style>