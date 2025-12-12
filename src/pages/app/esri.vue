<template>
  <v-container class="esri-container"  fluid>
    
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
          hide-details

        />
        <v-checkbox
          v-model="compareMode"
          label="Mode comparer"
          hide-details
          class="mt-0"
        />
      </v-col>

       
 
      <v-col cols="12" sm="auto" class="d-flex align-rignt">
        <v-btn
          color="primary"
          size="large"
          rounded="lg"
          @click="fetchEsriData"
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
      border="right"
      class="mb-4"
    >
      {{ message }}
    </v-alert>
    <v-card   v-if="status === 'success' && bilan.length" class="mt-4 mb-6 pa-6 bilan-card"
  outlined>
      <v-list>
        <v-list-item
          v-for="(item, index) in bilan"
          :key="index"
        >
          <v-list-item-content>
            <v-list-item-title>
              {{ item.Type }} : {{ item['Total Montant'].toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-card>

    <div class="table-filtre-bar" v-if="status === 'success' && rows.length">

      <v-row class="align-center mb-4 px-2" fluid>

      <v-select
        v-model="selectedMonth"
        :items="monthsAvailable"
        label="Filtrer par mois"
        clearable
        dense
        hide-details
        style="max-width: 200px; margin-left: 16px;"
      />
      <v-col cols="12" md="3">
        <v-select
          v-model="selectedAgences"
          :items="agencesList"
          item-title="nom"
          item-value="code"
          label="Filtrer par agence"
          multiple
          chips
          clearable
          dense
          hide-details
        />
      </v-col>

      <v-col cols="12" md="3">
      <v-select
        v-model="selectedType"
        :items="typesList"
        item-title="nom"
        item-value="code"
        label="Filtrer par type"
        clearable
        dense
        hide-details
        style="max-width: 180px; margin-left: 12px;"
      />
      </v-col>

      <v-col cols="12" md="4" class="text-md-right text-center">
        <v-btn
          :color="showTotal ? 'blue' : 'grey'"
          variant="outlined"
          size="large"
          rounded="xl"
          prepend-icon="mdi-chart-line"
          class="mt-2 px-6"
          @click="showTotal = !showTotal"
        >
          Voir le total
        </v-btn>
      </v-col>
      </v-row>
    </div>

    <!-- TABLEAU NORMAL -->
<TablesEsri
  v-if="status === 'success' && rows.length && !showTotal"
  :columns="columns"
  :rows="rows"
  :selected-month="selectedMonth"
  :months="monthsAvailable"
  :selected-agences="selectedAgences"
  :selected-type="selectedType"
  :show-total="false"
  ref="tableEsriRef"
/>

<!-- TABLEAU TOTAL UNIQUEMENT -->
<TablesEsri
  v-if="status === 'success' && rows.length && showTotal"
  :columns="columns"
  :rows="rows"
  :selected-month="selectedMonth"
  :months="monthsAvailable"
  :selected-agences="selectedAgences"
  :selected-type="selectedType"
  :show-total="true"
  ref="tableEsriRef"
/>

  </v-container>
</template>


<script setup>
import { ref, onMounted, onUnmounted, inject, computed } from "vue"
import axios from "axios"
import * as XLSX from "xlsx"
import TablesEsri from "@/components/esri/TableauEsri.vue"
import { usePopupStore } from '@/stores'

const dateDebut = ref("")
const dateFin = ref("")
const loading = ref(false)
const exporting = ref(false)
const status = ref(null)
const message = ref("")
const columns = ref([])
const rows = ref([])
const tableEsriRef = ref(null)
const api = inject('api') 
const bilan = ref([])

const showTotal = ref(false)

const compareMode = ref(false) 
import { useAgences } from '@/composables/useAgences'

const { 
  agencesList, 
  loading: agencesLoading, 
  error: agencesError,
  getAgenceByCode 
} = useAgences(api)


const selectedAgences = ref([]) 

const selectedMonth = ref("")
const monthsAvailable = computed(() => {
  const dates = rows.value.map(r => r.Date)
  const months = dates
    .filter(Boolean)
    .map(date => {
      const parts = date.split("/")
      if (parts.length < 2) return null
      const [year, month] = parts
      return `${year}-${month.padStart(2, "0")}`
    })
    .filter(Boolean)
  return [...new Set(months)].sort()
})

const selectedType = ref("")         
const typesList = ref([{code:"RIA.PAYMENT", nom:"RIA"},
                       {code:"GLOBAL.TRANSFER.PAYMENT", nom:"GLOBAL TRANSFER"},
]) 


const fetchEsriData = async () => {
  if (!dateDebut.value || !dateFin.value) {
    status.value = "error"
    message.value = "Veuillez remplir toutes les informations."
    return
  }
  
  loading.value = true
  status.value = null
  message.value = ""

  try {
    const res = await axios.post(
      `${api}/api/esri/create_esri_precompute`,
      null,
      { 
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
        params: {
          date_debut: dateDebut.value,
          date_fin: dateFin.value,
          compare: compareMode.value,

        },
      }
    )


    if (res.status === "error") {
      
      status.value = "error"
      message.value = data.message || "Erreur lors du chargement des données."
      return
    }

    const data = res.data
    status.value = data.status
    message.value = data.message
    columns.value = data.columns || []
    rows.value = data.rows || []
    bilan.value = data.bilan || []

   localStorage.setItem(
  "esriData",
  JSON.stringify({
    dateDebut: dateDebut.value,
    dateFin: dateFin.value,
    status: status.value,
    message: message.value,
  })
)

  } catch (err) {
    console.error("Erreur lors du chargement des données ESRI:", err)
    if (err.response && err.response.data && err.response.data.message) {
      message.value = err.response.data.message
    } else {
      message.value = "Erreur serveur ou réseau."
    }

    status.value = "error"
  } 
  finally {
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
    const dataToExport = rows.value.map(row => {
      const exportedRow = {}
      columns.value.forEach(col => {
        exportedRow[col] = row[col] || ""
      })
      return exportedRow
    })

    const wb = XLSX.utils.book_new()
    
    const ws = XLSX.utils.json_to_sheet(dataToExport)
    
    XLSX.utils.book_append_sheet(wb, ws, "Données ESRI")
    
    const fileName = `esri_${dateDebut.value}_${dateFin.value}.xlsx`
    
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
  const saved = localStorage.getItem("esriData")
  if (saved) {
    const parsed = JSON.parse(saved)
    dateDebut.value = parsed.dateDebut || ""
    dateFin.value = parsed.dateFin || ""
    
  }

  window.addEventListener('export-esri-data', handleExportEvent)
})

onUnmounted(() => {
  window.removeEventListener('export-esri-data', handleExportEvent)
})
</script>

<style scoped>
.esri-container {
  max-height: 90vh;
  overflow-y: auto;
  padding-bottom: 20px;
}
.esri-container::-webkit-scrollbar {
  display: none; 
}
</style>