<template>
  <v-card class="mb-4">
    <v-card-title>Transactions T24 par date</v-card-title>
    <v-row class="mb-4">
      <v-col cols="12">
        <v-alert
          v-if="lastSaisieLe"
          dense
          border="left"
        >
          Dernier transaction enregistrer T24 : {{ lastSaisieLe }}
        </v-alert>

        <v-alert
          v-else
          type="warning"
          dense
          border="left"
          colored-border
        >
          Aucun dernier saisie_le disponible
        </v-alert>
      </v-col>
    </v-row>
    <v-card-text style="padding: 0; padding-left: 16px; padding-right: 16px;">
      <div style="max-height: 70vh; overflow-y: auto; overflow-x: hidden; padding-right: 10px;">
        <!-- Filters -->
        <v-row class="mb-2">
          <v-col cols="12" sm="4" md="3">
            <v-text-field
              v-model="startDate"
              type="date"
              label="Date début"
              :disabled="loading"
              outlined
              dense
            />
          </v-col>

          <v-col cols="12" sm="4" md="3">
            <v-text-field
              v-model="endDate"
              type="date"
              label="Date fin (optionnelle)"
              :disabled="loading"
              outlined
              dense
            />
          </v-col>

          <v-col cols="12" sm="4" md="2">
            <v-btn
              color="primary"
              :loading="loading"
              @click="handleFetch"
              block
              size="small"
            >
              <v-icon start>mdi-refresh</v-icon>
              Charger
            </v-btn>
          </v-col>
        </v-row>

        <v-row v-if="message" class="mb-4">
          <v-col cols="12">
            <v-alert :type="messageType" dense>
              {{ message }}
            </v-alert>
          </v-col>
        </v-row>

        <v-row v-if="startDateTime || endDateTime" class="mb-4">
          <v-col cols="12" sm="6" md="3">
            <v-card class="pa-3">
              <div class="text-subtitle-2">Début saisie_le</div>
              <div>{{ startDateTime ?? 'Aucune date disponible' }}</div>
            </v-card>
          </v-col>
          <v-col cols="12" sm="6" md="3">
            <v-card class="pa-3">
              <div class="text-subtitle-2">Fin saisie_le</div>
              <div>{{ endDateTime ?? 'Aucune date disponible' }}</div>
            </v-card>
          </v-col>
        </v-row>

        <v-row v-if="transactions.length">
          <v-col cols="12">
            <div style="overflow-x: auto;">
              <v-data-table
                :items="transactions"
                :headers="headers"
                :items-per-page="10"
                dense
                fixed-header
                height="400px"
                class="elevation-1"
              >
                <template #item.credit_amount="{ item }">
                  {{ item.credit_amount }}
                </template>
              </v-data-table>
            </div>
          </v-col>
        </v-row>

        <v-row v-else>
          <v-col cols="12">
            <v-empty-state
              headline="Aucune transaction"
              description="Aucune transaction chargée pour cette date."
              icon="mdi-database-off"
            />
          </v-col>
        </v-row>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { onMounted, inject } from 'vue'
import { useTransactions } from '../../composables/useTransactions'

const api = inject('api')
const {
  startDate,
  endDate,
  loading,
  message,
  messageType,
  transactions,
  count,
  startDateTime,
  endDateTime,
  lastSaisieLe,
  fetchLastSaisieLe,
  setApiUrl,
  fetchTransactions,
  clearMessage
} = useTransactions()

const headers = [
  { title: 'ID', key: 'id', width: 80 },
  { title: 'Compte', key: 'account_number', width: 120 },
  { title: 'Montant', key: 'credit_amount', width: 100 },
  { title: 'Date traitement', key: 'processing_date', width: 140 },
  { title: 'PAN', key: 'pan', width: 110 },
  { title: 'RRN', key: 'rrn', width: 100 },
  { title: 'Compte DB Cions', key: 'compte_db_cions', width: 130 },
  { title: 'Saisi le', key: 'saisie_le', width: 140 }
]

const handleFetch = async () => {
  clearMessage()
  await fetchTransactions()
}

onMounted(() => {
  setApiUrl(api)
  fetchLastSaisieLe()
})
</script>

<style scoped>
.text-caption {
  margin-top: 8px;
}

:deep(.v-table__wrapper) {
  max-height: 400px !important;
}

:deep(.v-data-table__thead) {
  position: sticky;
  top: 0;
  z-index: 10;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style>