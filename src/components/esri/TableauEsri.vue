<template>
  <div class="table-wrapper">
    <div class="table-search-bar">
      <div class="d-flex justify-space-between align-center">
        <v-text-field
          v-model="search"
          label="Rechercher"
          clearable
          dense
          hide-details
          style="max-width: 300px;"
        />
        
        <div v-if="showTotal" class="navigation-tabs">
          <v-tabs v-model="activeTab" background-color="transparent" center-active>
            <v-tab @click="switchToDaily">
              <v-icon left small>mdi-calendar-today</v-icon>
              Journalier
            </v-tab>
            <v-tab @click="switchToMonthly">
              <v-icon left small>mdi-calendar-month</v-icon>
              Mensuel
            </v-tab>
          </v-tabs>
        </div>
      </div>
    </div>

    <div v-if="!showTotal" class="table-scroll">
      <v-data-table
        :headers="headers"
        :items="filteredRows"
        :items-per-page="itemsPerPage"
        :page.sync="page"
        class="elevation-1 fixed-header-table"
        :search="search"
        dense
        fixed-header
        height="900px"
      >
        <template v-slot:footer>
          <v-pagination
            v-model="page"
            :length="pageCount"
            circle
            class="my-2"
          />
        </template>

        <template v-slot:no-data>
          <v-alert type="info" border="left" color="green" dark>
            Aucune donnée trouvée
          </v-alert>
        </template>
      </v-data-table>
    </div>

    <div v-if="showTotal" class="summary-table mt-4">
      <v-card outlined class="pa-2" style="max-height: 900px; overflow-y: auto;">
        <v-card-title class="text-subtitle-1">
          <v-icon left>{{ activeTab === 0 ? 'mdi-calendar-today' : 'mdi-calendar-month' }}</v-icon>
          {{ activeTab === 0 ? 'Totaux journaliers' : 'Totaux mensuels' }}
        </v-card-title>
        <div style="overflow-y: auto;">
          <v-data-table
            :headers="activeTab === 0 ? summaryHeaders : monthlyHeaders"
            :items="activeTab === 0 ? dailyTotals : monthlyTotals"
            dense
            hide-default-footer
            fixed-header
            :items-per-page="(activeTab === 0 ? dailyTotals : monthlyTotals).length || 100000"
            height="900px"
          >
            <template v-if="activeTab === 0" v-slot:item.date="{ item }">
              {{ item.displayDate || item.date }}
            </template>
            
            <template v-if="activeTab === 0" v-slot:item.total_ria="{ item }">
              <div class="amount-container">
                <div>{{ formatCurrency(item.total_ria) }}</div>
                <div :class="getEcartClass(item.ecart_ria)" class="ecart-value">
                  {{ formatEcart(item.ecart_ria) }}
                </div>
              </div>
            </template>
            
            <template v-if="activeTab === 0" v-slot:item.total_global="{ item }">
              <div class="amount-container">
                <div>{{ formatCurrency(item.total_global) }}</div>
                <div :class="getEcartClass(item.ecart_global)" class="ecart-value">
                  {{ formatEcart(item.ecart_global) }}
                </div>
              </div>
            </template>
            
            <template v-if="activeTab === 0" v-slot:item.total="{ item }">
              <div class="amount-container">
                <div>{{ formatCurrency(item.total) }}</div>
                <div :class="getEcartClass(item.ecart_total)" class="ecart-value">
                  {{ formatEcart(item.ecart_total) }}
                </div>
              </div>
            </template>
            
            <template v-if="activeTab === 1" v-slot:item.month="{ item }">
              {{ formatMonth(item.month) }}
            </template>
            
            <template v-if="activeTab === 1" v-slot:item.total_ria="{ item }">
              <div class="amount-container">
                <div>{{ formatCurrency(item.total_ria) }}</div>
                <div :class="getEcartClass(item.ecart_ria)" class="ecart-value">
                  {{ formatEcart(item.ecart_ria) }}
                </div>
              </div>
            </template>
            
            <template v-if="activeTab === 1" v-slot:item.total_global="{ item }">
              <div class="amount-container">
                <div>{{ formatCurrency(item.total_global) }}</div>
                <div :class="getEcartClass(item.ecart_global)" class="ecart-value">
                  {{ formatEcart(item.ecart_global) }}
                </div>
              </div>
            </template>
            
            <template v-if="activeTab === 1" v-slot:item.total="{ item }">
              <div class="amount-container">
                <div>{{ formatCurrency(item.total) }}</div>
                <div :class="getEcartClass(item.ecart_total)" class="ecart-value">
                  {{ formatEcart(item.ecart_total) }}
                </div>
              </div>
            </template>
            
            <template v-slot:no-data>
              <v-alert type="info" border="left" color="green" dark>
                Aucune donnée pour {{ activeTab === 0 ? 'les totaux journaliers' : 'les totaux mensuels' }}
              </v-alert>
            </template>
          </v-data-table>
        </div>
      </v-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from "vue"
 
