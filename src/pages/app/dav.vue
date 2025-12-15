<template>
  <v-container class="unified-container" fluid>
    <!-- si pas encore initialiser -->
    <div v-if="selectedTable && isInitialized === 0" class="text-center py-16">
      <v-icon color="warning" size="80" class="mb-4">mdi-database-alert</v-icon>
      <h2 class="text-h5 mb-4">Table non initialisée</h2>
      <p class="text-body-1 mb-6">La table "{{ selectedTable }}" doit être initialisée avant utilisation.</p>
      <v-btn 
        color="primary" 
        size="large"
        @click="goToInitializePage"
        prepend-icon="mdi-cog"
      >
        Initialiser la table
      </v-btn>
    </div>
    
    <div v-else>
      <!-- SECTION GRAPHE GLOBAL AVEC ESPACEMENT -->
      <div class="global-graphe-section mb-6">
        <ResumeGlobalGraphe />
      </div>
      
      <!-- SECTION RESUME PAR TAB -->
      <div class="resumer-section" :class="{'mb-6': displayComponent === 'tableau'}">
        <ResumerDat v-if="selectedTable && activeTab === 0" :tableName="selectedTable" class="tab-resumer" />
        <ResumerDav v-if="selectedTable && activeTab === 1" :tableName="selectedTable" class="tab-resumer" />
        <ResumerEpr v-if="selectedTable && activeTab === 2" :tableName="selectedTable" class="tab-resumer" />
        <ResumerDec v-if="selectedTable && activeTab === 3" :tableName="selectedTable" class="tab-resumer" />
      </div>

      <!-- TABS -->
      <v-tabs v-model="activeTab" class="mb-4 tabs-container">
        <v-tab>DAT</v-tab>
        <v-tab>DAV</v-tab>
        <v-tab>EPR</v-tab>
        <v-tab>DECAISSEMENT</v-tab>
      </v-tabs>

      <!-- Boutons Tableau/Dashboard -->
      <v-row class="mb-4 display-toggle-row">
        <v-col cols="12" md="6">
          <v-btn
            color="success"
            class="mr-2"
            :variant="displayComponent === 'tableau' ? 'flat' : 'outlined'"
            @click="displayComponent = 'tableau'"
          >
            Tableau
          </v-btn>

          <v-btn
            color="success"
            prepend-icon="mdi-chart-line"

            :variant="displayComponent === 'dashboard' ? 'flat' : 'outlined'"
            @click="displayComponent = 'dashboard'"
          >
            Graphe
          </v-btn>
        </v-col>
      </v-row>

      <v-window v-model="activeTab" class="content-window">
        <!--  DAT -->
        <v-window-item>
          <div v-if="selectedTable" class="tab-content">
            <TableauDat
              v-if="displayComponent === 'tableau'"
              :tableName="selectedTable"
              class="tab-component"
            />
            
            <DatGraphe
              v-if="displayComponent === 'dashboard'"
              :tableName="selectedTable"
              class="tab-component"
            />
          </div>
        </v-window-item>

        <!-- Onglet DAV -->
        <v-window-item>
          <div v-if="selectedTable" class="tab-content">
            <TableauDav
              v-if="displayComponent === 'tableau'"
              :tableName="selectedTable"
              class="tab-component"
            />
            <DashboardDav
              v-if="displayComponent === 'dashboard'"
              :tableName="selectedTable"
              class="tab-component"
            />
          </div>
        </v-window-item>
        
        <!-- Onglet EPR -->
        <v-window-item>
          <div v-if="selectedTable" class="tab-content">
            <TableauEpr
              v-if="displayComponent === 'tableau'"
              :tableName="selectedTable"
              class="tab-component"
            />
            
            <EprGraphe
              v-if="displayComponent === 'dashboard'"
              :tableName="selectedTable"
              class="tab-component"
            />
          </div>
        </v-window-item>
        
        <!-- Onglet DECAISSEMENT -->
        <v-window-item>
          <div v-if="selectedTable" class="tab-content">
            <TableauDec
              v-if="displayComponent === 'tableau'"
              :tableName="selectedTable"
              class="tab-component"
            />
            
            <DecGraphe
              v-if="displayComponent === 'dashboard'"
              :tableName="selectedTable"
              class="tab-component"
            />
          </div>
        </v-window-item>
      </v-window>
    </div>
    
    <v-alert
      v-if="!selectedTable"
      type="info"
      border="left"
      color="green"
      dark
      class="mb-4 no-table-alert"
    >
      Sélectionnez une table pour afficher les données
    </v-alert>
  </v-container>
