<template>
  <v-container class="unified-container" fluid>
    <!-- Sélecteur de table commun -->
    <!-- <v-row class="mb-4">
      <v-col cols="12" md="6">
        <v-select
          v-model="selectedTable"
          :items="history.map(item => item.label)"
          label="Choisir une table"
          outlined
          dense
        />
      </v-col>
    </v-row> -->

    <!-- Résumé conditionnel selon l'onglet -->
    <ResumerDat v-if="selectedTable && activeTab === 0" :tableName="selectedTable" />
    <ResumerDav v-if="selectedTable && activeTab === 1" :tableName="selectedTable" />
    <ResumerEpr v-if="selectedTable && activeTab === 2" :tableName="selectedTable" />
    <!-- Onglets DAT/DAV -->
    <v-tabs v-model="activeTab" class="mb-4">
      <v-tab>DAT</v-tab>
      <v-tab>DAV</v-tab>
      <v-tab>EPR</v-tab>
    </v-tabs>

    <!-- Boutons Tableau/Dashboard -->
    <v-row class="mb-4">
      <v-col cols="12" md="6">
        <v-btn
          color="primary"
          class="mr-2"
          @click="displayComponent = 'tableau'"
          :outlined="displayComponent !== 'tableau'"
        >
          Tableau
        </v-btn>
        <v-btn
          color="primary"
          @click="displayComponent = 'dashboard'"
          :outlined="displayComponent !== 'dashboard'"
        >
          Dashboard
        </v-btn>
      </v-col>
    </v-row>

    <!-- Contenu des onglets -->
    <v-window v-model="activeTab">
      <!-- Onglet DAT -->
      <v-window-item>
        <div v-if="selectedTable">
          <TableauDat
            v-if="displayComponent === 'tableau'"
            :tableName="selectedTable"
          />
          
          <DatGraphe
            v-if="displayComponent === 'dashboard'"
            :tableName="selectedTable"
          />
        </div>
      </v-window-item>

      <!-- Onglet DAV -->
      <v-window-item>
        <div v-if="selectedTable">
          <TableauDav
            v-if="displayComponent === 'tableau'"
            :tableName="selectedTable"
          />
          <DashboardDav
            v-if="displayComponent === 'dashboard'"
            :tableName="selectedTable"
          />
          
        </div>
      </v-window-item>
      
      <!-- Onglet EPR -->
      
      <v-window-item>
        <div v-if="selectedTable">
          <TableauEpr
            v-if="displayComponent === 'tableau'"
            :tableName="selectedTable"
          />
          
          <EprGraphe
            v-if="displayComponent === 'dashboard'"
            :tableName="selectedTable"
          />
        </div>
      </v-window-item>
    </v-window>

    <!-- Alerte si aucune table sélectionnée -->
    <v-alert
      v-if="!selectedTable"
      type="info"
      border="left"
      color="blue"
      dark
      class="mb-4"
    >
      Sélectionnez une table pour afficher les données
    </v-alert>
  </v-container>
</template>
<script setup>
import { ref, onMounted, watch, onUnmounted } from "vue"
import axios from "axios"
import * as XLSX from "xlsx"
import { usePopupStore } from '@/stores'
const popupStore = usePopupStore()


// Composants DAT
import ResumerDat from "@/components/dat/ResumerDat.vue"
import TableauDat from "@/components/dat/TableauDat.vue"
import DatGraphe from "@/components/dat/DatGraphe.vue"

// Composants DAV
import ResumerDav from "@/components/dav/ResumerDav.vue"
import TableauDav from "@/components/dav/TableauDav.vue"
import DashboardDav from "@/components/dav/DavGraphe.vue" 

// Composants EPR
import ResumerEpr from "@/components/epr/resumerEpr.vue"
import TableauEpr from "@/components/epr/TableauEpr.vue"
import EprGraphe from "@/components/epr/EprGraphe.vue"

const history = ref([])
const selectedTable = ref(null)
const activeTab = ref(0)
const displayComponent = ref("tableau")

// config
const exportConfig = {
  'DAV': { 
    apiEndpoint: 'dav', 
    sheetName: 'DAV Data',
    fileNamePrefix: 'dav'
  },
  'DAT': { 
    apiEndpoint: 'dat', 
    sheetName: 'DAT Data',
    fileNamePrefix: 'dat'
  },
  'EPR': { 
    apiEndpoint: 'epr', 
    sheetName: 'EPR Data',
    fileNamePrefix: 'epr'
  }
}

// Fonction export
const exportToExcel = async (type) => {
  if (!selectedTable.value) {
    alert('Aucune table sélectionnée')
    return
  }

  const config = exportConfig[type]
  if (!config) {
    console.error(`Type d'export non supporté: ${type}`)
    return
  }

  try {
    const res = await axios.get(`http://127.0.0.1:8000/api/${config.apiEndpoint}/${selectedTable.value}`)
    const data = res.data.data || []
    const columns = res.data.columns || []

    if (!data.length) {
      alert('Aucune donnée à exporter')
      return
    }

    const dataToExport = data.map(row => {//emplacement data avec row ASSURER ordre colonnes
      const exportedRow = {}
      columns.forEach(col => {
        exportedRow[col] = row[col] ?? "" 
      })
      return exportedRow
    })

    const wb = XLSX.utils.book_new()
    const ws = XLSX.utils.json_to_sheet(dataToExport)
    XLSX.utils.book_append_sheet(wb, ws, config.sheetName)
    
    const fileName = `${config.fileNamePrefix}_${selectedTable.value}.xlsx`
    XLSX.writeFile(wb, fileName)
    
    console.log(`Export ${type} Excel réussi !`)
    
  } catch (error) {
    console.error(`Erreur lors de l'export ${type} Excel:`, error)
    alert(`Erreur lors de l'export ${type} Excel`)
  }
}

// gerer evenement export
const handleExportEvent = (event) => {
  const type = event.detail.type //attend le type envoier par menu_bar
  if (exportConfig[type]) {
    exportToExcel(type)
  } else {
    console.warn('Type d\'export non reconnu:', type)
  }
}

// Fonctions  pour chaque type 
const exportDavToExcel = () => exportToExcel('DAV')
const exportDatToExcel = () => exportToExcel('DAT')
const exportEprToExcel = () => exportToExcel('EPR')


const handleDateSelection = (event) => {
  selectedTable.value = event.detail.date
  console.log("📅 Table sélectionnée via event:", selectedTable.value)
}
onMounted(() => {
  window.addEventListener('export-dav-data', handleExportEvent)
  window.addEventListener('table-date-selected', handleDateSelection) // ✅ Nouvel écouteur
  fetchTables() 
})

onUnmounted(() => {
  window.removeEventListener('export-dav-data', handleExportEvent)
  window.removeEventListener('table-date-selected', handleDateSelection) // ✅ Nettoyage
})

const fetchTables = async () => {
  try {
    const res = await axios.get("http://127.0.0.1:8000/api/history/liste")
    history.value = res.data.history || []
  } catch (err) {
    console.error("Erreur lors du chargement de l'history:", err)
  }
}

watch(() => popupStore.selected_date, (newDate) => {
    console.log("🔄 Store updated - selected_date:", newDate)

  if (newDate) {
    selectedTable.value = newDate
    console.log("📅 Table sélectionnée via store:", selectedTable.value)
  }
}, { immediate: true })


</script>

<style scoped>
.unified-container {
  max-height: 90vh;
  overflow-y: auto;
  padding-bottom: 20px;
}
</style>