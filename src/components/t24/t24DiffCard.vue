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
                  <div>
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
                        <li v-for="(match, index) in item.t24_matches" :key="index">
                          {{ match.pan }} / {{ match.rrn }} / {{ match.credit_amount }} / {{ match.saisie_le }}
                        </li>
                      </ul>
                    </div>
                  </div>
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
  </div>
</template>

<script setup>
import { onMounted, inject } from 'vue'
import { useT24Diff } from '../../composables/useT24Diff'

const api = inject('api')
const {
  processingDate,
  loading,
  message,
  messageType,
  diffs,
  count,
  setApiUrl,
  fetchDiffs,
  clearMessage
} = useT24Diff()

const headers = [
  { title: 'Type', key: 'type' },
  { title: 'PowerCard', key: 'powercard' },
  { title: 'Matches T24', key: 't24_matches' }
]

const handleFetch = async () => {
  clearMessage()
  await fetchDiffs()
}

onMounted(() => {
  setApiUrl(api)
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
