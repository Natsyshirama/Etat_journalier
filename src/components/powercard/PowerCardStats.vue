<template>
  <div class="power-card-stats">

    <!-- ========================================== -->
    <!-- HEADER -->
    <!-- ========================================== -->
    <v-card class="main-card">

      <v-card-title class="page-title">
        <v-icon start size="28">mdi-chart-box</v-icon>
        Statistiques Power Card
      </v-card-title>

      <v-divider />

      <v-card-text>

        <!-- ========================================== -->
        <!-- FILTRES -->
        <!-- ========================================== -->
        <v-row class="filter-row">
          <v-col cols="12" md="6">
            <v-text-field
              v-model="selectedDate"
              type="date"
              label="Filtrer par date"
              variant="outlined"
              density="comfortable"
              clearable
              @update:model-value="loadStats"
            />
          </v-col>

          <v-col
            cols="12"
            md="6"
            class="d-flex align-center"
          >
            <v-btn
              color="primary"
              size="large"
              :loading="statsLoading"
              prepend-icon="mdi-refresh"
              @click="loadStats"
            >
              Actualiser
            </v-btn>
          </v-col>
        </v-row>


        <!-- ========================================== -->
        <!-- LOADING -->
        <!-- ========================================== -->
        <v-row v-if="statsLoading">
          <v-col cols="12">
            <v-skeleton-loader
              type="card, table"
              class="mt-4"
            />
          </v-col>
        </v-row>


        <!-- ========================================== -->
        <!-- CONTENU -->
        <!-- ========================================== -->
        <template v-else>

          <!-- ======================================== -->
          <!-- STATISTIQUES PAR TERMINAL -->
          <!-- ======================================== -->
          <div
            v-if="terminalStats.length"
            class="section-container terminal-section"
          >

            <div class="section-title">
              <v-icon start color="primary">
                mdi-monitor-dashboard
              </v-icon>

              Statistiques par terminal

              <v-chip
                size="small"
                class="ml-3"
                color="primary"
                variant="tonal"
              >
                {{ terminalStats.length }} terminal(s)
              </v-chip>
            </div>


            <v-card
              class="terminal-card"
              variant="outlined"
            >

              <v-data-table
                :headers="terminalHeaders"
                :items="terminalStats"
                :loading="statsLoading"
                class="terminal-table elevation-1"
                density="comfortable"
                hover
                fixed-header
                height="400px"
              >

                <!-- Terminal -->
                <template #item.terminal_no="{ item }">
                  <strong>
                    {{ item.terminal_no }}
                  </strong>
                </template>


                <!-- Total -->
                <template #item.total_transactions="{ item }">
                  <v-chip
                    color="blue"
                    size="small"
                    variant="tonal"
                  >
                    {{ item.total_transactions }}
                  </v-chip>
                </template>


                <!-- Approuvées -->
                <template #item.approved_count="{ item }">
                  <v-chip
                    color="green"
                    size="small"
                    variant="tonal"
                  >
                    <v-icon start size="16">
                      mdi-check
                    </v-icon>

                    {{ item.approved_count }}
                  </v-chip>
                </template>


                <!-- Annulées -->
                <template #item.canceled_count="{ item }">
                  <v-chip
                    :color="
                      item.canceled_count > 0
                        ? 'orange'
                        : 'grey'
                    "
                    size="small"
                    variant="tonal"
                  >
                    {{ item.canceled_count }}
                  </v-chip>
                </template>


                <!-- Autres -->
                <template #item.other_count="{ item }">
                  <v-chip
                    :color="
                      item.other_count > 0
                        ? 'red'
                        : 'grey'
                    "
                    size="small"
                    variant="tonal"
                  >
                    {{ item.other_count }}
                  </v-chip>
                </template>


                <!-- Montant -->
                <template #item.approved_amount="{ item }">
                  <strong>
                    {{ formatAmount(item.approved_amount) }}
                  </strong>
                </template>


                <!-- Taux -->
                <template #item.success_rate="{ item }">
                  <v-chip
                    :color="
                      item.success_rate >= 80
                        ? 'green'
                        : item.success_rate >= 50
                          ? 'orange'
                          : 'red'
                    "
                    size="small"
                    variant="tonal"
                  >
                    {{ formatSuccessRate(item.success_rate) }}
                  </v-chip>
                </template>

              </v-data-table>

            </v-card>
          </div>
          <!-- ======================================== -->
          <!-- STATISTIQUES GLOBALES -->
          <!-- ======================================== -->
          <div
            v-if="singleStats"
            class="section-container"
          >

            <div class="section-title">
              <v-icon start color="primary">
                mdi-chart-pie
              </v-icon>

              Statistiques globales

              <v-chip
                v-if="selectedDate"
                size="small"
                class="ml-3"
                color="primary"
                variant="tonal"
              >
                {{ selectedDate }}
              </v-chip>
            </div>


            <!-- CARDS GLOBALES -->
            <v-row>

              <!-- Total transactions -->
              <v-col
                cols="12"
                sm="6"
                md="3"
              >
                <v-card class="stat-card blue">
                  <v-card-text>
                    <div class="stat-icon">
                      <v-icon size="32">
                        mdi-swap-horizontal
                      </v-icon>
                    </div>

                    <p class="stat-label">
                      Total transactions
                    </p>

                    <p class="stat-value">
                      {{ singleStats.withdrawal_total_transactions || 0 }}
                    </p>
                  </v-card-text>
                </v-card>
              </v-col>


              <!-- Montant total -->
              <v-col
                cols="12"
                sm="6"
                md="3"
              >
                <v-card class="stat-card orange">
                  <v-card-text>
                    <div class="stat-icon">
                      <v-icon size="32">
                        mdi-cash-multiple
                      </v-icon>
                    </div>

                    <p class="stat-label">
                      Montant total
                    </p>

                    <p class="stat-value">
                      {{
                        formatAmount(
                          singleStats.withdrawal_total_amount
                        )
                      }}
                    </p>
                  </v-card-text>
                </v-card>
              </v-col>


              <!-- Transactions rejetées -->
              

            </v-row>
          </div>
          <!-- ======================================== -->
          <!-- ACTIONS -->
          <!-- ======================================== -->
          <div
            v-if="singleStats?.actions?.length"
            class="section-container"
          >

            <div class="section-title">
              <v-icon start color="primary">
                mdi-format-list-bulleted
              </v-icon>

              Répartition par action
            </div>

            <v-row>

              <v-col
                v-for="action in singleStats.actions"
                :key="action.action"
                cols="12"
                sm="6"
                md="4"
              >
                <v-card class="action-card">

                  <v-card-text>

                    <div class="action-header">
                      <span class="action-name">
                        {{ action.action }}
                      </span>

                      <v-chip
                        size="small"
                        color="primary"
                        variant="tonal"
                      >
                        {{ action.count }}
                      </v-chip>
                    </div>

                    <div class="action-amount">
                      {{ formatAmount(action.amount) }}
                    </div>

                  </v-card-text>

                </v-card>
              </v-col>

            </v-row>
          </div>

          


          


          <!-- ======================================== -->
          <!-- AUCUNE DONNÉE -->
          <!-- ======================================== -->
          <v-empty-state
            v-if="
              !singleStats &&
              !terminalStats.length
            "
            headline="Aucune donnée"
            description="
              Aucune transaction Power Card trouvée
              pour les critères spécifiés
            "
            icon="mdi-database-off"
            class="mt-8"
          />

        </template>

      </v-card-text>


      <!-- ========================================== -->
      <!-- MESSAGE -->
      <!-- ========================================== -->
      <v-card-text v-if="message">

        <v-alert
          :type="messageType"
          border="start"
          closable
          @click:close="clearMessage"
        >
          {{ message }}
        </v-alert>

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
  fetchStats,
  fetchTerminalStats,
  message,
  messageType,
  clearMessage
} = usePowerCardImport()

