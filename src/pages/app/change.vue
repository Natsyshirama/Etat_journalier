<template>
  <v-container class="change-container" fluid>
    <v-row class="mb-4">
      <v-col cols="12" md="3">
        <v-date-input
          v-model="dateDebutModel"
          label="Date début"
          variant="outlined"
          density="compact"
          prepend-icon=""
          prepend-inner-icon="mdi-calendar"
          clearable
          :min="minDate"
          :max="maxDate"
          @update:model-value="onDateDebutChange"
        />
        <v-checkbox
          v-model="mode_unique"
          label="Date unique"
          class="mt-0"
          hide-details
        />
      </v-col>

      <v-col cols="12" md="3" v-if="!mode_unique">
        <v-date-input
          v-model="dateFinModel"
          label="Date fin"
          variant="outlined"
          density="compact"
          prepend-icon=""
          prepend-inner-icon="mdi-calendar"
          clearable
          :min="dateDebutModel || minDate"
          :max="maxDate"
          @update:model-value="onDateFinChange"
        />
      </v-col>

      <!-- Reste du template inchangé -->
      <v-col cols="12" md="auto" class="d-flex align-right">
        <v-btn
          color="primary"
          size="large"
          rounded="lg"
          @click="fetchChangeData"
          :loading="loading"
          class="px-6"
        >
          Charger
        </v-btn>
      </v-col>
    </v-row>


    <v-alert
      v-if="message"
      :type="status === 'error' ? 'error' : (status === 'warning' ? 'warning' : 'success')"
      border="left"
      dark
      class="mb-4"
    >
      {{ message }}
    </v-alert>
    <v-snackbar v-model="showSnackbar" :color="snackbarColor" timeout="3000">
        <div class="d-flex align-center">
          <v-icon class="mr-2">
            {{ snackbarIcon }}
          </v-icon>
          {{ snackbarMessage }}
        </div>
        
        <template #actions>
          <v-btn icon @click="showSnackbar = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </template>
      </v-snackbar>

    <v-tabs v-if="hasData" v-model="activeTab" class="mb-4">
      <v-tab>Synthèse</v-tab>
      <v-tab>État</v-tab>
      <v-tab>Allocation</v-tab>
    </v-tabs>

    <v-window v-if="hasData" v-model="activeTab">
      <v-window-item>
        <TableauChange
          :columns="syntheseColumns"
          :rows="syntheseRows"
          :money-columns-prop="['EUR_Montant', 'USD_Montant', 'Total_MGA', 'EUR_Montant_CV_MGA', 'USD_Montant_CV_MGA']"

          title="Tableau de Synthèse"
        />
      </v-window-item>

      <v-window-item>
        <TableauChange
          :columns="etatColumns"
          :rows="etatRows"
                  :money-columns-prop="['MONTANT_OPERATION_DEVISE', 'MONTANT_CV_MGA','COURS']"

          title="Tableau d'État"
        />
      </v-window-item>

      <v-window-item>
        <TableauChange
          :columns="allocationColumns"
          :rows="allocationRows"
                  :money-columns-prop="['MONTANT_OPERATION_DEVISE', 'MONTANT_CV_MGA','COURS']"

          title="Tableau d'Allocation"
        />
      </v-window-item>
    </v-window>
  </v-container>
</template>

<script setup>
import { ref, computed,onMounted, onUnmounted ,inject} from "vue"
import axios from "axios"
import * as XLSX from "xlsx"
import { watch } from "vue"
import TableauChange from "@/components/change/TableauChange.vue"
import { formatUSD } from "@/composables/format_money.js"
import { dateToYYYYMMDD, yyyymmddToDate } from "@/composables/format_date.js" 


const mode_unique = ref(false)
const dateDebut = ref("")
const dateFin = ref("")
const loading = ref(false)
const exporting = ref(false)
const status = ref(null)
const message = ref("")
const activeTab = ref(0)

const syntheseRows = ref([])
const syntheseColumns = ref([])
const etatRows = ref([])
const etatColumns = ref([])
const allocationRows = ref([])
const allocationColumns = ref([])

