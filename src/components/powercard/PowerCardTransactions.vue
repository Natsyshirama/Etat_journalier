<template>
  <div class="power-card-transactions">
    <v-card>
      <v-card-title>
        <v-icon>mdi-table</v-icon>
        Transactions Power Card
      </v-card-title>
      <v-row class="mb-4">
          <v-col cols="12">
            <v-alert
              v-if="lastLocalTime"
              dense
              border="left"
              
            >
              Dernier `local_time` PowerCard : {{ lastLocalTime }}
            </v-alert>

            <v-alert
              v-else
              type="warning"
              dense
              border="left"
              
            >
              Aucun `local_time` PowerCard disponible pour le moment
            </v-alert>
          </v-col>
        </v-row>
      <v-card-text>
        <v-container>
          <!-- Filters -->
          <v-row class="mb-2" dense>
            <v-col cols="12" sm="4" md="3">
              <v-text-field
                v-model="selectedDate"
                type="date"
                label="Date"
                outlined
                dense
                :required="true"
              />
            </v-col>
            <v-col cols="12" sm="4" md="3">
              <v-text-field
                v-model="selectedEndDate"
                type="date"
                label="Date fin"
                outlined
                dense
              />
            </v-col>
            <v-col cols="12" sm="4" md="2">
              <v-btn
                color="primary"
                :loading="transactionsLoading"
                @click="loadTransactions"
                block
                size="small"
              >
                <v-icon start>mdi-refresh</v-icon>
                Charger
              </v-btn>
            </v-col>
            
          </v-row>

          <!-- Processing Code and Action Filters -->
          <v-row class="mb-4">
            <v-col cols="12" sm="6" md="3">
              <v-select
                v-model="selectedProcessingCode"
                :items="processingCodeOptions"
                label="Processing Code"
                dense
                outlined
                clearable
              />
            </v-col>
            <v-col cols="12" sm="6" md="3">
              <v-select
                v-model="selectedAction"
                :items="actionOptions"
                label="Action"
                dense
                outlined
                clearable
              />
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
              <div style="height: 500px; overflow-y: auto; overflow-x: auto; border: 1px solid #e0e0e0; border-radius: 4px;">
                <v-data-table
                  :headers="headers"
                  :items="filteredTransactions"
                  :loading="transactionsLoading"
                  :items-per-page="10"
                  dense
                  class="elevation-1"
                  style="min-height: 500px;"
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
              </div>
            </v-col>
          </v-row>

          <!-- Empty State -->
          <v-row v-if="!transactionsLoading && transactions.length === 0 && selectedDate">
            <v-col cols="12">
              <v-empty-state
                headline="Aucune transaction"
                :description="selectedEndDate
                  ? `Aucune transaction trouvée entre ${selectedDate} et ${selectedEndDate}`
                  : `Aucune transaction trouvée pour le ${selectedDate}`"
                icon="mdi-database-off"
              />
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
      <!-- Afficher les messages d'erreur/succès -->
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
  </div>
</template>

<script setup>
import { ref, inject, onMounted,computed } from 'vue'
import { usePowerCardImport } from '../../composables/usePowerCardImport'

const api = inject('api')
const {
  setApiUrl,
  fetchTransactions,
  fetchLastLocalTime,
  lastLocalTime,
  message,        // <-- AJOUTER
  messageType,
  clearMessage 
} = usePowerCardImport()

const selectedProcessingCode = ref('')
const selectedAction = ref('')
const processingCodeOptions = ref(['WITHDRAWAL', 'Authentication Request', 'Balance Inquiry', 'Short statement request'])
const actionOptions = ref(['Approved', 'Canceled', 'Reversal accepted','Rejected','No sufficient funds',])

const selectedDate = ref('')
const selectedEndDate = ref('')
const transactionsLoading = ref(false)
const transactions = ref([])

const headers = [
  { title: 'Reference', key: 'reference', width: 90 },
  { title: 'PAN', key: 'pan', width: 110 },
  { title: 'Processing Code', key: 'processing_code', width: 100 },
  { title: 'Action', key: 'action', width: 90 },
  { title: 'Date/Heure', key: 'local_time', width: 140 },
  { title: 'Montant', key: 'transaction_amount', width: 100 },
  { title: 'Terminal', key: 'terminal_no', width: 80 },
  { title: 'Import Date', key: 'import_date', width: 100 }
]



const formatAmount = (amount) => {
  if (!amount) return '0 MGA'
  return `${amount}`
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
    alert('Veuillez sélectionner une date de début')
    return
  }
  clearMessage()  

  transactionsLoading.value = true
  try {
    const data = await fetchTransactions(
      selectedDate.value,
      selectedEndDate.value || null,
      1000,
      0
    )
    transactions.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('Erreur chargement transactions:', error)
    transactions.value = []
  } finally {
    transactionsLoading.value = false
  }
}

const filteredTransactions = computed(() => {
  return transactions.value.filter(item => {
    if (selectedProcessingCode.value && item.processing_code !== selectedProcessingCode.value) {
      return false
    }
    if (selectedAction.value && item.action !== selectedAction.value) {
      return false
    }
    return true
  })
})

onMounted(() => {
  setApiUrl(api)
  fetchLastLocalTime()
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

