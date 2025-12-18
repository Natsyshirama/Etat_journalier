<template>
  <v-toolbar color=" " class="bg-transparent" :title="toolbarTitle">
    <!-- Badge date -->

      <div class="flex flex-row justify-end items-center space-x-4 mx-4" >
        <h3 class="mr-5 text-xl">Date d'arrêt</h3>
<v-menu
  v-if="isCompte || isEsriPage || isChangePage || isSession || isInitialise || isgenerale || isFilemanager || isDecaissementAnalyse || isDepotAnalyse || isDepotDetail || isDecDetal || isAgence"
  v-model="menu"
  close-on-content-click
  offset-y
  max-width="250"
  min-width="250"
>
  <template #activator="{ props }">
    <v-btn v-bind="props" prepend-icon="mdi-calendar-range" variant="outlined">
      <template #prepend>
        <v-icon color="success" />
      </template>
      <span class="text-2xl">{{ selectedDate }}</span>
    </v-btn>
  </template>
  
  <v-card @click.stop> 
    <!-- Filtres Année/Mois -->
    <div class="pa-3 bg-lighten-4">
      <div class="d-flex align-center gap-2 mb-2">
        <v-select
          v-model="selectedYear"
          :items="availableYears"
          label="Année"
          density="compact"
          variant="outlined"
          hide-details
          class="flex-grow-1"
          @update:model-value="filterDates"
          @click.stop 
        ></v-select>
        
        <v-select
          v-model="selectedMonth"
          :items="availableMonths"
          item-title="name"
          item-value="value"
          label="Mois"
          density="compact"
          variant="outlined"
          hide-details
          class="flex-grow-1"
          @update:model-value="filterDates"
          @click.stop 
        ></v-select>
      </div>
      
       <v-btn
        v-if="selectedYear !== 'all' || selectedMonth !== 'all'"
        @click="resetFilters"
        color="primary"
        variant="text"
        size="small"
        block
      >
        Réinitialiser les filtres
      </v-btn>
    </div>
    
    <!-- Liste des dates filtrées -->
    <v-list style="max-height: 300px; overflow-y: auto;">
      <v-list-subheader v-if="filteredHistoryDates.length === 0">
        Aucune date trouvée
      </v-list-subheader>
      
      <v-list-item
        v-for="date in filteredHistoryDates"
        :key="date.label"
        @click="() => selectDate(date.label, date.stat_compte)"
        role="button"
        :active="date.label === selectedDate"
      >
        <div class="flex align-center" :title="date.stat_compte !== 1 ? 'Base non initialisée' : ''">
          <v-icon 
            v-if="date.stat_compte !== 1" 
            class="mr-2 text-red-700"
            size="small"
          >
            mdi-database-alert
          </v-icon> 
          <v-icon 
            v-else 
            color="success" 
            class="mr-2"
            size="small"
          >
            mdi-database-check
          </v-icon> 
          <v-list-item-title>{{ formatDisplayDate(date.label) }}</v-list-item-title>
        </div>
      </v-list-item>
    </v-list>
  </v-card>
