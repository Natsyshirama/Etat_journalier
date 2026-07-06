<template>
  <div class="power-card-stats">
    <v-card class="mb-4">
      <v-card-title>
        <v-icon>mdi-chart-box</v-icon>
        Statistiques Power Card
      </v-card-title>

      <v-card-text>
        <v-container>
          <!-- Date Filter -->
          <v-row class="mb-4">
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="selectedDate"
                type="date"
                label="Filtrer par date"
                outlined
                dense
                @change="loadStats"
              />
            </v-col>
            <v-col cols="12" sm="6">
              <v-btn
                color="primary"
                :loading="statsLoading"
                @click="loadStats"
              >
                <v-icon start>mdi-refresh</v-icon>
                Actualiser
              </v-btn>
            </v-col>
          </v-row>

          <!-- Loading State -->
          <v-row v-if="statsLoading">
            <v-col cols="12">
              <v-skeleton-loader type="table" />
            </v-col>
          </v-row>

          <!-- Single Date Stats -->
          <v-row v-else-if="selectedDate && singleStats">
            <v-col cols="12" sm="6" md="3">
              <v-card class="stat-card blue">
                <v-card-text>
                  <p class="stat-label">Total Transactions</p>
                  <p class="stat-value">{{ singleStats.total_transactions }}</p>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-card class="stat-card green">
                <v-card-text>
                  <p class="stat-label">Approuvées</p>
                  <p class="stat-value">{{ singleStats.approved_count }}</p>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-card class="stat-card red">
                <v-card-text>
                  <p class="stat-label">Rejetées</p>
                  <p class="stat-value">{{ singleStats.rejected_count }}</p>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-card class="stat-card purple">
                <v-card-text>
                  <p class="stat-label">Montant Total</p>
                  <p class="stat-value">{{ formatAmount(singleStats.total_amount) }}</p>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-card class="stat-card orange">
                <v-card-text>
                  <p class="stat-label">Total WITHDRAW</p>
                  <p class="stat-value">{{ formatAmount(singleStats.withdrawal_total_amount) }}</p>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <!-- All Dates Stats Table -->
          <v-row v-else-if="!selectedDate && allStats && allStats.length > 0">
            <v-col cols="12">
              <v-data-table
                :headers="headers"
                :items="allStats"
                :loading="statsLoading"
                class="elevation-1"
              >
                <template #item.import_date="{ item }">
                  <v-chip size="small">{{ item.import_date }}</v-chip>
                </template>
                <template #item.total_transactions="{ item }">
                  <v-chip color="blue" text-color="white">
                    {{ item.total_transactions }}
                  </v-chip>
                </template>
                <template #item.approved_count="{ item }">
                  <v-chip color="green" text-color="white">
                    {{ item.approved_count }}
                  </v-chip>
                </template>
                <template #item.rejected_count="{ item }">
                  <v-chip :color="item.rejected_count > 0 ? 'red' : 'grey'" text-color="white">
                    {{ item.rejected_count }}
                  </v-chip>
                </template>
                <template #item.actions="{ item }">
                  <v-btn
                    size="small"
                    variant="text"
                    @click="selectDateAndLoadStats(item.import_date)"
                  >
                    <v-icon>mdi-eye</v-icon>
                    Détails
                  </v-btn>
                </template>
              </v-data-table>
            </v-col>
          </v-row>

          <!-- Empty State -->
          <v-row v-else>
            <v-col cols="12">
              <v-empty-state
                headline="Aucune donnée"
                description="Aucune transaction Power Card trouvée pour les critères spécifiés"
                icon="mdi-database-off"
              />
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import { ref, inject, onMounted } from 'vue'
import { usePowerCardImport } from '../../composables/usePowerCardImport'

const api = inject('api')
const {
  setApiUrl,
  fetchStats
} = usePowerCardImport()

const selectedDate = ref('')
const statsLoading = ref(false)
const singleStats = ref(null)
const allStats = ref([])

const headers = [
  { title: 'Date', key: 'import_date' },
  { title: 'Total Transactions', key: 'total_transactions' },
  { title: 'Approuvées', key: 'approved_count' },
  { title: 'Rejetées', key: 'rejected_count' },
  { title: 'Actions', key: 'actions', sortable: false }
]

const formatAmount = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'MGA'
  }).format(amount || 0)
}

const loadStats = async () => {
  statsLoading.value = true
  try {
    const stats = await fetchStats(selectedDate.value || null)

    if (selectedDate.value) {
      singleStats.value = stats
      allStats.value = []
    } else {
      allStats.value = Array.isArray(stats) ? stats : []
      singleStats.value = null
    }
  } catch (error) {
    console.error('Erreur chargement stats:', error)
  } finally {
    statsLoading.value = false
  }
}

const selectDateAndLoadStats = (date) => {
  selectedDate.value = date
  loadStats()
}

onMounted(() => {
  setApiUrl(api)
  loadStats()
})
</script>

<style scoped>
.power-card-stats {
  padding: 16px;
}

.stat-card {
  border-left: 4px solid;
}

.stat-card.blue {
  border-left-color: #2196f3;
}

.stat-card.green {
  border-left-color: #4caf50;
}

.stat-card.red {
  border-left-color: #f44336;
}

.stat-card.purple {
  border-left-color: #9c27b0;
}

.stat-card.orange {
  border-left-color: #f57c00;
}

.stat-label {
  font-size: 0.875rem;
  color: #666;
  margin: 0;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 600;
  margin: 8px 0 0 0;
}
</style>
