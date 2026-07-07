<template>
  <v-card class="mb-4">
    <v-card-title>Transactions T24 par date</v-card-title>
    <v-card-text>
      <v-container>
        <v-row>
          <v-col cols="12" sm="4">
            <v-text-field
              v-model="importDate"
              type="date"
              label="Date"
              :disabled="loading"
              outlined
              dense
            />
          </v-col>

          <v-col cols="12" sm="4" class="d-flex align-end">
            <v-btn
              color="primary"
              :loading="loading"
              @click="handleFetch"
            >
              Charger
            </v-btn>
          </v-col>
        </v-row>

        <v-row v-if="message">
          <v-col cols="12">
            <v-alert :type="messageType" dense>
              {{ message }}
            </v-alert>
          </v-col>
        </v-row>

        <v-row v-if="transactions.length">
          <v-col cols="12">
            <v-data-table
              :items="transactions"
              :headers="headers"
              :items-per-page="10"
              class="elevation-1"
            >
              <template #item.credit_amount="{ item }">
                {{ item.credit_amount }}
              </template>
            </v-data-table>
          </v-col>
        </v-row>

        <v-row v-else>
          <v-col cols="12">
            <p class="text-caption">Aucune transaction chargée pour cette date.</p>
          </v-col>
        </v-row>
      </v-container>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { onMounted,inject } from 'vue'
import { useTransactions } from '../../composables/useTransactions'

const api = inject('api')
const {
  importDate,
  loading,
  message,
  messageType,
  transactions,
  count,
  setApiUrl,
  fetchTransactions,
  clearMessage
} = useTransactions()

const headers = [
  { title: 'ID', key: 'id' },
  { title: 'Compte', key: 'account_number' },
  { title: 'Montant', key: 'credit_amount' },
  { title: 'Date traitement', key: 'processing_date' },
  { title: 'PAN', key: 'pan' },
  { title: 'RRN', key: 'rrn' },
  { title: 'Compte DB Cions', key: 'compte_db_cions' },
  { title: 'Saisi le', key: 'saisie_le' }
]

const handleFetch = async () => {
  clearMessage()
  await fetchTransactions()
}

onMounted(() => {
  setApiUrl(api)
})
</script>

<style scoped>
.text-caption {
  margin-top: 8px;
}
</style>