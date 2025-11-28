<template>
  <v-container fluid class="pa-0 full-container">
    <v-card class="pa-8 rounded-0 elevation-2 fade-in full-card" flat>
      
      <!-- TITRE -->
      <v-card-title class="text-h4 font-weight-bold text-center mb-6">
        📊 Analyse des Encours de Dépôts par Agence
      </v-card-title>

      <!-- FORMULAIRE -->
      <v-row dense class="px-4 justify-center">
        <!-- SELECTION MULTIPLE DES AGENCES -->
        <v-col cols="12" sm="4">
          <v-select
            v-model="selectedAgences"
            :items="agencesList"
            item-title="nom"
            item-value="code"
            label="Sélectionner les agences"
            variant="outlined"
            rounded="lg"
            multiple
            chips
            clearable
            density="comfortable"
            :hint="selectedAgences.length > 0 ? `${selectedAgences.length} agence(s) sélectionnée(s)` : 'Sélectionnez une ou plusieurs agences'"
            persistent-hint
          >
            <template v-slot:prepend-item>
              <v-list-item title="Toutes les agences" @click="toggleAllAgences">
                <template v-slot:prepend>
                  <v-checkbox
                    :model-value="allAgencesSelected"
                    :indeterminate="someAgencesSelected"
                    color="primary"
                  ></v-checkbox>
                </template>
              </v-list-item>
              <v-divider class="mt-2"></v-divider>
            </template>
          </v-select>
        </v-col>

        <v-col cols="12" sm="2">
          <v-text-field
            v-model="dateDebut"
            label="Date début"
            placeholder="YYYYMMDD"
            variant="outlined"
            rounded="lg"
            clearable
            density="comfortable"
          />
        </v-col>

        <v-col cols="12" sm="2">
          <v-text-field
            v-model="dateFin"
            label="Date fin"
            placeholder="YYYYMMDD"
            variant="outlined"
            rounded="lg"
            clearable
            density="comfortable"
          />
        </v-col>

        <v-col cols="12" sm="auto" class="d-flex align-center">
          <v-btn
            color="primary"
            size="large"
            rounded="lg"
            :loading="loading"
            @click="analyserEncours"
            class="px-8"
          >
            <v-icon left>mdi-chart-line</v-icon>
            Analyser
          </v-btn>
        </v-col>
      </v-row>

      <!-- MESSAGE -->
      <v-alert
        v-if="message"
        :type="messageType"
        class="mt-4 mx-2"
        rounded="lg"
        border="start"
        elevation="1"
      >
        {{ message }}
      </v-alert>

      <!-- TABLEAU HORIZONTAL -->
      <v-row v-if="hasResults" class="mt-8">
        <v-col cols="12">
          <v-card class="elevation-3">
            <v-card-text class="pa-0">
              <div class="table-container">
                <table class="encours-table">
                  <thead>
                    <tr>
                      <th class="header-agence">AGENCE</th>
                      <th class="header-nom">NOM AGENCE</th>
                      <th 
                        v-for="date in datesList" 
                        :key="date"
                        class="header-date"
                      >
                        {{ formatDateDisplay(date) }}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="agence in agencesData" :key="agence.code">
                      <td class="cell-agence">{{ agence.code }}</td>
                      <td class="cell-nom">{{ agence.nom }}</td>
                      <td 
                        v-for="date in datesList" 
                        :key="date"
                        class="cell-montant"
                      >
                        <div class="montant-container">
                          <div class="montant-value">
                            {{ formatNumber(agence.encours[date]?.montant) }}
                          </div>
                          <div 
                            v-if="agence.encours[date]?.ecart !== 0" 
                            class="ecart-indicator"
                            :class="getEcartClass(agence.encours[date]?.ecart)"
                          >
                            {{ formatEcart(agence.encours[date]?.ecart) }}
                          </div>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

    </v-card>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from "vue"
import axios from "axios"

const api = "http://localhost:8000"

// Liste des agences avec leurs noms
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

// Résultats
const datesList = ref([])
const agencesData = ref([])

// Computed
const allAgencesSelected = computed(() => 
  selectedAgences.value.length === agencesList.value.length
)

const someAgencesSelected = computed(() => 
  selectedAgences.value.length > 0 && !allAgencesSelected.value
)

const hasResults = computed(() => agencesData.value.length > 0 && datesList.value.length > 0)

// Méthodes
const toggleAllAgences = () => {
  if (allAgencesSelected.value) {
    selectedAgences.value = []
  } else {
    selectedAgences.value = agencesList.value.map(ag => ag.code)
  }
}

const analyserEncours = async () => {
  loading.value = true
  message.value = ""
  datesList.value = []
  agencesData.value = []

  try {
    // Déterminer les agences à analyser
    const agencesToAnalyze = selectedAgences.value.length > 0 
      ? selectedAgences.value 
      : agencesList.value.map(ag => ag.code)

    // Récupérer les données pour toutes les agences
    const allData = await fetchAllAgencesData(agencesToAnalyze)
    
    // Organiser les données
    organizeData(allData, agencesToAnalyze)

    messageType.value = "success"
    message.value = `Analyse terminée : ${agencesData.value.length} agences, ${datesList.value.length} dates`

  } catch (error) {
    console.error("Erreur analyse:", error)
    messageType.value = "error"
    message.value = "❌ Erreur lors de l'analyse des encours"
  } finally {
    loading.value = false
  }
}