const showSnackbar = ref(false)
const snackbarMessage = ref('')
const snackbarColor = ref('success')
const snackbarIcon = ref('mdi-check-circle')

const dateDebutModel = ref(null)
const dateFinModel = ref(null)


// Dates min et max (optionnel)


const maxDate = computed(() => {
  return new Date() // Aujourd'hui
})


const onDateDebutChange = (newDate) => {
  dateDebut.value = dateToYYYYMMDD(newDate)
}

const onDateFinChange = (newDate) => {
  dateFin.value = dateToYYYYMMDD(newDate)
}

// Reset dateFin quand mode_unique change
watch(mode_unique, (newVal) => {
  if (newVal) {
    dateFinModel.value = null
    dateFin.value = ''
  }
})

const showNotification = (message, type = 'success') => {
  snackbarMessage.value = message
  snackbarColor.value = type
  
  // Définir l'icône selon le type
  switch(type) {
    case 'success':
      snackbarIcon.value = 'mdi-check-circle'
      break
    case 'error':
      snackbarIcon.value = 'mdi-alert-circle'
      break
    case 'info':
      snackbarIcon.value = 'mdi-information'
      break
    case 'warning':
      snackbarIcon.value = 'mdi-alert'
      break
    default:
      snackbarIcon.value = 'mdi-information'
  }
  
  showSnackbar.value = true
}
const api = inject('api') 

const hasData = computed(() =>
  syntheseRows.value.length > 0 ||
  etatRows.value.length > 0 ||
  allocationRows.value.length > 0
)

const saveToLocalStorage = () => {
  const dataToSave = {
    dateDebut: dateDebut.value,
    dateFin: dateFin.value,
    status: status.value,
    message: message.value,
    synthese: syntheseRows.value,
    etat: etatRows.value,
    allocation: allocationRows.value,
  }
  localStorage.setItem("changeData", JSON.stringify(dataToSave))
}

