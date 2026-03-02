<template>
  <div class="table-wrapper">
    <div class="table-search-bar">
      <v-text-field
        v-model="search"
        label="Rechercher"
        clearable
        dense
        hide-details
        class="mx-4 mb-2"
      />
    </div>

    <div class="table-scroll">
      <v-data-table
        :headers="headers"
        :items="rows"
        :items-per-page="itemsPerPage"
        :page.sync="page"
        :search="search"
        class="elevation-1 fixed-header-table"
        dense
        fixed-header
        height="500px"
      >
      <template v-for="col in moneyColumns" :key="col" v-slot:[`item.${col}`]="{ item }">
          <span class="money-cell">{{ formatUSD(item[col]) }}</span>
        </template>

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
  </div>
</template>

<script setup>
import { ref, computed, watch } from "vue"
import { formatUSD } from "@/composables/format_money.js"

const props = defineProps({
  columns: {
    type: Array,
    required: true
  },
  rows: {
    type: Array,
    required: true
  },
  // Optionnel: spécifier manuellement les colonnes de montant
  moneyColumnsProp: {
    type: Array,
    default: () => []
  }
})

const search = ref("")
const page = ref(1)
const itemsPerPage = ref(20)

// Détection automatique des colonnes qui contiennent des montants
const moneyColumns = computed(() => {
  if (props.moneyColumnsProp.length > 0) {
    return props.moneyColumnsProp
  }
  
  // Mots-clés pour identifier les colonnes de montant
  const moneyKeywords = [
    'MONTANT', 'montant', 'MONTANT_', 'montant_',
    'EUR_', 'USD_', 'Total_', 'total_',
    'CAPITAL', 'capital', 'PAY', 'pay',
    'PRIX', 'prix', 'COUT', 'cout',
    'MGA', 'Ar', 'ARIARY'
  ]
  
  return props.columns.filter(col => 
    moneyKeywords.some(keyword => col.includes(keyword))
  )
})

// Formater une valeur monétaire
const formatMoneyValue = (value) => {
  if (value === null || value === undefined || value === '') return ''
  
  // Si c'est déjà une chaîne formatée, la retourner
  if (typeof value === 'string' && (value.includes(',') || value.includes('.'))) {
    return value
  }
  
  // Convertir en nombre et formater
  const num = parseFloat(value)
  if (isNaN(num)) return value
  
  return formatUSD(num, 2)
}

// Créer une version formatée des lignes pour l'affichage
const formattedRows = computed(() => {
  return props.rows.map(row => {
    const newRow = { ...row }
    moneyColumns.value.forEach(col => {
      if (row[col] !== undefined) {
        newRow[col] = formatMoneyValue(row[col])
      }
    })
    return newRow
  })
})

const headers = computed(() =>
  props.columns.map(col => ({
    title: col,
    key: col,
     }))
)

const pageCount = computed(() =>
  Math.ceil(props.rows.length / itemsPerPage.value)
)

watch(
  () => props.rows,
  () => (page.value = 1)
)
</script>

<style scoped>
.table-wrapper {
   display: flex;
  flex-direction: column;
  width: 100%;
  overflow: hidden;
  max-width: 100%;
  height: 900px;
}

.table-search-bar {
  position: sticky;
  top: 0;
  z-index: 20;
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
  cursor: pointer;
}
/* Style pour les cellules de montant */
.money-cell {
  display: block;
  text-align: right;
  font-family: 'Roboto Mono', monospace;
  font-weight: 500;
}

</style>