const props = defineProps({
  columns: {
    type: Array,
    required: true
  },
  rows: {
    type: Array,
    required: true
  },
  selectedMonth: {
    type: String,
    default: ""
  },
  selectedAgences: {
    type: Array,
    default: () => []
  },
  selectedType: {
    type: String,
    default: ""
  },
  months: {
    type: Array,
    default: () => []
  },
  showTotal: {
    type: Boolean,
    default: false
  }
})

const search = ref("")
const page = ref(1)
const itemsPerPage = ref(20)
const activeTab = ref(0) // 0 = journ, 1 = mensuel

const headers = computed(() =>
  props.columns.map(col => ({
    title: col,
    key: col
  }))
)

const pageCount = computed(() =>
  Math.ceil(filteredRows.value.length / itemsPerPage.value)
)

const filteredRows = computed(() => {
  let result = props.rows || []

  // filtre par mois 
  if (props.selectedMonth) {
    result = result.filter(row => {
      if (!row.Date) return false
      const parts = row.Date.split("/")
      if (parts.length < 2) return false
      const [year, month] = parts
      return `${year}-${month.padStart(2, "0")}` === props.selectedMonth
    })
  }
  //filtre type
  if (props.selectedType) {
    const wanted = String(props.selectedType).trim().toUpperCase()
    result = result.filter(row => {
      const t = row.Type ?? row.type ?? ""
      return String(t).trim().toUpperCase() === wanted
    })
  }

  // filtre par agences 
  if (props.selectedAgences && props.selectedAgences.length > 0) {
    const setAg = new Set(props.selectedAgences.map(s => String(s).trim()))
    result = result.filter(row => {

      const agenceCodeRaw = row.Agence ?? row.agence ?? row.AGENCY
      if (!agenceCodeRaw) return false
      const agenceCode = String(agenceCodeRaw).trim()
      return setAg.has(agenceCode)
    })
  }

  return result
})

watch(
  () => [props.rows, props.selectedMonth, props.selectedAgences,props.selectedType],
  () => (page.value = 1)
)

const summaryHeaders = computed(() => [
  { title: "Date", key: "date" },
  { title: "Total RIA", key: "total_ria", align: "center" },
  { title: "Total GLOBAL", key: "total_global", align: "center" },
  { title: "Total", key: "total", align: "center" }
])

const monthlyHeaders = computed(() => [
  { title: "Mois", key: "month" },
  { title: "Total RIA", key: "total_ria", align: "center" },
  { title: "Total GLOBAL", key: "total_global", align: "center" },
  { title: "Total", key: "total", align: "center" }
])

