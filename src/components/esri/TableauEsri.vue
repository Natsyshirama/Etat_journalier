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

    <div class="table-scroll">
      <v-data-table
        :headers="headers"
        :items="filteredRows"
        :items-per-page="itemsPerPage"
        :page.sync="page"
        class="elevation-1 fixed-header-table"
        :search="search"
        dense
        fixed-header
        height="600px"
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
  months: {
    type: Array,
    default: () => []
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
  if (!props.selectedMonth) return props.rows
  return props.rows.filter(row => {
    if (!row.Date) return false
    const parts = row.Date.split("/")
    if (parts.length < 2) return false
    const [year, month] = parts
    return `${year}-${month.padStart(2, "0")}` === props.selectedMonth
  })
})

watch(
  () => [props.rows, props.selectedMonth],
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

/* 🔍 Barre de recherche fixée */
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

/* 📌 Rendre l'en-tête du tableau fixe */
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

/* ✅ Lignes du tableau avec fond légèrement différent */
.fixed-header-table ::v-deep(td) {
  border-bottom: 1px solid #333;
  padding: 8px 12px;
  font-size: 14px;
  transition: background-color 0.2s ease;
}

/* ✅ Effet au survol pour mieux distinguer la ligne active */
.fixed-header-table ::v-deep(tr:hover td) {
  background-color: #2a2a2a;
  cursor: pointer;
}

</style>
