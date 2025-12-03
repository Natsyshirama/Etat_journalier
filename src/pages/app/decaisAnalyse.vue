<template>
  <v-container fluid class="pa-0 full-container">
    <v-card class="pa-8 rounded-0 elevation-2 full-card" flat>
      <v-card-title class="text-h4 font-weight-bold mb-6">Analyse des Décaissements</v-card-title>

      <v-row dense class="px-4">
        <v-col cols="12" sm="4">
          <v-select v-model="selectedAgences" :items="agencesList" item-title="nom" item-value="code"
                    label="Sélectionner agences" multiple chips clearable></v-select>
        </v-col>
        <v-col cols="12" sm="2">
          <v-text-field v-model="dateDebut" label="Date début (YYYYMMDD)" clearable></v-text-field>
        </v-col>
        <v-col cols="12" sm="2">
          <v-text-field v-model="dateFin" label="Date fin (YYYYMMDD)" clearable></v-text-field>
        </v-col>
        <v-col cols="12" sm="auto">
          <v-btn color="primary" @click="analyserDecaissement" :loading="loading">Analyser</v-btn>
        </v-col>
      </v-row>

      <v-alert v-if="message" :type="messageType" class="mt-4">{{ message }}</v-alert>

      <v-row v-if="hasResults" class="mt-6">
        <v-col cols="12">
          <!-- tableau simplifié: lignes = agences, colonnes = dates -->
          <div class="table-container">
            <table class="encours-table">
              <thead>
                <tr>
                  <th>AGENCE</th><th>NOM</th>
                  <th v-for="d in datesList" :key="d">{{ formatDateDisplay(d) }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="ag in agencesData" :key="ag.code">
                  <td>{{ ag.code }}</td><td>{{ ag.nom }}</td>
                  <td v-for="d in datesList" :key="d">{{ formatNumber( getCellValue(ag, d) ) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </v-col>
      </v-row>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, computed } from "vue"
import axios from "axios"
import { useRouter } from "vue-router"
const api = import.meta.env.VITE_API_BASE || "http://localhost:8000"

const agencesList = ref([
  { code: "MG0010009", nom: "Andavamamba" },
  { code: "MG0010004", nom: "Analamahitsy" },
  { code: "MG0010024", nom: "Andravoahangy" },
  { code: "MG0010052", nom: "Imerinafovoany" },
  { code: "MG0010011", nom: "Andoharanofotsy" },
  { code: "MG0010012", nom: "Anosizato" },
  { code: "MG0010010", nom: "67 Hectares" },
  { code: "MG0011001", nom: "Antanimena" },
  { code: "MG0010003", nom: "Antsahabe" },
  { code: "MG0010022", nom: "Behoririka" },
  { code: "MG0010053", nom: "Ivandry" },
  { code: "MG0010013", nom: "Mahamasina" },
  { code: "MG0010041", nom: "Soixante Sept Hectares" },
  { code: "MG0010023", nom: "Tanjombato" }
])
const selectedAgences = ref([])
const dateDebut = ref("")
const dateFin = ref("")
const loading = ref(false)
const message = ref("")
const messageType = ref("info")

const datesList = ref([])
const agencesData = ref([]) // [{ code, nom, decaissements: {date: { total_montant_capital, ecart } } }]

const hasResults = computed(() => agencesData.value.length && datesList.value.length)

const formatDateDisplay = (d) => `${d.substring(6,8)}/${d.substring(4,6)}/${d.substring(0,4)}`
const formatNumber = (n) => n == null ? "0" : new Intl.NumberFormat('fr-FR',{minimumFractionDigits:2,maximumFractionDigits:2}).format(n)

const getCellValue = (agence, date) => agence.decaissements[date]?.total_montant_capital || 0

const analyserDecaissement = async () => {
  loading.value = true
  message.value = ""
  datesList.value = []
  agencesData.value = []
  try {
    const agencesToAnalyze = selectedAgences.value.length ? selectedAgences.value : agencesList.value.map(a => a.code)
    // fetch per agence
    const allData = { decaissement: {} }
    for (const ag of agencesToAnalyze) {
      const params = { agence: ag, date_debut: dateDebut.value || undefined, date_fin: dateFin.value || undefined }
      Object.keys(params).forEach(k => params[k] === undefined && delete params[k])
      const res = await axios.get(`${api}/api/resume/total-produit/decaissement`, { params })
      if (Array.isArray(res.data)) {
        allData.decaissement[ag] = {}
        res.data.forEach(item => {
          allData.decaissement[ag][item.date_agence.date] = item.data
        })
      }
    }
    // construire datesList (union)
    const dateSet = new Set()
    Object.values(allData.decaissement).forEach(m => Object.keys(m).forEach(d => dateSet.add(d)))
    datesList.value = Array.from(dateSet).sort()
    // construire agencesData
    agencesData.value = agencesToAnalyze.map(code => {
      const info = agencesList.value.find(x => x.code === code) || { code, nom: code }
      return { code: info.code, nom: info.nom, decaissements: allData.decaissement[code] || {} }
    })
    messageType.value = "success"
    message.value = "Analyse terminée"
  } catch (e) {
    console.error(e)
    messageType.value = "error"
    message.value = "Erreur récupération décaissement"
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* reprendre styles de depotAnalyse ou adapter */
.table-container { overflow-x: auto; }
.encours-table { width:100%; border-collapse: collapse; }
</style>