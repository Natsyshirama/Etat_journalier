<template>
  <v-container class="esri-container">
    <!-- En-tête : Sélection période -->
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

      <v-col cols="12" md="3">
        <v-text-field
          v-model="label"
          label="Label (ex: 202505)"
          outlined
          dense
        />
      </v-col>

      <v-col cols="12" md="3" class="d-flex align-center">
        <v-btn
          color="primary"
          @click="fetchEsriData"
          :loading="loading"
          class="mr-2"
        >
          Charger les données
        </v-btn>
        
        <v-btn
          color="success"
          @click="exportToExcel"
          :disabled="!rows.length"
          :loading="exporting"
        >
          Exporter Excel
        </v-btn>
      </v-col>
    </v-row>

    <!-- Message d'état -->
    <v-alert
      v-if="message"
      :type="status === 'error' ? 'error' : (status === 'warning' ? 'warning' : 'success')"
      border="left"
      dark
      class="mb-4"
    >
      {{ message }}
    </v-alert>

    <!-- Tableau des données -->
    <TablesEsri
      v-if="status === 'success' && rows.length"
      :columns="columns"
      :rows="rows"
      ref="tableEsriRef"
    />
  </v-container>
</template>
<script setup>
import { ref } from "vue"
import axios from "axios"
import * as XLSX from "xlsx" // Installation requise: npm install xlsx
import TablesEsri from "@/components/esri/TableauEsri.vue"

const dateDebut = ref("")
const dateFin = ref("")
const label = ref("")
const loading = ref(false)
const exporting = ref(false)
const status = ref(null)
const message = ref("")
const columns = ref([])
const rows = ref([])
const tableEsriRef = ref(null)

const fetchEsriData = async () => {
  if (!dateDebut.value || !dateFin.value || !label.value) {
    status.value = "error"
    message.value = "Veuillez remplir toutes les informations."
    return
  }

  loading.value = true
  status.value = null
  message.value = ""

  try {
    const res = await axios.post(
      `http://127.0.0.1:8000/api/esri/create_esri_precompute`,
      null,
      {
        params: {
          label: label.value,
          date_debut: dateDebut.value,
          date_fin: dateFin.value,
        },
      }
    )

    const data = res.data
    status.value = data.status
    message.value = data.message
    columns.value = data.columns || []
    rows.value = data.rows || []

  } catch (err) {
    console.error("Erreur lors du chargement des données ESRI:", err)
    status.value = "error"
    message.value = "Erreur serveur ou réseau."
  } finally {
    loading.value = false
  }
}

const exportToExcel = () => {
  if (!rows.value.length || !dateDebut.value || !dateFin.value) {
    message.value = "Aucune donnée à exporter ou dates manquantes."
    status.value = "error"
    return
  }

  exporting.value = true

  try {
    // Préparer les données pour l'export
    const dataToExport = rows.value.map(row => {
      const exportedRow = {}
      columns.value.forEach(col => {
        exportedRow[col] = row[col] || ""
      })
      return exportedRow
    })

    // Créer un workbook
    const wb = XLSX.utils.book_new()
    
    // Créer une worksheet à partir des données
    const ws = XLSX.utils.json_to_sheet(dataToExport)
    
    // Ajouter la worksheet au workbook
    XLSX.utils.book_append_sheet(wb, ws, "Données ESRI")
    
    // Générer le nom du fichier
    const fileName = `esri_${dateDebut.value}_${dateFin.value}.xlsx`
    
    // Télécharger le fichier
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
</script>

<style scoped>
.esri-container {
  max-height: 90vh;
  overflow-y: auto;
  padding-bottom: 20px;
}
</style>