</v-menu>

        <v-menu
        v-else
        v-model="menu"
        close-on-content-click
        offset-y
        max-width="200"
        min-width="200"
      >
        <template #activator="{ props }">
          <v-btn v-bind="props" prepend-icon="mdi-calendar-range" variant="outlined">
            <template #prepend>
              <v-icon color="success" />
            </template>
            <span class="text-2xl">{{ selectedDate }}</span>
          </v-btn>
        </template>
        <v-list style="max-height: 200px; overflow-y: auto;">
          <v-list-item
            v-for="date in historyDates"
            :key="date.label"
  @click="() => selectDateStatOf(date.label, date.stat_of)"
            role="button"
          >
            <div class="flex" :title="date.stat_of!='init'? 'Base non initialisé':''">
              <v-icon v-if="date.stat_of !== 'init'" class=" mr-2 text-red-700">mdi-database-alert</v-icon> 
              <v-icon v-else color="success" class=" mr-2">mdi-database-check</v-icon> 
              <v-list-item-title>{{ date.label }}</v-list-item-title>
            </div>
          </v-list-item>
        </v-list>
      </v-menu>
      </div>
    <!-- <div class="flex items-center gap-1 green_transparent mr-2 px-5 rounded-md">
      <v-icon icon="mdi-database" />
      <span v-if="date_last_import_file !== ''" title="Dernière importation">
        {{ formatDateString(date_last_import_file) }}
      </span>
      <span v-else>Récupération ...</span>
    </div> -->


    <!-- Menu change et esri export -->
    <v-btn 
      v-if="isEsriPage || isChangePage" 
      @click="handleExport" 
      prepend-icon="mdi-share-variant"
      :loading="exporting"
    >
      <template #prepend><v-icon color="success"></v-icon></template>
      <span class="text-md">Exporter</span>
    </v-btn>

    <!-- Menu export dav, dat, epr -->

    <v-menu v-else-if="isCompte" offset-y>
          <template v-slot:activator="{ props }">
            <v-btn v-bind="props" prepend-icon="mdi-share-variant">
              <template #prepend><v-icon color="success"></v-icon></template>
              <span class="text-md">Exporter</span>
            </v-btn>
          </template>
          <v-list>
            <v-list-item @click="exportDAT">
              <template #prepend><v-icon color="success">mdi-table</v-icon></template>
              <v-list-item-title style="font-size: 15px;">DAT</v-list-item-title>
            </v-list-item>
            <v-list-item @click="exportDAV">
              <template #prepend><v-icon color="success">mdi-chart-bar</v-icon></template>
              <v-list-item-title style="font-size: 15px;">DAV</v-list-item-title>
            </v-list-item>
            <v-list-item @click="exportEPR">
              <template #prepend><v-icon color="success">mdi-chart-line</v-icon></template>
              <v-list-item-title style="font-size: 15px;">EPR</v-list-item-title>
            </v-list-item>
            <v-list-item @click="exportDECAISSEMENT">
              <template #prepend><v-icon color="success">mdi-chart-line</v-icon></template>
              <v-list-item-title style="font-size: 15px;">DECAISSEMENT</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>

    <!-- Menu menu d'exportation -->
    <v-menu v-else offset-y  >
      <template v-slot:activator="{ props }" style=" margin: 0px 15px;">
        <v-btn v-bind="props" prepend-icon="mdi-share-variant">
          <template #prepend><v-icon color="success"></v-icon></template>
          <span class="text-md">Exporter</span>
        </v-btn>
      </template>

      <v-list>
        <v-list-item @click="exportToExcel_encours" >
          <template #prepend><v-icon color="success">mdi-file-chart</v-icon></template>
          <v-list-item-title style="font-size: 15px;">Encours</v-list-item-title>
        </v-list-item>

        <v-list-item @click="exportToExcel_LIMIT_AVM">
          <template #prepend><v-icon color="success">mdi-chart-bubble</v-icon></template>
          <v-list-item-title style="font-size: 15px;">Limit AVM</v-list-item-title>
        </v-list-item>

        <v-list-item @click="exportToExcel_LIMIT_CAUTION">
          <template #prepend><v-icon color="success">mdi-shield-check</v-icon></template>
          <v-list-item-title style="font-size: 15px;">Limit Caution</v-list-item-title>
        </v-list-item>

        <v-list-item @click="exportToExcel_remboursement">
          <template #prepend><v-icon color="success">mdi-cash-refund</v-icon></template>
          <v-list-item-title style="font-size: 15px;">État Remboursement</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>

    <!-- Avatar à droite -->
     <user_btn_profil class=" mx-4"></user_btn_profil>
    <!-- <v-btn stacked>
      <v-icon icon="mdi mdi-account"></v-icon>
      <span class=" text-xs">daa</span>
    </v-btn> -->
  </v-toolbar>
</template>

<script setup>
import user_btn_profil from './user_btn_profil.vue'
import { ref, watch, onMounted,inject,computed } from 'vue'
import { useRoute } from 'vue-router'
import { usePopupStore } from '../stores'
import * as XLSX from 'xlsx'
import { useRouter } from 'vue-router'


const route = useRoute()
const api = inject('api') 
const selectedDate = ref('Chargement en cours...')
const menu = ref(false)
const popupStore = usePopupStore()
const exporting = ref(false)
const router = useRouter()

const historyDates  = ref([])


const isEsriPage = computed(() => route.path === '/app/esri')
const isChangePage = computed(() => route.path === '/app/change')
const isCompte = computed(() => route.path === '/app/dav')
const isSession = computed(() => route.path === '/app/session')
const isInitialise = computed(() => route.path === '/app/Initialise')
const isgenerale = computed(() => route.path === '/app/generale')
const isFilemanager = computed(() => route.path === '/app/file_manager')
const isDecaissementAnalyse = computed(() => route.path === '/app/decaisAnalyse')
const isDepotAnalyse = computed(() => route.path === '/app/depotAnalyse')
const isDepotDetail = computed(() => route.path === '/app/analyseDetails')
const isDecDetal = computed(() => route.path === '/app/detailDecais')
const isAgence =  computed(() => route.path === '/app/Agence')