// Calcul 
const dailyTotals = computed(() => {
  const map = new Map()
  const rows = filteredRows.value || []
  
  for (const row of rows) {
    const dateRaw = row.Date ?? row.date ?? ""

    const dateKey = String(dateRaw).replace(/\//g, "").trim() || "unknown"
    const rawAmount = row.Montant ?? row.Amount ?? row.amount ?? 0
    const amount = parseFloat(String(rawAmount).replace(/,/g, "")) || 0
    const type = String(row.Type ?? row.type ?? "").toUpperCase()

    const entry = map.get(dateKey) ?? { 
      date: dateKey, 
      displayDate: dateRaw,
      total_ria: 0, 
      total_global: 0, 
      total: 0 
    }
    
    if (type.includes("RIA")) {
      entry.total_ria += amount
    } else if (type.includes("GLOBAL")) {
      entry.total_global += amount
    }
    entry.total += amount
    map.set(dateKey, entry)
  }
  
  const dailyTotalsArray = Array.from(map.values())
    .sort((a, b) => a.date.localeCompare(b.date))
    .map(item => ({
      ...item,
      date: item.displayDate || item.date
    }))
  
  const resultWithEcart = dailyTotalsArray.map((item, index) => {
    if (index === 0) {
      return {
        ...item,
        ecart_ria: 0,
        ecart_global: 0,
        ecart_total: 0
      }
    }
    
    const prevItem = dailyTotalsArray[index - 1]
    
    return {
      ...item,
      ecart_ria: item.total_ria - prevItem.total_ria,
      ecart_global: item.total_global - prevItem.total_global,
      ecart_total: item.total - prevItem.total
    }
  })
  
  return resultWithEcart
})

const monthlyTotals = computed(() => {
  const map = new Map()
  const rows = filteredRows.value || []
  
  for (const row of rows) {
    const dateRaw = row.Date ?? row.date ?? ""
    if (!dateRaw) continue
    
    const parts = dateRaw.split("/")
    if (parts.length < 2) continue
    const [year, month] = parts
    const monthKey = `${year}-${month.padStart(2, "0")}`
    
    const rawAmount = row.Montant ?? row.Amount ?? row.amount ?? 0
    const amount = parseFloat(String(rawAmount).replace(/,/g, "")) || 0
    const type = String(row.Type ?? row.type ?? "").toUpperCase()

    const entry = map.get(monthKey) ?? { 
      month: monthKey,
      total_ria: 0, 
      total_global: 0, 
      total: 0 
    }
    
    if (type.includes("RIA")) {
      entry.total_ria += amount
    } else if (type.includes("GLOBAL")) {
      entry.total_global += amount
    }
    entry.total += amount
    map.set(monthKey, entry)
  }
  
  const monthlyTotalsArray = Array.from(map.values())
    .sort((a, b) => a.month.localeCompare(b.month))
    .map(item => ({
      ...item,
      displayMonth: formatMonth(item.month)
    }))
  
  const resultWithEcart = monthlyTotalsArray.map((item, index) => {
    if (index === 0) {
      return {
        ...item,
        ecart_ria: 0,
        ecart_global: 0,
        ecart_total: 0
      }
    }
    
    const prevItem = monthlyTotalsArray[index - 1]
    
    return {
      ...item,
      ecart_ria: item.total_ria - prevItem.total_ria,
      ecart_global: item.total_global - prevItem.total_global,
      ecart_total: item.total - prevItem.total
    }
  })
  
  return resultWithEcart
})

const formatMonth = (monthKey) => {
  if (!monthKey) return "Inconnu"
  
  const [year, month] = monthKey.split("-")
  const monthNames = [
    "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
  ]
  
  const monthName = monthNames[parseInt(month) - 1] || month
  return `${monthName} ${year}`
}

const formatCurrency = (value) => {
  return value.toLocaleString(undefined, { 
    minimumFractionDigits: 2, 
    maximumFractionDigits: 2 
  })
}

const formatEcart = (value) => {
  if (value === 0) return "±0.00"
  const sign = value > 0 ? "+" : ""
  return `${sign}${value.toLocaleString(undefined, { 
    minimumFractionDigits: 2, 
    maximumFractionDigits: 2 
  })}`
}

const getEcartClass = (value) => {
  if (value > 0) return "ecart-positive"
  if (value < 0) return "ecart-negative"
  return "ecart-neutral"
}

const switchToDaily = () => {
  activeTab.value = 0
}

const switchToMonthly = () => {
  activeTab.value = 1
}
</script>

<style scoped>
.table-wrapper {
  display: flex;
  flex-direction: column;
  width: 100%;
  overflow: hidden;
  max-width: 100%;
  height: 1000px;
}

.table-search-bar {
  position: sticky;
  top: 0;
  z-index: 20;
  padding: 8px;
  border-bottom: 1px solid #333;
}

.table-search-bar .d-flex {
  gap: 16px;
}

.navigation-tabs {
  flex-shrink: 0;
}

.navigation-tabs ::v-deep(.v-tabs) {
  min-width: 250px;
}

.navigation-tabs ::v-deep(.v-tab) {
  min-width: 120px;
}

.table-scroll {
  flex: 1;
  overflow-y: auto;
}

.fixed-header-table ::v-deep(.v-data-table__wrapper) {
  overflow-y: auto;
  max-height: 500px;
}

.fixed-header-table ::v-deep(th) {
  position: sticky;
  top: 0;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  border-bottom: 2px solid #444;
  border-right: 1px solid #333;
  padding: 10px 12px;
  z-index: 15;
  white-space: nowrap;
}

.fixed-header-table ::v-deep(td) {
  border-bottom: 1px solid #333;
  padding: 8px 12px;
  font-size: 14px;
  transition: background-color 0.2s ease;
}

.fixed-header-table ::v-deep(tr:hover td) {
  background-color: #2a2a2a;
  cursor: pointer;
}

.summary-table ::v-deep(.v-data-table__wrapper) {
  max-height: 350px;
  overflow-y: auto;
}

.summary-table ::v-deep(th) {
  position: sticky;
  top: 0;
  background-color: white;
}

.amount-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.ecart-value {
  font-size: 0.75rem;
  font-weight: 500;
  margin-top: 2px;
  padding: 1px 4px;
  border-radius: 2px;
}

.ecart-positive {
  color: #4caf50; 
  background-color: rgba(76, 175, 80, 0.1);
}

.ecart-negative {
  color: #f44336; 
  background-color: rgba(244, 67, 54, 0.1);
}

.ecart-neutral {
  color: #9e9e9e; 
}
</style>