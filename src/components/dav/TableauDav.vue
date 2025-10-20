<template>
  <div style="max-height: 600px; overflow-y: auto;">
    <v-data-table
      :headers="headers"
      :items="items"
      :items-per-page="itemsPerPage"
      :page.sync="page"
      class="elevation-1"
      :search="search"
      dense
    >
      <template v-slot:top>
        <v-text-field
          v-model="search"
          label="Rechercher"
          class="mx-4"
          clearable
          dense
        />
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
        <v-alert type="info" border="left" color="blue" dark>
          Aucune donnée trouvée
        </v-alert>
      </template>
    </v-data-table>
  </div>
</template>

<script setup>
import { ref, watch, computed, onMounted, onUnmounted } from "vue"
import axios from "axios"
import * as XLSX from "xlsx"

// Props : tableName choisi dans dat.vue
const props = defineProps({
  tableName: {
    type: String,
    required: true
  }
})

const headers = ref([])
const items = ref([])
const search = ref("")
const page = ref(1)
const itemsPerPage = ref(10)

const pageCount = computed(() =>
  Math.ceil(items.value.length / itemsPerPage.value)
)
const fetchTableData = async (tableName) => {
  if (!tableName) {
    items.value = []
    headers.value = []
    return
  }
  try {
    const res = await axios.get(`http://127.0.0.1:8000/api/dav/${tableName}`)
    console.log("Réponse API:", res.data)

    items.value = res.data.data || []  // <-- ici
    headers.value = (res.data.columns || []).map((col) => ({
      title: col,
      key: col
    }))
    page.value = 1
  } catch (err) {
    console.error("Erreur lors du chargement de la table:", err)
  }
}

const exportToExcel = () => {
  if (!items.value.length) {
    alert('Aucune donnée à exporter')
    return
  }

  try {
    // Préparer les données pour l'export
    const dataToExport = items.value.map(row => {
      const exportedRow = {}
      headers.value.forEach(header => {
        exportedRow[header.title] = row[header.key] || ""
      })
      return exportedRow
    })

    // Créer un workbook
    const wb = XLSX.utils.book_new()
    const ws = XLSX.utils.json_to_sheet(dataToExport)
    
    // Ajouter la worksheet au workbook
    XLSX.utils.book_append_sheet(wb, ws, "DAV Data")
    
    // Générer le nom du fichier avec la table
    const fileName = `dav_${props.tableName}.xlsx`
    
    // Télécharger le fichier
    XLSX.writeFile(wb, fileName)
    
    console.log('Export DAV Excel réussi !')
    
  } catch (error) {
    console.error("Erreur lors de l'export Excel:", error)
    alert("Erreur lors de l'export Excel")
  }
}

const handleExportEvent = (event) => {
  if (event.detail.type === 'DAV') {
    exportToExcel()
  }
}

onMounted(() => {
  window.addEventListener('export-dav-data', handleExportEvent)
})

onUnmounted(() => {
  window.removeEventListener('export-dav-data', handleExportEvent)
})
watch(
  () => props.tableName,
  (newVal) => {
    fetchTableData(newVal)
  },
  { immediate: true }
)
</script>
