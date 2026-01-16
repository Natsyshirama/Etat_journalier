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
        <v-card-title class="text-subtitle-1 d-flex justify-space-between align-center">
          <div>
            <v-icon left>{{ activeTab === 0 ? 'mdi-calendar-today' : 'mdi-calendar-month' }}</v-icon>
            {{ activeTab === 0 ? 'Totaux journaliers' : 'Totaux mensuels' }}
          </div>
          <v-btn 
            v-if="showChartButton"
            small 
            color="primary" 
            @click="showOverallChart"
            class="ml-2"
          >
            <v-icon left small>mdi-chart-line</v-icon>
            Voir graphique global
          </v-btn>
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
              <div class="date-cell">
                {{ item.displayDate || item.date }}
                <v-btn 
                  small 
                  text 
                  color="primary" 
                  @click="showEvolutionChart(item.date, item.total, 'daily')"
                  class="chart-btn"
                >
                  <v-icon x-small>mdi-chart-line</v-icon>
                </v-btn>
              </div>
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
              <div class="date-cell">
                {{ formatMonth(item.month) }}
                <v-btn 
                  small 
                  text 
                  color="primary" 
                  @click="showEvolutionChart(item.month, item.total, 'monthly')"
                  class="chart-btn"
                >
                  <v-icon x-small>mdi-chart-line</v-icon>
                </v-btn>
              </div>
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

    <v-dialog v-model="showChart" max-width="1400px" scrollable>
      <v-card>
        <v-card-title class="headline">
          <v-icon left>mdi-chart-line</v-icon>
          {{ chartTitle }}
          <v-spacer></v-spacer>
          <v-btn icon @click="showChart = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        
        <v-card-text>
          <div v-if="chartData.type === 'daily' && chartData.label" class="text-subtitle-1 mb-4">
            <strong>Date sélectionnée :</strong> {{ formatDateForChart(chartData.label) }}
          </div>
          <div v-else-if="chartData.type === 'monthly' && chartData.label" class="text-subtitle-1 mb-4">
            <strong>Mois sélectionné :</strong> {{ formatMonth(chartData.label) }}
          </div>
          
          <div class="chart-container">
            <canvas ref="chartCanvas"></canvas>
          </div>
          
          <v-card class="mt-4" outlined>
            <v-card-text>
              <div v-if="chartData.type === 'overall'" class="text-center">
                <strong>Graphique global {{ activeTab === 0 ? 'journalier' : 'mensuel' }}</strong>
                <div class="mt-2">
                  <v-icon small color="blue">mdi-information</v-icon>
                  Visualisation de toutes les périodes disponibles
                </div>
              </div>
              <div v-else class="d-flex justify-space-between">
                <div>
                  <strong>Total :</strong> {{ formatCurrency(chartData.total) }}
                </div>
                <div v-if="chartData.ecart !== 0" :class="getEcartClass(chartData.ecart)">
                  <strong>Écart :</strong> {{ formatEcart(chartData.ecart) }}
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="showChart = false">
            Fermer
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from "vue"
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

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
const activeTab = ref(0)
const showChart = ref(false)
const chartCanvas = ref(null)
let chartInstance = null

const chartData = ref({
  type: 'overall', // 'daily monthly overall'
  label: '',
  total: 0,
  ecart: 0,
  evolutionData: []
})

const headers = computed(() =>
  props.columns.map(col => ({
    title: col,
    key: col
  }))
)

const pageCount = computed(() =>
  Math.ceil(filteredRows.value.length / itemsPerPage.value)
)


const chartTitle = computed(() => {
  if (chartData.value.type === 'overall') {
    return `Évolution ${activeTab.value === 0 ? 'journalière' : 'mensuelle'} globale`
  } else {
    return `Évolution ${chartData.value.type === 'daily' ? 'journalière' : 'mensuelle'}`
  }
})
//quelle boutton on affiche
const showChartButton = computed(() => {
  if (activeTab.value === 0) {
    return dailyTotals.value.length > 0
  } else {
    return monthlyTotals.value.length > 0
  }
})