</template>
<script setup>
import { ref, onMounted, watch, onUnmounted , computed, inject} from "vue"
import axios from "axios"
import * as XLSX from "xlsx"
import { usePopupStore } from '@/stores'
const popupStore = usePopupStore()
import { useRouter } from 'vue-router'


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

// Composants decaissement
import ResumerDec from "@/components/decaissement/ResumerDec.vue"
import TableauDec from "@/components/decaissement/TableauDecaiss.vue"
import DecGraphe from "@/components/decaissement/DecGraphe.vue"

import ResumeGlobalGraphe from "@/components/dav/ResulerGlobalGraphe.vue"


const history = ref([])
const selectedTable =  ref(localStorage.getItem("selectedTable") || null)
const activeTab = ref(0)
const displayComponent = ref("tableau")
const router = useRouter()

const api = inject('api') 

//verifier le status
const isInitialized = computed(() => {
  return popupStore.selected_date_stat_compte 
})


// Fonction de redirection
const goToInitializePage = () => {
  router.push('/app/Initialise')
}

watch(() => popupStore.selected_date_stat_compte, (newStat) => {
  isInitialized.value = newStat !== false
  console.log("📊 Statut d'initialisation:", isInitialized.value)
})


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
  },
  'DECAISSEMENT': { 
    apiEndpoint: 'decaissement', 
    sheetName: 'Decaissement Data',
    fileNamePrefix: 'decaissement'
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
    const res = await axios.get(`${api}/api/${config.apiEndpoint}/${selectedTable.value}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
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
    alert(`Erreur lors de l'export ${type} Excel: ${error?.response?.data?.error || error.message}`)
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

const fetchAndSetLatestDate = async () => {
  try {
    const res = await axios.get(`${api}/api/history_insert`)
    const history = res.data.response?.data || []
    
    if (Array.isArray(history) && history.length > 0) {
      // Trier par date décroissante
      const sorted = [...history].sort((a, b) => b.label.localeCompare(a.label))
      const latest = sorted[0]
      
      // Si pas encore de table sélectionnée, prendre la dernière
      if (!selectedTable.value && latest.label) {
        selectedTable.value = latest.label
        popupStore.selected_date = latest.label
        popupStore.selected_date_stat_compte = latest.stat_compte
        localStorage.setItem("selectedTable", latest.label)
        
        console.log("📅 Date automatiquement sélectionnée :", latest.label)
        
        // Émettre l'événement si nécessaire
        window.dispatchEvent(new CustomEvent('table-date-selected', { 
          detail: { 
            date: latest.label,
            stat_compte: latest.stat_compte 
          }
        }))
      }
    }
  } catch (err) {
    console.error("Erreur lors du chargement de l'historique :", err)
  }
}

onMounted(async () => {
  // Synchronise la sélection au chargement
  const savedTable = localStorage.getItem("selectedTable")
  if (savedTable) {
    if (savedTable.startsWith('{') || savedTable.startsWith('[')) {
      console.error("Données corrompues dans localStorage, nettoyage...")
      localStorage.removeItem("selectedTable")
      selectedTable.value = null
    } else {
      selectedTable.value = savedTable
      popupStore.selected_date = savedTable
    }
  }
  
  // get last date si pas de date selectionne
  if (!selectedTable.value) {
    await fetchAndSetLatestDate()
  }
  
  // ecouteur
  window.addEventListener('export-dav-data', handleExportEvent)
  window.addEventListener('table-date-selected', handleDateSelection)
  
  await fetchTables()
})


const handleDateSelection = (event) => {
  
  const dateString = event.detail?.date?.label || event.detail?.date
  const stat = event.detail?.stat_compte
  
  if (dateString) {
    selectedTable.value = dateString
    popupStore.selected_date = dateString
    popupStore.selected_date_stat_compte = stat
    console.log("📅 Table sélectionnée via event:", dateString)
  }
}

onMounted(() => {
  const savedTable = localStorage.getItem("selectedTable")
  if (savedTable) {
    selectedTable.value = savedTable
    popupStore.selected_date = savedTable
  }
  window.addEventListener('export-dav-data', handleExportEvent)
  window.addEventListener('table-date-selected', handleDateSelection)
  fetchTables()
})

onUnmounted(() => {
  window.removeEventListener('export-dav-data', handleExportEvent)
  window.removeEventListener('table-date-selected', handleDateSelection)
})

const fetchTables = async () => {
  try {
    const res = await axios.get(`${api}/api/history_insert`)
        console.log("📊 dav.vue - Données history/liste:", res.data)

    history.value = res.data.history || []
  } catch (err) {
    console.error("Erreur lors du chargement de l'history:", err)
  }
}

watch(selectedTable, (newVal) => {
  if (newVal) {
    console.log("Table persistée :", localStorage.getItem("selectedTable"))
    localStorage.setItem("selectedTable", newVal)
    popupStore.selected_date = newVal
  }
})

watch(() => popupStore.selected_date, (newDate) => {
    console.log(" Store updated - selected_date:", newDate)

  if (newDate) {
    selectedTable.value = newDate
    localStorage.setItem("selectedTable", newDate)
    console.log("📅 Table sélectionnée via store:", selectedTable.value)
        console.log("Nom de la table utilisée :", selectedTable.value, typeof selectedTable.value)

  }
}, { immediate: true })

watch(() => popupStore.selected_date, (newDate) => {
  let dateValue = newDate
  if (newDate && typeof newDate === 'object' && newDate.label) {
    dateValue = newDate.label
  }
  
  if (dateValue) {
    selectedTable.value = dateValue
    localStorage.setItem("selectedTable", dateValue)
    console.log("📅 Table sélectionnée via store:", dateValue)
  }
}, { immediate: true })
</script>
<style scoped>
.unified-container {
  max-height: 90vh;
  overflow-y: auto;
  padding-bottom: 20px;
  padding: 0 10px; 
}

.global-graphe-section {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e0e0e0;
}

.resumer-section {
  margin-bottom: 20px;
}

.tab-resumer {
  margin-bottom: 16px;
}

.tabs-container {
  margin-top: 16px;
  margin-bottom: 20px;
}

.display-toggle-row {
  margin-bottom: 20px;
  margin-top: 8px;
}

.content-window {
  min-height: 400px;
}

.tab-content {
  margin-top: 8px;
}

.tab-component {
  margin-top: 16px;
}

.no-table-alert {
  margin-top: 20px;
}

@media (max-width: 960px) {
  .global-graphe-section {
    margin-bottom: 20px;
    padding-bottom: 12px;
  }
  
  .resumer-section {
    margin-bottom: 16px;
  }
  
  .tabs-container {
    margin-top: 12px;
    margin-bottom: 16px;
  }
  
  .display-toggle-row {
    margin-bottom: 16px;
  }
}

@media (max-width: 600px) {
  .global-graphe-section {
    margin-bottom: 16px;
    padding-bottom: 8px;
  }
  
  .resumer-section {
    margin-bottom: 12px;
  }
  
  .tab-resumer {
    margin-bottom: 12px;
  }
}
</style>