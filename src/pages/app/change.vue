<template>
  <v-container class="change-container" fluid>
    <!-- 🔹 En-tête : Sélection période -->
    <v-row class="mb-4">
      <v-col cols="12" md="3">
        <v-text-field
          v-model="dateDebut"
          label="Date début (YYYYMMDD)"
          outlined
          dense
        />
      </v-col>

      <v-col cols="12" md="3">
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

    <!-- 🔹 Message d'état -->
    <v-alert
      v-if="message"
      :type="status === 'error' ? 'error' : (status === 'warning' ? 'warning' : 'success')"
      border="left"
      dark
      class="mb-4"
    >
      {{ message }}
    </v-alert>

    <!-- 🔹 Onglets pour les différentes tables -->
    <v-tabs v-if="hasData" v-model="activeTab" class="mb-4">
      <v-tab>Synthèse</v-tab>
      <v-tab>État</v-tab>
      <v-tab>Allocation</v-tab>
    </v-tabs>

    <!-- 🔹 Contenu des onglets -->
    <v-window v-if="hasData" v-model="activeTab">
      <!-- Synthèse -->
      <v-window-item>
        <TableauChange
          :columns="syntheseColumns"
          :rows="syntheseRows"
          title="Tableau de Synthèse"
        />
      </v-window-item>

      <!-- État -->
      <v-window-item>
        <TableauChange
          :columns="etatColumns"
          :rows="etatRows"
          title="Tableau d'État"
        />
      </v-window-item>

      <!-- Allocation -->
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
import { ref, computed,onMounted, onUnmounted } from "vue"
import axios from "axios"
import * as XLSX from "xlsx"
import TableauChange from "@/components/change/TableauChange.vue"

const dateDebut = ref("")
const dateFin = ref("")
const loading = ref(false)
const exporting = ref(false)
const status = ref(null)
const message = ref("")
const activeTab = ref(0)

// 🔹 Données pour chaque tableau
const syntheseRows = ref([])
const syntheseColumns = ref([])
const etatRows = ref([])
const etatColumns = ref([])
const allocationRows = ref([])
const allocationColumns = ref([])

const hasData = computed(() =>
  syntheseRows.value.length > 0 ||
  etatRows.value.length > 0 ||
  allocationRows.value.length > 0
)

// 🔹 Récupération des données depuis l'API
const fetchChangeData = async () => {
  if (!dateDebut.value || !dateFin.value) {
    status.value = "error"
    message.value = "Veuillez remplir les dates de début et de fin."
    return
  }

  loading.value = true
  status.value = null
  message.value = ""

  try {
    const res = await axios.post(
      `http://127.0.0.1:8000/api/change/generate_report_optimized`,
      null,
      {
        params: {
          date_debut: dateDebut.value,
          date_fin: dateFin.value,
        },
      }
    )

    const data = res.data
    status.value = data.status

    if (data.status === "success") {
      message.value = `Rapport généré avec succès pour la période ${dateDebut.value} - ${dateFin.value}`

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
 localStorage.setItem(
  "esriData",
  JSON.stringify({
    dateDebut: dateDebut.value,
    dateFin: dateFin.value,
    status: status.value,
    message: message.value,
  })
)

    } else {
      message.value = data.message || "Erreur lors de la génération du rapport."
    }
  } catch (err) {
    console.error("Erreur lors du chargement des données Change:", err)
    status.value = "error"
    message.value = err.response?.data?.message || "Erreur serveur ou réseau."
  } finally {
    loading.value = false
  }
}

// 🔹 Export Excel
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
  } catch (error) {
    console.error("Erreur lors de l'export Excel:", error)
    message.value = "Erreur lors de l'export Excel."
    status.value = "error"
  } finally {
    exporting.value = false
  }
}
const handleExportEvent = () => {
  exportToExcel()
}

onMounted(() => {
  window.addEventListener('export-change-data', handleExportEvent)
})

onUnmounted(() => {
  window.removeEventListener('export-change-data', handleExportEvent)
})
</script>

<style scoped>
.change-container {
  max-height: 90vh;
  overflow-y: auto;
  padding-bottom: 20px;
}
</style>
