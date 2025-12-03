<template>
  <v-container class="unified-container" fluid>
    <v-card class="pa-6">
      <h2 class="mb-4">Détail Decaissement</h2>
      <div class="mb-4">
        <strong>Agence :</strong> {{ agence }}<br>
        <strong>Date :</strong> {{ formattedDate }}
      </div>
      <v-tabs v-model="activeTab" class="mb-4">
        
        <v-tab>Decaissement</v-tab>
      </v-tabs>
      <v-window v-model="activeTab">
        
        <v-window-item>
          <TableauDecaiss :tableName="tableName" :agence="agence" />
        </v-window-item>
      </v-window>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, computed } from "vue"
import { useRoute } from "vue-router"
import TableauDecaiss from '@/components/decaissement/TableauDecaiss.vue'

const route = useRoute()
const tableName = computed(() => route.query.tableName)
const agence = computed(() => route.query.agence)
const activeTab = ref(0)

const formattedDate = computed(() => {
  if (!tableName.value || tableName.value.length !== 8) return tableName.value
  
  const year = tableName.value.slice(0, 4)
  const month = tableName.value.slice(4, 6)
  const day = tableName.value.slice(6, 8)
  
  return `${day}/${month}/${year}`
})

console.log('analyseDetail - Query params:', {
  tableName: tableName.value,
  agence: agence.value,
  fullQuery: route.query
})
</script>

<style scoped>
.unified-container {
  max-height: 90vh;
  overflow-y: auto;
  padding-bottom: 20px;
  padding: 0 10px; 
}
.pa-6 {
  padding: 20px !important;
}
.mb-4 {
  margin-bottom: 16px !important;
}
h2 {
  margin-bottom: 16px;
}
</style>