const filteredRows = computed(() => {
  let result = props.rows || []

  if (props.selectedMonth) {
    result = result.filter(row => {
      if (!row.Date) return false
      const parts = row.Date.split("/")
      if (parts.length < 2) return false
      const [year, month] = parts
      return `${year}-${month.padStart(2, "0")}` === props.selectedMonth
    })
  }
  
  if (props.selectedType) {
    const wanted = String(props.selectedType).trim().toUpperCase()
    result = result.filter(row => {
      const t = row.Type ?? row.type ?? ""
      return String(t).trim().toUpperCase() === wanted
    })
  }

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

const formatDateForChart = (dateStr) => {
  if (!dateStr) return "Date inconnue"
  
  const parts = dateStr.split("/")
  if (parts.length === 3) {
    return `${parts[2]}/${parts[1]}/${parts[0]}`
  }
  return dateStr
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

//graphe evolution
const showEvolutionChart = (label, total, type) => {
  chartData.value = {
    type: type,
    label: label,
    total: total,
    ecart: 0,
    evolutionData: []
  }

  if (type === 'daily') {
    const dailyData = dailyTotals.value
    const index = dailyData.findIndex(item => item.date === label)
    
    if (index >= 0) {
      if (index > 0) {
        chartData.value.ecart = dailyData[index].total - dailyData[index - 1].total
      }
      
      const start = Math.max(0, index - 10)
      const end = Math.min(dailyData.length, index + 11)
      
      chartData.value.evolutionData = dailyData
        .slice(start, end)
        .map(item => ({
          label: item.displayDate || item.date,
          value: item.total
        }))
    }
  } else {
    const monthlyData = monthlyTotals.value
    const index = monthlyData.findIndex(item => item.month === label)
    
    if (index >= 0) {
      if (index > 0) {
        chartData.value.ecart = monthlyData[index].total - monthlyData[index - 1].total
      }
      
      const start = Math.max(0, index - 5)
      const end = Math.min(monthlyData.length, index + 5)
      
      chartData.value.evolutionData = monthlyData
        .slice(start, end)
        .map(item => ({
          label: formatMonth(item.month),
          value: item.total
        }))
    }
  }
  
  showChart.value = true
  
  if (chartInstance) {
    chartInstance.destroy()
  }
  
  nextTick(() => {
    createChart()
  })
}

//graphe global
const showOverallChart = () => {
  if (activeTab.value === 0) {
    // daily
    const dailyData = dailyTotals.value
    
    chartData.value = {
      type: 'overall',
      label: '',
      total: 0,
      ecart: 0,
      evolutionData: dailyData.map(item => ({
        label: item.displayDate || item.date,
        value: item.total
      }))
    }
  } else {
    //mensuel
    const monthlyData = monthlyTotals.value
    
    chartData.value = {
      type: 'overall',
      label: '',
      total: 0,
      ecart: 0,
      evolutionData: monthlyData.map(item => ({
        label: formatMonth(item.month),
        value: item.total
      }))
    }
  }
  
  showChart.value = true
  
  if (chartInstance) {
    chartInstance.destroy()
  }
  
  nextTick(() => {
    createChart()
  })
}

//creation de la graphe
const createChart = () => {
  if (!chartCanvas.value) return
  
  const ctx = chartCanvas.value.getContext('2d')
  
  const labels = chartData.value.evolutionData.map(item => item.label)
  const data = chartData.value.evolutionData.map(item => item.value)
  
  
  let backgroundColors
  let borderColors
  
  if (chartData.value.type === 'overall') {
    backgroundColors = labels.map(() => 'rgba(54, 162, 235, 0.8)')
    borderColors = labels.map(() => 'rgb(54, 162, 235)')
  } else {
    const selectedIndex = chartData.value.evolutionData.findIndex(
      item => item.label === (chartData.value.type === 'daily' 
        ? chartData.value.label 
        : formatMonth(chartData.value.label))
    )
    
    backgroundColors = labels.map((_, index) => 
      index === selectedIndex ? 'rgba(54, 162, 235, 0.8)' : 'rgba(201, 203, 207, 0.8)'
    )
    
    borderColors = labels.map((_, index) => 
      index === selectedIndex ? 'rgb(54, 162, 235)' : 'rgb(201, 203, 207)'
    )
  }
  
  chartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Montant total',
        data: data,
        backgroundColor: backgroundColors,
        borderColor: borderColors,
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        title: {
          display: true,
          text: chartTitle.value
        },
        tooltip: {
          callbacks: {
            label: function(context) {
              return `Total: ${formatCurrency(context.raw)}`
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: function(value) {
              return formatCurrency(value)
            }
          }
        },
        x: {
          ticks: {
            maxRotation: chartData.value.type === 'daily' ? 45 : 0,
            minRotation: chartData.value.type === 'daily' ? 45 : 0
          }
        }
      }
    }
  })
}


onUnmounted(() => {
  if (chartInstance) {
    chartInstance.destroy()
  }
})

watch(showChart, (newValue) => {
  if (!newValue && chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
})
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
  background-color: #6a6969;
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

.date-cell {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-btn {
  min-width: 30px !important;
  height: 24px !important;
  padding: 0 4px !important;
}

.chart-container {
  position: relative;
  height: 630px;
  width: 100%;
}

/* Styles pour le bouton graphique principal */
.v-btn--icon.v-size--small .v-icon {
  font-size: 16px;
}
</style>