const fetchChangeData = async () => {
if (!dateDebut.value) {
    status.value = "error"
    message.value = "Veuillez remplir la date de début."
    showNotification('Veuillez remplir la date de début.', 'error')
    return
  }
  
  if (!mode_unique.value && !dateFin.value) {
    status.value = "error"
    message.value = "Veuillez remplir la date de fin."
    showNotification('Veuillez remplir la date de fin.', 'error')
    return
  }
  
  if (mode_unique.value) {
    dateFin.value = ''
  }

  loading.value = true
  status.value = null
  message.value = ""

  try {
    const res = await axios.post(
      `${api}/api/change/generate_report`,
      null,
      {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` },
        params: {
          date_debut: dateDebut.value,
          date_fin: dateFin.value,
          unique: mode_unique.value
        },
      }
    )

    const data = res.data
    status.value = data.status
    message.value = data.message || ""

    if (data.status === "success" ) {
      // Message personnalisé selon le mode
      let successMessage = `Rapport généré avec succès`
      if (mode_unique.value) {
        successMessage = `Rapport généré avec succès pour le ${dateDebut.value}`
      } else if (dateFin.value) {
        successMessage = `Rapport généré avec succès du ${dateDebut.value} au ${dateFin.value}`
      }
      
      message.value = successMessage
      showNotification(successMessage, 'success')
      
      // Mise à jour des données
      if (data.synthese?.length) {
        syntheseColumns.value = Object.keys(data.synthese[0])
        syntheseRows.value = data.synthese
      } else {
        syntheseColumns.value = []
        syntheseRows.value = []
      }

      if (data.etat?.length) {
        etatColumns.value = Object.keys(data.etat[0])
        etatRows.value = data.etat
      } else {
        etatColumns.value = []
        etatRows.value = []
      }

      if (data.allocation?.length) {
        allocationColumns.value = Object.keys(data.allocation[0])
        allocationRows.value = data.allocation
      } else {
        allocationColumns.value = []
        allocationRows.value = []
      }

      saveToLocalStorage()

     } else if (data.status === "warning") {
      // CAS WARNING : Aucune donnée trouvée
      const warningMsg = data.message || 
        (mode_unique.value 
          ? `Aucune donnée trouvée pour le ${dateDebut.value}`
          : `Aucune donnée trouvée du ${dateDebut.value} au ${dateFin.value}`)
      
      message.value = warningMsg
      showNotification(warningMsg, 'warning')
      
      // Réinitialiser les tableaux
      syntheseColumns.value = []
      syntheseRows.value = []
      etatColumns.value = []
      etatRows.value = []
      allocationColumns.value = []
      allocationRows.value = []

    } else if (data.status === "error") {
      // CAS ERROR : Erreur technique
      const errorMsg = data.message || "Erreur lors de la génération du rapport."
      message.value = errorMsg
      showNotification(`Erreur : ${errorMsg}`, 'error')
      
      // Réinitialiser les tableaux
      syntheseColumns.value = []
      syntheseRows.value = []
      etatColumns.value = []
      etatRows.value = []
      allocationColumns.value = []
      allocationRows.value = []
    }
  } catch (err) {
    console.error("Erreur lors du chargement des données Change:", err)
    status.value = "error"
    showNotification('Erreur serveur ou réseau lors du chargement des données Change.', 'error')
  if (err.response?.data?.message) {
    message.value = err.response.data.message
  } else {
    message.value = "Erreur serveur ou réseau."
    showNotification('Erreur serveur ou réseau lors du chargement des données Change.', 'error')
  }

}finally {
    loading.value = false
  }
}

const exportToExcel = () => {
  if (!hasData.value || !dateDebut.value || !dateFin.value) {
    message.value = "Aucune donnée à exporter ou dates manquantes."
    status.value = "error"
    return
  }

  exporting.value = true

  try {
    const wb = XLSX.utils.book_new()

    const addSheet = (rows, name) => {
      if (rows.length) {
        const ws = XLSX.utils.json_to_sheet(rows)
        XLSX.utils.book_append_sheet(wb, ws, name)
      }
    }

    addSheet(syntheseRows.value, "Synthèse")
    addSheet(etatRows.value, "État")
    addSheet(allocationRows.value, "Allocation")

    const fileName = `change_${dateDebut.value}_${dateFin.value}.xlsx`
    XLSX.writeFile(wb, fileName)

    message.value = "Export Excel réussi !"
    status.value = "success"
    showNotification('Export Excel réussi !', 'success')
  } catch (error) {
    console.error("Erreur lors de l'export Excel:", error)
    message.value = "Erreur lors de l'export Excel."
    status.value = "error"
    showNotification('Erreur lors de l\'export Excel.', 'error')
  } finally {
    exporting.value = false
  }
}
const handleExportEvent = () => {
  exportToExcel()
}

onMounted(() => {
    const saved = localStorage.getItem("changeData")
  if (saved) {
    const parsed = JSON.parse(saved)
    dateDebut.value = parsed.dateDebut || ""
    dateFin.value = parsed.dateFin || ""

     // Mettre à jour les modèles Date
    dateDebutModel.value = yyyymmddToDate(dateDebut.value)
    dateFinModel.value = yyyymmddToDate(dateFin.value)

    status.value = parsed.status || null
    message.value = parsed.message || ""
    syntheseRows.value = parsed.synthese || []
    etatRows.value = parsed.etat || []  
    allocationRows.value = parsed.allocation || []
    if (parsed.synthese?.length) {
      syntheseColumns.value = Object.keys(parsed.synthese[0])
    }
    if (parsed.etat?.length) {
      etatColumns.value = Object.keys(parsed.etat[0])
    }
    if (parsed.allocation?.length) {
      allocationColumns.value = Object.keys(parsed.allocation[0])
    }
    
  }
  window.addEventListener('export-change-data', handleExportEvent)
})

onUnmounted(() => {
  window.removeEventListener('export-change-data', handleExportEvent)
})

watch(
  [syntheseRows, etatRows, allocationRows, dateDebut, dateFin],
  saveToLocalStorage,
  { deep: true }
)
</script>

<style scoped>
.change-container {
  max-height: 90vh;
  overflow-y: auto;
  padding-bottom: 20px;
}
.change-container::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Edge (basé sur Chromium) */
}
</style>