const fetchAllAgencesData = async (agences) => {
  const allData = {
    dav: {},
    dat: {},
    epr: {}
  }

  // Récupérer les données pour les 3 produits
  for (const product of ['dav', 'dat', 'epr']) {
    console.log(`Récupération des données ${product} pour agences:`, agences)

    // Pour chaque agence, faire un appel API
    for (const agenceCode of agences) {
      const params = {
        agence: agenceCode, // ← IMPORTANT: Spécifier l'agence
        date_debut: dateDebut.value || undefined,
        date_fin: dateFin.value || undefined
      }

      // Nettoyer les params undefined
      Object.keys(params).forEach(key => params[key] === undefined && delete params[key])

      try {
        console.log(`Appel API pour ${product} - ${agenceCode}`, params)
        
        const response = await axios.get(`${api}/api/resume/total-produit/${product}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
          params
        })

        console.log(`Réponse ${product} - ${agenceCode}:`, response.data)

        if (Array.isArray(response.data) && response.data.length > 0) {
          if (!allData[product][agenceCode]) {
            allData[product][agenceCode] = {}
          }
          
          // Organiser les données par date
          response.data.forEach(item => {
            const date = item.date_agence.date
            allData[product][agenceCode][date] = item.data
          })
        } else {
          console.log(`Aucune donnée pour ${product} - ${agenceCode}`)
        }
      } catch (error) {
        console.error(`Erreur récupération ${product} - ${agenceCode}:`, error)
      }
    }
  }

  console.log('Données récupérées:', allData)
  return allData
}

const organizeData = (allData, agences) => {
  // Collecter toutes les dates uniques
  const allDates = new Set()
  
  Object.values(allData.dav).forEach(agenceData => {
    Object.keys(agenceData).forEach(date => allDates.add(date))
  })
  Object.values(allData.dat).forEach(agenceData => {
    Object.keys(agenceData).forEach(date => allDates.add(date))
  })
  Object.values(allData.epr).forEach(agenceData => {
    Object.keys(agenceData).forEach(date => allDates.add(date))
  })

  // Trier les dates
  datesList.value = Array.from(allDates).sort()

  // Organiser les données par agence
  agencesData.value = agences.map(agenceCode => {
    const agenceInfo = agencesList.value.find(ag => ag.code === agenceCode)
    const encours = {}

    // Pour chaque date, calculer l'encours
    datesList.value.forEach((date, index) => {
      const davData = allData.dav[agenceCode]?.[date] || {}
      const datData = allData.dat[agenceCode]?.[date] || {}
      const eprData = allData.epr[agenceCode]?.[date] || {}

      const davDebit = davData.total_debit || 0
      const datMontant = datData.total_montant || 0
      const eprDebit = eprData.total_debit || 0

      const encoursDepot = davDebit + datMontant + eprDebit

      // Calculer l'écart par rapport à la date précédente
      let ecart = 0
      if (index > 0) {
        const previousDate = datesList.value[index - 1]
        const previousEncours = encours[previousDate]?.montant || 0
        ecart = encoursDepot - previousEncours
      }

      encours[date] = {
        montant: encoursDepot,
        ecart: ecart
      }
    })

    return {
      code: agenceInfo.code,
      nom: agenceInfo.nom,
      encours: encours
    }
  })
}

const formatDateDisplay = (dateStr) => {
  if (!dateStr) return ''
  const year = dateStr.substring(0, 4)
  const month = dateStr.substring(4, 6)
  const day = dateStr.substring(6, 8)
  return `${day}/${month}/${year}`
}

const formatNumber = (num) => {
  if (num === undefined || num === null || num === 0) return '0'
  return new Intl.NumberFormat('fr-FR').format(Math.round(num))
}

const formatEcart = (ecart) => {
  if (ecart === undefined || ecart === null || ecart === 0) return ''
  return ecart > 0 ? `+${formatNumber(ecart)}` : formatNumber(ecart)
}

const getEcartClass = (ecart) => {
  if (ecart > 0) return 'ecart-positive'
  if (ecart < 0) return 'ecart-negative'
  return ''
}



// Sélectionner toutes les agences par défaut au chargement
onMounted(() => {
  selectedAgences.value = agencesList.value.map(ag => ag.code)
})
</script>

<style scoped>
.full-container {
  width: 100%;
  min-height: 100vh;
  overflow-x: auto;
}

.full-card {
  border-radius: 0 !important;
}

.table-container {
  overflow-x: auto;
  max-width: 100%;
}

.encours-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.encours-table th,
.encours-table td {
  padding: 12px 8px;
  border: 1px solid #e0e0e0;
  text-align: left;
}

.encours-table th {
  font-weight: bold;
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-agence {
  width: 120px;
  background-color: #1976d2 !important;
  text-align: center !important;
}

.header-nom {
  width: 200px;
  background-color: #1976d2 !important;
}

.header-date {
  width: 140px;
  background-color: #424242 !important;
  color: white;
  text-align: center !important;
}

.cell-agence {
  font-weight: bold;
  text-align: center;
}

.cell-nom {
  font-weight: 500;
}

.cell-montant {
  text-align: right;
  font-family: 'Courier New', monospace;
  font-weight: 500;
}

.montant-container {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.montant-value {
  font-size: 0.9rem;
  font-weight: bold;
}

.ecart-indicator {
  font-size: 0.75rem;
  font-weight: bold;
  padding: 2px 6px;
  border-radius: 4px;
}

.ecart-positive {
  color: #2e7d32;
  background-color: rgba(76, 175, 80, 0.1);
}

.ecart-negative {
  color: #c62828;
  background-color: rgba(244, 67, 54, 0.1);
}

.fade-in {
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Responsive */
@media (max-width: 768px) {
  .encours-table {
    font-size: 0.75rem;
  }
  
  .encours-table th,
  .encours-table td {
    padding: 8px 4px;
  }
  
  .header-agence,
  .header-nom {
    width: 100px;
  }
  
  .header-date {
    width: 120px;
  }
}
</style>