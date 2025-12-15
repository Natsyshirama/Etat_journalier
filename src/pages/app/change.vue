<template>
  <v-container class="change-container" fluid>
    <v-row class="mb-4">
      <v-col cols="12" md="3">
        <v-text-field
          v-model="dateDebut"
          label="Date début (YYYYMMDD)"
          outlined
          dense
           hide-details
        />
        <v-checkbox
            v-model="mode_unique"
            label="date unique"
            class="mt-0"
            hide-details
          />
      </v-col>

      <v-col cols="12" md="3" v-if= !mode_unique>
        <v-text-field
          v-model="dateFin"
          label="Date fin (YYYYMMDD)"
          outlined
          dense
        />
      </v-col>

      <v-col cols="12" md="3" class="d-flex align-center">
        <v-btn
          color="primary"
          @click="fetchChangeData"
          :loading="loading"
          class="mr-2"
        >
          Charger les données
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
          title="Tableau de Synthèse"
        />
      </v-window-item>

      <v-window-item>
        <TableauChange
          :columns="etatColumns"
          :rows="etatRows"
          title="Tableau d'État"
        />
      </v-window-item>

      <v-window-item>
        <TableauChange
          :columns="allocationColumns"
          :rows="allocationRows"
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
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
        params: {
          date_debut: dateDebut.value,
          date_fin: dateFin.value,
          unique: mode_unique.value
        },
      }
    )

    const data = res.data
    status.value = data.status

    if (data.status === "success") {
      message.value = `Rapport généré avec succès pour la période ${dateDebut.value} - ${dateFin.value}`
      showNotification(`Rapport Change généré avec succès pour la période ${dateDebut.value} - ${dateFin.value}`, 'success')
      if (data.synthese?.length) {
        syntheseColumns.value = Object.keys(data.synthese[0])
        syntheseRows.value = data.synthese
      }

      if (data.etat?.length) {
        etatColumns.value = Object.keys(data.etat[0])
        etatRows.value = data.etat
      }

      if (data.allocation?.length) {
        allocationColumns.value = Object.keys(data.allocation[0])
        allocationRows.value = data.allocation
      }

      saveToLocalStorage()

    } else {
      message.value = data.message || "Erreur lors de la génération du rapport."
      showNotification(`Erreur lors de la génération du rapport Change: ${message.value}`, 'error')
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