const toolbarTitle = computed(() => {
  if (isEsriPage.value) return 'ESRI'
  if (isChangePage.value) return 'Change'
  if (isCompte.value) return 'Encours Compte'
  if (isSession.value) return 'Gestion des utilisateurs'
  if (isInitialise.value) return 'Initialisation Compte'
  if (isgenerale.value) return 'Compte Vue'
  if (isFilemanager.value) return 'Gestionnaire de fichiers'
  if (isDecaissementAnalyse.value) return ' Décaissement'
  if (isDepotAnalyse.value) return ' Dépôt'
  if (isDepotDetail.value) return 'Détail Dépôt'
  if (isDecDetal.value) return 'Détail Décaissement'
  if (isAgence.value) return 'Gestion des Agences'

 return 'Encours Credits'
})



const selectedYear = ref('all')
const selectedMonth = ref('all')
const availableYears = ref(['all'])
const availableMonths = ref([
  { name: 'Tous', value: 'all' },
  { name: 'Janvier', value: '01' },
  { name: 'Février', value: '02' },
  { name: 'Mars', value: '03' },
  { name: 'Avril', value: '04' },
  { name: 'Mai', value: '05' },
  { name: 'Juin', value: '06' },
  { name: 'Juillet', value: '07' },
  { name: 'Août', value: '08' },
  { name: 'Septembre', value: '09' },
  { name: 'Octobre', value: '10' },
  { name: 'Novembre', value: '11' },
  { name: 'Décembre', value: '12' }
])

const allHistoryDates = ref([])

const handleExport = () => {
  if (isEsriPage.value) {
    exportEsriData()
  } else if (isChangePage.value) {
    exportChangeData()
  }
}


const exportEsriData = async () => {
  exporting.value = true
  try {
    window.dispatchEvent(new CustomEvent('export-esri-data'))
  } catch (error) {
    console.error('Erreur export ESRI:', error)
  } finally {
    exporting.value = false
  }
}

const exportChangeData = async () => {
  exporting.value = true
  try {
    window.dispatchEvent(new CustomEvent('export-change-data'))
  } catch (error) {
    console.error('Erreur export change:', error)
  } finally {
    exporting.value = false
  }
}


const exportDAT = () => {
  exporting.value = true
  console.log('Export DAT déclenché')
  window.dispatchEvent(new CustomEvent('export-dav-data', { detail: { type: 'DAT' } }))
}

const exportDAV = () => {
  exporting.value = true
  console.log('Export DAV déclenché')
  window.dispatchEvent(new CustomEvent('export-dav-data', { detail: { type: 'DAV' } }))
}

const exportEPR = () => {
  exporting.value = true
  console.log('Export EPR déclenché')
  window.dispatchEvent(new CustomEvent('export-dav-data', { detail: { type: 'EPR' } }))
}
const exportDECAISSEMENT = () => {
  exporting.value = true
  console.log('Export decaissement déclenché')
  window.dispatchEvent(new CustomEvent('export-dav-data', { detail: { type: 'DECAISSEMENT' } }))
}

const date_last_import_file = ref('')

const get_last_import_file = async () => {
  try {
    const response = await fetch(`${api}/api/get_last_import_file`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    })

    const data = await response.json()
    if (data?.response) {
      date_last_import_file.value = data.response.label
      popupStore.selected_date = data.response
    }
  } catch (error) {
    console.error("❌ Erreur :", error)
  }
}



const filteredHistoryDates = computed(() => {
  if (!allHistoryDates.value.length) return []
  
  return allHistoryDates.value.filter(date => {
    const year = date.label.substring(0, 4)
    const month = date.label.substring(4, 6)
    
    // Filtre par annee
    if (selectedYear.value !== 'all' && year !== selectedYear.value) {
      return false
    }
    
    // Filtre par mois
    if (selectedMonth.value !== 'all' && month !== selectedMonth.value) {
      return false
    }
    
    return true
  })
})


// Fonction pour extraire les annees disponibles
function extractAvailableYears(dates) {
  const years = new Set()
  dates.forEach(date => {
    if (date.label && date.label.length >= 4) {
      years.add(date.label.substring(0, 4))
    }
  })
  return ['all', ...Array.from(years).sort((a, b) => b - a)] 
}

function formatDisplayDate(dateStr) {
  if (dateStr.length === 8) {
    return `${dateStr.substring(6, 8)}/${dateStr.substring(4, 6)}/${dateStr.substring(0, 4)}`
  }
  return dateStr
}

// Fonction de filtrage
function filterDates() {
  // Pas besoin de faire quoi que ce soit ici
  console.log('Filtrage appliqué:', {
    year: selectedYear.value,
    month: selectedMonth.value,
    count: filteredHistoryDates.value.length
  })
}

// Fonction de reinitialisation
function resetFilters() {
  selectedYear.value = 'all'
  selectedMonth.value = 'all'
}


