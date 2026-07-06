<template>
  <div class="power-card-transactions">
    <v-card>
      <v-card-title>
        <v-icon>mdi-table</v-icon>
        Transactions Power Card
      </v-card-title>

      <v-card-text>
        <v-container>
          <!-- Filters -->
          <v-row class="mb-4">
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="selectedDate"
                type="date"
                label="Date"
                outlined
                dense
                :required="true"
              />
            </v-col>
            <v-col cols="12" sm="6">
              <v-btn
                color="primary"
                :loading="transactionsLoading"
                @click="loadTransactions"
              >
                <v-icon start>mdi-refresh</v-icon>
                Charger
              </v-btn>
            </v-col>
          </v-row>

          <!-- Loading State -->
          <v-row v-if="transactionsLoading">
            <v-col cols="12">
              <v-skeleton-loader type="table" />
            </v-col>
          </v-row>

          <!-- Transactions Table -->
          <v-row v-else>
            <v-col cols="12">
              <v-data-table
                :headers="headers"
                :items="transactions"
                :loading="transactionsLoading"
                :items-per-page="50"
                class="elevation-1"
              >
                <template #item.action="{ item }">
                  <v-chip
                    :color="item.action === 'Approved' ? 'green' : 'red'"
                    text-color="white"
                    size="small"
                  >
                    {{ item.action }}
                  </v-chip>
                </template>

                <template #item.local_time="{ item }">
                  {{ formatDateTime(item.local_time) }}
                </template>

                <template #item.transaction_amount="{ item }">
                  {{ formatAmount(item.transaction_amount) }}
                </template>

                <template #expanded-row="{ columns, item }">
                  <tr>
                    <td :colspan="columns.length" class="expansion-row">
                      <v-container>
                        <v-row>
                          <v-col cols="12" sm="6" md="3">
                            <p><strong>Reference:</strong></p>
                            <p>{{ item.reference }}</p>
                          </v-col>
                          <v-col cols="12" sm="6" md="3">
                            <p><strong>PAN:</strong></p>
                            <p>{{ item.pan }}</p>
                          </v-col>
                          <v-col cols="12" sm="6" md="3">
                            <p><strong>Terminal:</strong></p>
                            <p>{{ item.terminal_no }}</p>
                          </v-col>
                          <v-col cols="12" sm="6" md="3">
                            <p><strong>Source Account:</strong></p>
                            <p>{{ item.source_account_number }}</p>
                          </v-col>
                        </v-row>
                        <v-row>
                          <v-col cols="12" sm="6">
                            <p><strong>Message:</strong></p>
                            <p>{{ item.message }}</p>
                          </v-col>
                          <v-col cols="12" sm="6">
                            <p><strong>Processing Code:</strong></p>
                            <p>{{ item.processing_code }}</p>
                          </v-col>
                        </v-row>
                      </v-container>
                    </td>
                  </tr>
                </template>
              </v-data-table>
            </v-col>
          </v-row>

          <!-- Empty State -->
          <v-row v-if="!transactionsLoading && transactions.length === 0 && selectedDate">
            <v-col cols="12">
              <v-empty-state
                headline="Aucune transaction"
                :description="`Aucune transaction trouvée pour le ${selectedDate}`"
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
  fetchTransactions
} = usePowerCardImport()

const selectedDate = ref('')
const transactionsLoading = ref(false)
const transactions = ref([])

const headers = [
  { title: 'Reference', key: 'reference', width: 120 },
  { title: 'PAN', key: 'pan', width: 150 },
  { title: 'Date/Heure', key: 'local_time', width: 180 },
  { title: 'Montant', key: 'transaction_amount', width: 120 },
  { title: 'Action', key: 'action', width: 120 },
  { title: 'Terminal', key: 'terminal_no', width: 80 }
]

const formatAmount = (amount) => {
  if (!amount) return '0 MGA'
  return `${amount} MGA`
}

const formatDateTime = (dateTime) => {
  if (!dateTime) return '-'
  try {
    const date = new Date(dateTime)
    return date.toLocaleString('fr-FR')
  } catch {
    return dateTime
  }
}

const loadTransactions = async () => {
  if (!selectedDate.value) {
    alert('Veuillez sélectionner une date')
    return
  }

  transactionsLoading.value = true
  try {
    const data = await fetchTransactions(selectedDate.value, 1000, 0)
    transactions.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('Erreur chargement transactions:', error)
    transactions.value = []
  } finally {
    transactionsLoading.value = false
  }
}

onMounted(() => {
  setApiUrl(api)
})
</script>

<style scoped>
.power-card-transactions {
  padding: 16px;
}

.expansion-row {
  background-color: #f5f5f5;
}
</style>
