<template>
  <v-card class="mb-4">
    <v-card-title>
      <v-icon>mdi-sync</v-icon>
      Assignation processing_date (T24 → PowerCard)
    </v-card-title>

    <v-card-text>
      <v-row class="mb-4">
        <v-col cols="12" sm="4">
          <v-text-field v-model="startDate" type="date" label="Date début" outlined dense />
        </v-col>
        <v-col cols="12" sm="4">
          <v-text-field v-model="endDate" type="date" label="Date fin (optionnelle)" outlined dense />
        </v-col>
        <v-col cols="12" sm="4" class="d-flex align-end">
          <v-btn color="primary" :loading="loading" @click="run">
            Lancer
          </v-btn>
          <v-btn text @click="clearAll" class="ml-2">Réinitialiser</v-btn>
        </v-col>
      </v-row>

      <v-row v-if="message">
        <v-col cols="12">
          <v-alert :type="messageType" dense>{{ message }}</v-alert>
        </v-col>
      </v-row>

      <v-row v-if="result">
        <v-col cols="12">
          <div v-if="result.processed && result.processed.length">
            <v-data-table
              :items="result.processed"
              :headers="tableHeaders"
              :items-per-page="10"
              class="elevation-1"
            >
              <template #item.warning="{ item }">
                <v-chip v-if="item.rows_in_range === 0" color="orange" small>Pas de lignes dans la plage</v-chip>
              </template>
            </v-data-table>
          </div>

          <div v-else class="text-caption">
            Aucune période traitée (vérifier les dates ou la présence des données T24).
          </div>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { onMounted, inject, computed } from 'vue'
import { useInsertProcessing } from '../../composables/useInsertProcessing'

const api = inject('api')
const {
  setApiUrl,
  loading,
  startDate,
  endDate,
  result,
  message,
  messageType,
  insertProcessingDates,
  clear
} = useInsertProcessing()

onMounted(() => setApiUrl(api))

const run = async () => {
  await insertProcessingDates()
}

const clearAll = () => clear()

const tableHeaders = computed(() => [
  { title: 'processing_date', key: 'processing_date' },
  { title: 'start_datetime', key: 'start_datetime' },
  { title: 'end_datetime', key: 'end_datetime' },
  { title: 'rows_in_range', key: 'rows_in_range' },
  { title: 'exact_updated_rows', key: 'exact_updated_rows' },
  { title: 'auto_updated_rows', key: 'auto_updated_rows' },
  { title: 'total_updated_rows', key: 'total_updated_rows' },
  { title: 'Warning', key: 'warning' }
])
</script>

<style scoped>
.text-caption { margin-top: 8px; color: #666; }
</style>