const formatDateString = (rawDate) => {
  if (!/^\d{8}$/.test(rawDate)) return null
  return `${rawDate.slice(0, 4)}-${rawDate.slice(4, 6)}-${rawDate.slice(6, 8)}`
}

onMounted(() => {
  (async () => {
    const data = await fetchData(`${api}/api/history_insert`)
    allHistoryDates.value = data
    historyDates.value = data 
    availableYears.value = extractAvailableYears(data)
  })();
  get_last_import_file()
})

// 📦 Donnee a exporter
const listes_encours_credits = ref([])
const listes_remboursement_credits = ref([])
const listes_limit_avm = ref([])
const listes_limit_caution = ref([])

watch(() => popupStore.encours_actual_data, (val) => {
  listes_encours_credits.value = val
}, { immediate: true })

watch(() => popupStore.remboursement_actual_data, (val) => {
  listes_remboursement_credits.value = val
}, { immediate: true })

watch(() => popupStore.limit_avm_actual_data, (val) => {
  listes_limit_avm.value = val
}, { immediate: true })

watch(() => popupStore.limit_caution_actual_data, (val) => {
  listes_limit_caution.value = val
}, { immediate: true })


function exportToExcel(data, filenameBase, sheetName = 'Feuille1') {
  if (!data || data.length === 0) {
    alert('Aucune donnée à exporter')
    return
  }

  const date = new Date().toISOString().slice(0, 10)
  const filename = `${filenameBase}_${date}.xlsx`

  const worksheet = XLSX.utils.json_to_sheet(data)
  const workbook = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(workbook, worksheet, sheetName)
  XLSX.writeFile(workbook, filename)
}

const exportToExcel_encours = () => exportToExcel(listes_encours_credits.value, 'Encours', 'Encours')
const exportToExcel_remboursement = () => exportToExcel(listes_remboursement_credits.value, 'Etat_de_remboursement', 'Remboursement')
const exportToExcel_LIMIT_AVM = () => exportToExcel(listes_limit_avm.value, 'Limit_AVM', 'LIMIT_AVM')
const exportToExcel_LIMIT_CAUTION = () => exportToExcel(listes_limit_caution.value, 'Limit_Caution', 'LIMIT_CAUTION')

async function fetchData(baseUrl, date = null) {
  try {
    // Si une date est fournie, on l’ajoute à l’URL
    const url = date ? `${baseUrl}?date=${date}` : baseUrl

    const response = await fetch(url)
    if (!response.ok) throw new Error(`Erreur HTTP : ${response.status}`)

    const data = await response.json()
        console.log("📊 menu_bar - Données reçues:", data)

    return data.response.data
  } catch (error) {
    console.error('❌ Erreur de chargement :', error)
    return []
  }
}

async function selectDate(date,stat_compte) {
  try {
    //update mise a jour
    const response = await fetch(`${api}/api/update_used_status?selected_date=${date}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    
    if (!response.ok) {
      console.warn("⚠️ Échec de la mise à jour du statut 'used'");
    }
    
    const result = await response.json();
    console.log("✅ Statut 'used' mis à jour:", result);
    
  } catch (error) {
    console.error("❌ Erreur lors de la mise à jour du statut 'used':", error);
  }
  
  selectedDate.value = date
  popupStore.selected_date = date
  popupStore.selected_date_stat_compte = stat_compte
  localStorage.setItem("selectedTable", date) 

  menu.value = false
   
 if (isCompte.value) {
    if (stat_compte === 0) {
      router.push({ name: 'Initialise', query: { label: date } })
    } else {
      window.dispatchEvent(new CustomEvent('table-date-selected', { detail: { date : date, stat_compte: stat_compte } }))
    }
  }
}  

async function selectDateStatOf(date, stat_of) {
  selectedDate.value = date

  popupStore.selected_date = date
  popupStore.selected_date_stat_of = stat_of

  menu.value = false

  window.dispatchEvent(new CustomEvent('table-date-stat-of-selected', {
    detail: { date, stat_of }
  }))
}



watch(historyDates, (val) => {
  if (Array.isArray(val) && val.length > 0) {
    const sorted = [...val].sort((a, b) => b.label.localeCompare(a.label))
    const lastDate = sorted[0].label
    const lastStatCompte = sorted[0].stat_compte

    selectedDate.value = lastDate
    popupStore.selected_date = lastDate
    popupStore.selected_date_stat_compte = lastStatCompte
    localStorage.setItem("selectedTable", lastDate)

    if (isCompte.value) {
      window.dispatchEvent(new CustomEvent('table-date-selected', { detail: { date: lastDate, stat_compte: lastStatCompte } }))
    }
    console.log("📅 Dernière date sélectionnée automatiquement :", lastDate)
  }
}, { immediate: true })
</script>

<style>
.green_transparent {
  background-color: #00dc54a4;
}
</style>