const selectedDate = ref('')
const statsLoading = ref(false)
const singleStats = ref(null)
const terminalStats = ref([])

const headers = [
  { title: 'Date', key: 'import_date' },
  { title: 'Total Transactions', key: 'total_transactions' },
  { title: 'Approuvées', key: 'approved_count' },
  { title: 'Rejetées', key: 'rejected_count' },
  { title: 'Actions', key: 'actions', sortable: false }
]

const terminalHeaders = [
  { title: 'Terminal', key: 'terminal_no' },
  { title: 'Total transactions', key: 'total_transactions' },
  { title: 'Approuvées', key: 'approved_count' },
  { title: 'Annulées', key: 'canceled_count' },
  { title: 'Autres', key: 'other_count' },
  { title: 'Montant approuvé', key: 'approved_amount' },
  { title: 'Taux de réussite', key: 'success_rate' }
]

const formatAmount = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'MGA'
  }).format(amount || 0)
}

const formatSuccessRate = (rate) => {
  return `${Number(rate || 0).toFixed(2)} %`
}

const loadStats = async () => {
  statsLoading.value = true
  clearMessage()

  const date = selectedDate.value || null

  try {
    const [globalStats, terminalData] = await Promise.all([
      fetchStats(date),
      fetchTerminalStats(date)
    ])

    singleStats.value = globalStats
    terminalStats.value = terminalData
  } catch (error) {
    console.error('Erreur chargement statistiques:', error)
    singleStats.value = null
    terminalStats.value = []
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
  height: calc(100vh - 32px);
  min-height: 0;
  padding: 20px;
}

.main-card {
  height: 90%;
  max-height: none;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-radius: 12px;
}

.main-card > .v-card-text {
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
}

.terminal-card {
  border-radius: 10px;
  overflow: hidden;
}

.terminal-table {
  width: 100%;
}

.terminal-table-container {
  height: 500px;
  overflow-y: auto;
  overflow-x: auto;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  background: white;
}

.terminal-table {
  min-width: 900px;
  width: 100%;
}

.terminal-table :deep(.v-table__wrapper) {
  max-height: 400px !important;
  overflow-y: auto !important;
  overflow-x: auto !important;
}

.terminal-table :deep(.v-data-table__thead) {
  position: sticky;
  top: 0;
  z-index: 2;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* ==========================================
   STATISTIQUES GLOBALES
========================================== */

.stat-card {
  height: 145px;
  border-left: 5px solid;
  border-radius: 10px;
  transition: transform 0.2s ease,
              box-shadow 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.12);
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

.stat-card.orange {
  border-left-color: #f57c00;
}

.stat-icon {
  margin-bottom: 5px;
}

.stat-icon .v-icon {
  opacity: 0.75;
}

.stat-label {
  font-size: 0.85rem;
  color: #666;
  margin: 0;
}

.stat-value {
  font-size: 1.6rem;
  font-weight: 700;
  margin: 5px 0 0;
}


/* ==========================================
   TABLEAU TERMINAUX
========================================== */
.terminal-card {
  border-radius: 10px;
  overflow: hidden;
}

.terminal-table {
  width: 100%;
}

.terminal-table :deep(.v-table__wrapper) {
  max-height: 400px;
  overflow-y: auto;
  overflow-x: auto;
}

/* ==========================================
   ACTIONS
========================================== */

.action-card {
  border-radius: 10px;
  border-left: 4px solid #9e9e9e;
}

.action-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-name {
  font-weight: 600;
  font-size: 0.95rem;
}

.action-amount {
  margin-top: 12px;
  font-size: 1.2rem;
  font-weight: 600;
}


/* ==========================================
   RESPONSIVE
========================================== */

@media (max-width: 600px) {

  .power-card-stats {
    padding: 10px;
  }

  .stat-card {
    height: auto;
    min-height: 130px;
  }

  .stat-value {
    font-size: 1.4rem;
  }

}

</style>