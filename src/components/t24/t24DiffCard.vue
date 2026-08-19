<template>
  <div class="t24-diff-card">
    <v-card class="mb-4">
      <v-card-title>Différences PowerCard / T24</v-card-title>
      <v-card-text style="padding: 0; padding-left: 16px; padding-right: 16px;">
        <div style="max-height: 70vh; overflow-y: auto; overflow-x: hidden; padding-right: 10px;">
          <!-- Mode Selection -->
          <v-row class="mb-2">
            <v-col cols="12" sm="4" md="3">
              <v-select
                v-model="mode"
                :items="modeItems"
                label="Mode de traitement"
                :disabled="loading"
                outlined
                dense
              />
            </v-col>
          </v-row>

          <!-- Single Mode: Date Unique -->
          <v-row v-if="mode === 'single'" class="mb-2">
            <v-col cols="12" sm="4" md="3">
              <v-text-field
                v-model="processingDate"
                type="date"
                label="Date de traitement"
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
              >
                <v-icon start>mdi-refresh</v-icon>
                Charger
              </v-btn>
            </v-col>
          </v-row>

          <!-- Range Mode: Date Début & Date Fin -->
          <v-row v-else class="mb-2">
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
                label="Date fin"
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

          <v-row v-if="diffs.length">
            <v-col cols="12">
              <div style="overflow-x: auto;">
                <v-data-table
                  :items="diffs"
                  :headers="headers"
                  :items-per-page="10"
                  dense
                  fixed-header
                  height="400px"
                  class="elevation-1"
                >
                  <template #item.powercard="{ item }">
                    <div v-if="item.type === 'missing_in_powercard' ">—</div>
                    <div v-else-if="item.powercard">
                      <div><strong>PAN:</strong> {{ item.powercard.pan }}</div>
                      <div><strong>Réf.:</strong> {{ item.powercard.reference }}</div>
                      <div><strong>Action:</strong> {{ item.powercard.action }}</div>
                      <div><strong>Montant:</strong> {{ item.powercard.transaction_amount }}</div>
                    </div>
                    <div v-else-if="item.t24">
                      <div><strong>T24 seul</strong></div>
                      <div><strong>PAN:</strong> {{ item.t24.pan }}</div>
                      <div><strong>RRN:</strong> {{ item.t24.rrn }}</div>
                      <div><strong>Montant:</strong> {{ item.t24.credit_amount }}</div>
                    </div>
                    <div v-else>—</div>
                  </template>
                  <template #item.t24_matches="{ item }">
                    <div v-if=" item.type === 'approved_missing_in_t24'">—</div>
                    <div v-else-if="item.t24_matches?.length">
                      <div><strong>{{ item.t24_matches_count }} match(s)</strong></div>
                      <ul class="match-list">
                        <li
                          v-for="(match, index) in item.t24_matches"
                          :key="index"
                          class="reference-link"
                          @click="openT24Reference(match.rrn)"
                        >
                          {{ match.pan }} / {{ match.rrn }} / {{ match.credit_amount }} / {{ match.saisie_le }}
                        </li>
                      </ul>
                    </div>
                    <div v-else-if="item.t24">
                      <div><strong>T24 seul</strong></div>
                      <div>{{ item.t24.pan }} / {{ item.t24.rrn }} / {{ item.t24.credit_amount }}</div>
                    </div>
                    <div v-else>—</div>
                  </template>
                  <template #item.processing_date="{ item }">
                    {{ item.processing_date || '-' }}
                  </template>
                </v-data-table>
              </div>
            </v-col>
          </v-row>

          <v-row v-else>
            <v-col cols="12">
              <v-empty-state
                headline="Aucune différence"
                description="Sélectionne une date et clique sur Charger."
                icon="mdi-database-off"
              />
            </v-col>
          </v-row>
        </div>
      </v-card-text>
    </v-card>
    <v-dialog v-model="showReferenceDialog" max-width="800px">
  <v-card>
    <v-card-title>Détail {{ referenceSource }} - {{ referenceDetail }}</v-card-title>
    <v-card-text>
      <v-simple-table v-if="referenceData">
        <thead>
          <tr>
            <th>Champ</th>
            <th>Valeur</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="field in referenceSource === 'T24' ? referenceFieldsT24 : referenceFields" :key="field">
            <td>{{ field }}</td>
            <td>{{ referenceData[field] }}</td>
          </tr>
        </tbody>
      </v-simple-table>
      <div v-else>Aucun détail disponible</div>
    </v-card-text>
    <v-card-actions>
      <v-spacer />
      <v-btn text @click="showReferenceDialog = false">Fermer</v-btn>
    </v-card-actions>
    <v-row class="mb-4">
        <v-col cols="12">
          <v-alert
            v-if="message"
            :type="messageType"
            dense
            border="left"
            closable
          >
            {{ message }}
          </v-alert>
        </v-col>
      </v-row>  
  </v-card>
</v-dialog>
  </div>
</template>

<script setup>
import { onMounted, inject } from 'vue'
import { useT24Diff } from '../../composables/useT24Diff'

const apiUrl = inject('api')
const referenceFieldsT24 = [
  'id',
  'account_number',
  'credit_amount',
  'processing_date',
  'pan',
  'rrn',
  'compte_db_cions',
  'saisie_le',
  'import_date',
  'created_at'
]

const modeItems = [
  { title: 'Date unique', value: 'single' },
  { title: 'Période', value: 'range' }
]

const referenceFields = [
  'id',
  'external_stan',
  'reference',
  'source',
  'destination',
  'message',
  'processing_code',
  'action',
  'pan',
  'local_time',
  'internal_time',
  'transaction_amount',
  'terminal_no',
  'acceptor_point',
  'authorization_reference',
  'current_table_indicator',
  'source_account_number',
  'import_date',
  'created_at'
]
const {
  api,
  loading,
  processingDate,
  startDate,
  endDate,
  mode,
  message,
  messageType,
  diffs,
  count,
  showReferenceDialog,
  referenceDetail,
  referenceData,
  setApiUrl,
  fetchDiffs,
  clearMessage,
  openPowerCardReference,
  openT24Reference,
  referenceSource,
  startDateTime,
  endDateTime,
  
} = useT24Diff()
const headers = [
  { title: 'Processing Date', key: 'processing_date' },
  { title: 'Type', key: 'type' },
  { title: 'PowerCard', key: 'powercard' },
  { title: 'Matches T24', key: 't24_matches' }
]

const handleFetch = async () => {
  clearMessage()
  await fetchDiffs()
}

onMounted(() => {
  setApiUrl(apiUrl)
})
</script>

<style scoped>
.t24-diff-card {
  padding: 16px;
}

.match-list {
  margin: 0;
  padding-left: 16px;
}

.text-caption {
  margin-top: 8px;
}
</style>
