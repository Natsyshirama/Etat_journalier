<template>
  <div class="table-wrapper">
    <div class="table-search-bar">
      <v-text-field
        v-model="search"
        label="Rechercher"
        clearable
        dense
        hide-details
      />
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

    <!-- Tableau des totaux journaliers basé sur filteredRows -->
    <div v-if="showTotal" class="summary-table mt-4">
      <v-card outlined class="pa-2" style="max-height: 900px; overflow-y: auto;">
        <v-card-title class="text-subtitle-1">Totaux journaliers</v-card-title>
        <div style="overflow-y: auto;">
          <v-data-table
            :headers="summaryHeaders"
            :items="dailyTotals"
            dense
            hide-default-footer
            fixed-header
            :items-per-page="dailyTotals.length || 100000"
            height="900px"
          >
            <template v-slot:item.date="{ item }">
              {{ item.displayDate || item.date }}
            </template>
            
            <template v-slot:item.total_ria="{ item }">
              <div class="amount-container">
                <div>{{ formatCurrency(item.total_ria) }}</div>
                <div :class="getEcartClass(item.ecart_ria)" class="ecart-value">
                  {{ formatEcart(item.ecart_ria) }}
                </div>
              </div>
            </template>
            
            <template v-slot:item.total_global="{ item }">
              <div class="amount-container">
                <div>{{ formatCurrency(item.total_global) }}</div>
                <div :class="getEcartClass(item.ecart_global)" class="ecart-value">
                  {{ formatEcart(item.ecart_global) }}
                </div>
              </div>
            </template>
            
            <template v-slot:item.total="{ item }">
              <div class="amount-container">
                <div>{{ formatCurrency(item.total) }}</div>
                <div :class="getEcartClass(item.ecart_total)" class="ecart-value">
                  {{ formatEcart(item.ecart_total) }}
                </div>
              </div>
            </template>
            
            <template v-slot:no-data>
              <v-alert type="info" border="left" color="green" dark>
                Aucune donnée pour les totaux journaliers
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
  // commencer par toutes les lignes
  let result = props.rows || []

  // filtre par mois si sélectionnée
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

  // filtre par agences si une sélection est faite
  if (props.selectedAgences && props.selectedAgences.length > 0) {
    const setAg = new Set(props.selectedAgences.map(s => String(s).trim()))
    result = result.filter(row => {
      // normaliser la valeur venant de la row
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

// Headers pour le tableau de totaux
const summaryHeaders = computed(() => [
  { title: "Date", key: "date" },
  { title: "Total RIA", key: "total_ria", align: "center" },
  { title: "Total GLOBAL", key: "total_global", align: "center" },
  { title: "Total", key: "total", align: "center" }
])

// Calcul des totaux journaliers à partir de filteredRows (réactif)
const dailyTotals = computed(() => {
  const map = new Map()
  const rows = filteredRows.value || []
  
  // D'abord, calculer les totaux pour chaque jour
  for (const row of rows) {
    const dateRaw = row.Date ?? row.date ?? ""
    // normaliser au format YYYYMMDD sans séparation
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
  
  // Convertir en tableau et trier par date décroissante
  const dailyTotalsArray = Array.from(map.values())
    .sort((a, b) => a.date.localeCompare(b.date))
    .map(item => ({
      ...item,
      date: item.displayDate || item.date
    }))
  
  // Calculer les écarts par rapport au jour précédent
  const resultWithEcart = dailyTotalsArray.map((item, index) => {
    const prevItem = dailyTotalsArray[index - 1] // Jour précédent (car trié par ordre décroissant)
    
    return {
      ...item,
      ecart_ria: prevItem ? item.total_ria - prevItem.total_ria : 0,
      ecart_global: prevItem ? item.total_global - prevItem.total_global : 0,
      ecart_total: prevItem ? item.total - prevItem.total : 0
    }
  })
  
  return resultWithEcart
})

// Formater la devise
const formatCurrency = (value) => {
  return value.toLocaleString(undefined, { 
    minimumFractionDigits: 2, 
    maximumFractionDigits: 2 
  })
}

// Formater l'écart avec signe
const formatEcart = (value) => {
  if (value === 0) return "±0.00"
  const sign = value > 0 ? "+" : ""
  return `${sign}${value.toLocaleString(undefined, { 
    minimumFractionDigits: 2, 
    maximumFractionDigits: 2 
  })}`
}

// Obtenir la classe CSS pour l'écart
const getEcartClass = (value) => {
  if (value > 0) return "ecart-positive"
  if (value < 0) return "ecart-negative"
  return "ecart-neutral"
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

/* Styles pour les montants avec écarts */
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
  color: #4caf50; /* Vert */
  background-color: rgba(76, 175, 80, 0.1);
}

.ecart-negative {
  color: #f44336; /* Rouge */
  background-color: rgba(244, 67, 54, 0.1);
}

.ecart-neutral {
  color: #9e9e9e; /* Gris */
}
</style>