<template>
  <div class="t24-diff-card">
    <v-card class="mb-4">
      <v-card-title>Différences PowerCard / T24</v-card-title>
      <v-card-text>
        <v-container>
          <v-row>
            <v-col cols="12" sm="4">
              <v-text-field
                v-model="processingDate"
                type="date"
                label="Date de traitement"
                :disabled="loading"
                outlined
                dense
              />
            </v-col>
            <v-col cols="12" sm="4" class="d-flex align-end">
              <v-btn color="primary" :loading="loading" @click="handleFetch">
                Charger
              </v-btn>
            </v-col>
          </v-row>

          <v-row>
            <v-col cols="12" sm="4">
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

          <v-row v-if="mode === 'single'">
            <v-col cols="12" sm="4">
              <v-text-field
                v-model="processingDate"
                type="date"
                label="Date de traitement"
                :disabled="loading"
                outlined
                dense
              />
            </v-col>
          </v-row>

          <v-row v-else>
            <v-col cols="12" sm="4">
              <v-text-field
                v-model="startDate"
                type="date"
                label="Date début"
                :disabled="loading"
                outlined
                dense
              />
            </v-col>
            <v-col cols="12" sm="4">
              <v-text-field
                v-model="endDate"
                type="date"
                label="Date fin"
                :disabled="loading"
                outlined
                dense
              />
            </v-col>
          </v-row>

          <v-row v-if="startDateTime || endDateTime" class="mb-4">
            <v-col cols="12" sm="6">
              <v-card class="pa-3">
                <div class="text-subtitle-2">Début saisie_le</div>
                <div>{{ startDateTime ?? 'Aucune date disponible' }}</div>
              </v-card>
            </v-col>
            <v-col cols="12" sm="6">
              <v-card class="pa-3">
                <div class="text-subtitle-2">Fin saisie_le</div>
                <div>{{ endDateTime ?? 'Aucune date disponible' }}</div>
              </v-card>
            </v-col>
          </v-row>

          <v-row v-if="message">
            <v-col cols="12">
              <v-alert :type="messageType" dense>
                {{ message }}
              </v-alert>
            </v-col>
          </v-row>

          <v-row v-if="diffs.length">
            <v-col cols="12">
              <v-data-table
                :items="diffs"
                :headers="headers"
                :items-per-page="10"
                class="elevation-1"
              >
                <template #item.powercard="{ item }">
                  <div @click="openPowerCardReference(item.powercard.reference)" class="reference-link">
                    <div><strong>PAN:</strong> {{ item.powercard.pan }}</div>
                    <div><strong>Réf.:</strong> {{ item.powercard.reference }}</div>
                    <div><strong>Action:</strong> {{ item.powercard.action }}</div>
                    <div><strong>Montant:</strong> {{ item.powercard.transaction_amount }}</div>
                  </div>
                </template>
                <template #item.t24_matches="{ item }">
                  <div>
                    <div><strong>{{ item.t24_matches_count }} match(s)</strong></div>
                    <div v-if="item.t24_matches.length">
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
                  </div>
                </template>
                <template #item.processing_date="{ item }">
                  {{ item.processing_date || '-' }}
                </template>
              </v-data-table>
            </v-col>
          </v-row>

          <v-row v-else>
            <v-col cols="12">
              <p class="text-caption">Aucune différence trouvée. Sélectionne une date et clique sur Charger.</p>
            </v-col>
          </v-row>
        </v-container>
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
