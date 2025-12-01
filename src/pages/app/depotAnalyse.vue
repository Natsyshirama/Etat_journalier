<template>
  <v-container  class="pa-0 full-container"fluid>
    <v-card class="pa-8 rounded-0 elevation-2 fade-in full-card" flat>
      
      <!-- TITRE -->
      <v-card-title class="text-h4 font-weight-bold text-left mb-6">
         Analyse des Encours de Dépôts 
      </v-card-title>

      <!-- FORMULAIRE -->
      <v-row dense class="px-4 justify-left">
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

        <!-- FILTRE PAR MOIS -->
        <v-col cols="12" sm="2">
          <v-select
            v-model="selectedMonths"
            :items="availableMonths"
            item-title="label"
            item-value="value"
            label="Filtrer par mois"
            variant="outlined"
            rounded="lg"
            multiple
            chips
            clearable
            density="comfortable"
            :hint="monthFilterHint"
            persistent-hint
          >
            <template v-slot:prepend-item>
              <v-list-item title="Tous les mois" @click="toggleAllMonths">
                <template v-slot:prepend>
                  <v-checkbox
                    :model-value="allMonthsSelected"
                    :indeterminate="someMonthsSelected"
                    color="primary"
                  ></v-checkbox>
                </template>
              </v-list-item>
              <v-divider class="mt-2"></v-divider>
            </template>
          </v-select>
        </v-col>

        <v-col cols="12" sm="auto" class="d-flex align-right ">
          <v-btn
            color="pink"
            size="large"
            rounded="lg"
            :loading="loading"
            @click="analyserEncours"
            class="px-8"
          >
            
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
                  v-for="column in tableColumns" 
                  :key="column.key"
                  class="header-date"
                >
                  {{ column.label }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="agence in agencesData" :key="agence.code">
                <td class="cell-agence">{{ agence.code }}</td>
                <td class="cell-nom">{{ agence.nom }}</td>
                <td 
                  v-for="column in tableColumns" 
                  :key="column.key"
                  class="cell-montant"
                >
                  <div class="montant-container">
                    <div class="montant-value">
                      {{ formatNumber(getCellValue(agence, column)) }}
                    </div>
                    <div 
                      v-if="getCellEcart(agence, column) !== 0" 
                      class="ecart-indicator"
                      :class="getEcartClass(getCellEcart(agence, column))"
                    >
                      {{ formatEcart(getCellEcart(agence, column)) }}
                    </div>
                  </div>
                </td>
              </tr>
              
              <!-- LIGNE DE TOTAL -->
              <tr v-if="hasResults" class="total-row">
                <td class="cell-agence total-cell">
                  <strong>TOTAL</strong>
                </td>
                <td class="cell-nom total-cell">
                  <strong>{{ agencesData.length }} agences</strong>
                </td>
                <td 
                  v-for="column in tableColumns" 
                  :key="column.key"
                  class="cell-montant total-cell"
                >
                  <div class="montant-container">
                    <div class="montant-value total-montant">
                      {{ formatNumber(getTotalValue(column)) }}
                    </div>
                    <div 
                      v-if="getTotalEcart(column) !== 0" 
                      class="ecart-indicator total-ecart"
                      :class="getEcartClass(getTotalEcart(column))"
                    >
                      {{ formatEcart(getTotalEcart(column)) }}
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
const selectedMonths = ref([])
const loading = ref(false)
const message = ref("")
const messageType = ref("info")

// Résultats
const datesList = ref([])
const agencesData = ref([])
const availableMonths = ref([])
const allData = ref({}) // Stocker toutes les données brutes

// Computed
const allAgencesSelected = computed(() => 
  selectedAgences.value.length === agencesList.value.length
)

const someAgencesSelected = computed(() => 
  selectedAgences.value.length > 0 && !allAgencesSelected.value
)

const allMonthsSelected = computed(() => 
  selectedMonths.value.length === availableMonths.value.length
)

const someMonthsSelected = computed(() => 
  selectedMonths.value.length > 0 && !allMonthsSelected.value
)

const hasResults = computed(() => agencesData.value.length > 0 && datesList.value.length > 0)

const monthFilterHint = computed(() => {
  if (selectedMonths.value.length === 0) return 'Affichage quotidien'
  return `${selectedMonths.value.length} mois sélectionné(s) - Affichage mensuel`
})

// Colonnes du tableau (dates ou mois selon la sélection)
const tableColumns = computed(() => {
  if (selectedMonths.value.length === 0) {
    // Mode quotidien : afficher toutes les dates
    return datesList.value.map(date => ({
      key: date,
      label: formatDateDisplay(date),
      type: 'daily'
    }))
  } else {
    // Mode mensuel : afficher les mois sélectionnés
    return availableMonths.value
      .filter(month => selectedMonths.value.includes(month.value))
      .map(month => ({
        key: month.value,
        label: month.label,
        type: 'monthly'
      }))
  }
})

// Méthodes
const toggleAllAgences = () => {
  if (allAgencesSelected.value) {
    selectedAgences.value = []
  } else {
    selectedAgences.value = agencesList.value.map(ag => ag.code)
  }
}

const toggleAllMonths = () => {
  if (allMonthsSelected.value) {
    selectedMonths.value = []
  } else {
    selectedMonths.value = availableMonths.value.map(month => month.value)
  }
}

// Obtenir la valeur d'une cellule
const getCellValue = (agence, column) => {
  if (column.type === 'daily') {
    // Mode quotidien : valeur quotidienne
    return agence.encours[column.key]?.montant || 0
  } else {
    // Mode mensuel : total du mois
    return agence.monthlyEncours[column.key]?.montant || 0
  }
}

// Obtenir l'écart d'une cellule
const getCellEcart = (agence, column) => {
  if (column.type === 'daily') {
    // Mode quotidien : écart quotidien
    return agence.encours[column.key]?.ecart || 0
  } else {
    // Mode mensuel : écart mensuel
    return agence.monthlyEncours[column.key]?.ecart || 0
  }
}

// Extraire les mois disponibles des dates
const extractAvailableMonths = (dates) => {
  const monthSet = new Set()
  const monthLabels = []
  
  dates.forEach(date => {
    const year = date.substring(0, 4)
    const month = date.substring(4, 6)
    const monthKey = `${year}${month}`
    
    if (!monthSet.has(monthKey)) {
      monthSet.add(monthKey)
      
      // Formater le label (ex: "Septembre 2025")
      const monthNames = [
        'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
        'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
      ]
      const monthName = monthNames[parseInt(month) - 1]
      monthLabels.push({
        value: monthKey,
        label: `${monthName} ${year}`
      })
    }
  })
  
  // Trier par date (du plus récent au plus ancien)
  return monthLabels.sort((a, b) => a.value.localeCompare(b.value))
}

// Calculer les totaux mensuels pour chaque agence
const calculateMonthlyEncours = (agences) => {
  const monthlyData = []

  agences.forEach(agenceCode => {
    const agenceInfo = agencesList.value.find(ag => ag.code === agenceCode)
    const monthlyEncours = {}

    // Pour chaque mois disponible
    availableMonths.value.forEach((month, index) => {
      // Récupérer toutes les dates de ce mois
      const monthDates = datesList.value.filter(date => 
        date.startsWith(month.value)
      )

      // Calculer le total mensuel
      let totalMontant = 0

      monthDates.forEach(date => {
        const davData = allData.value.dav[agenceCode]?.[date] || {}
        const datData = allData.value.dat[agenceCode]?.[date] || {}
        const eprData = allData.value.epr[agenceCode]?.[date] || {}

        const davDebit = davData.total_debit || 0
        const datMontant = datData.total_montant || 0
        const eprDebit = eprData.total_debit || 0

        totalMontant += (davDebit + datMontant + eprDebit)
      })

      // Calculer l'écart par rapport au mois précédent
      let ecart = 0
      if (index > 0) {
        const previousMonth = availableMonths.value[index - 1]
        const previousEncours = monthlyEncours[previousMonth.value]?.montant || 0
        ecart = totalMontant - previousEncours
      }

      monthlyEncours[month.value] = {
        montant: totalMontant,
        ecart: ecart
      }
    })

    monthlyData.push({
      code: agenceInfo.code,
      nom: agenceInfo.nom,
      encours: {}, // Données quotidiennes
      monthlyEncours: monthlyEncours // Données mensuelles
    })
  })

  return monthlyData
}

// Organiser les données quotidiennes
const organizeDailyData = (agences) => {
  const dailyData = []

  agences.forEach(agenceCode => {
    const agenceInfo = agencesList.value.find(ag => ag.code === agenceCode)
    const encours = {}

    // Pour chaque date, calculer l'encours
    datesList.value.forEach((date, index) => {
      const davData = allData.value.dav[agenceCode]?.[date] || {}
      const datData = allData.value.dat[agenceCode]?.[date] || {}
      const eprData = allData.value.epr[agenceCode]?.[date] || {}

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

    dailyData.push({
      code: agenceInfo.code,
      nom: agenceInfo.nom,
      encours: encours,
      monthlyEncours: {} // Sera calculé plus tard si besoin
    })
  })

  return dailyData
}

const analyserEncours = async () => {
  loading.value = true
  message.value = ""
  datesList.value = []
  agencesData.value = []
  availableMonths.value = []
  selectedMonths.value = [] // Réinitialiser la sélection mois

  try {
    // Déterminer les agences à analyser
    const agencesToAnalyze = selectedAgences.value.length > 0 
      ? selectedAgences.value 
      : agencesList.value.map(ag => ag.code)

    // Récupérer les données pour toutes les agences
    allData.value = await fetchAllAgencesData(agencesToAnalyze)
    
    // Organiser les données quotidiennes
    organizeBaseData(allData.value, agencesToAnalyze)

    // Extraire les mois disponibles
    availableMonths.value = extractAvailableMonths(datesList.value)
    
    // Calculer les données quotidiennes
    const dailyData = organizeDailyData(agencesToAnalyze)
    
    // Calculer les données mensuelles
    const monthlyData = calculateMonthlyEncours(agencesToAnalyze)
    
    // Fusionner les données quotidiennes et mensuelles
    agencesData.value = dailyData.map((dailyAgence, index) => ({
      ...dailyAgence,
      monthlyEncours: monthlyData[index].monthlyEncours
    }))

    messageType.value = "success"
    message.value = `Analyse terminée : ${agencesData.value.length} agences, ${datesList.value.length} dates disponibles`

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
        agence: agenceCode,
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

const organizeBaseData = (allData, agences) => {
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


// Calculer le total pour une colonne (date ou mois)
const getTotalValue = (column) => {
  let total = 0
  agencesData.value.forEach(agence => {
    total += getCellValue(agence, column)
  })
  return total
}

// Calculer l'écart total pour une colonne
const getTotalEcart = (column) => {
  let totalEcart = 0
  agencesData.value.forEach(agence => {
    totalEcart += getCellEcart(agence, column)
  })
  return totalEcart
}
// Sélectionner toutes les agences par défaut au chargement
onMounted(() => {
  selectedAgences.value = agencesList.value.map(ag => ag.code)
})
</script>

<style scoped>
/* Modern Professional Style */
.full-container {
  width: 100%;
  height: 100vh;
  overflow-y: auto;
  max-height: 90vh;
  overflow-y: auto;
  padding-bottom: 20px;
  padding: 0 10px; 
}

.full-card {
  border-radius: 18px !important;
  
  box-shadow: 0 4px 24px rgba(44, 62, 80, 0.08);
}

.v-card-title {
  letter-spacing: 1px;
  text-align: left;
  font-family: 'Montserrat', 'Segoe UI', Arial, sans-serif;
}

.table-container {
  overflow-x: auto;
  max-width: 100%;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(44, 62, 80, 0.07);
  
}
/* Styles pour la ligne de total */
.total-row {
  border-top: 2px solid #dee2e6;
}

.total-cell {
  font-weight: bold !important;
}

.total-montant {
  font-size: 1rem !important;
  color: #698bab !important;
      vertical-align: top; /* montant en haut */

}

.total-ecart {
  font-size: 0.9rem !important;
  background-color: rgba(164, 174, 185, 0.1) !important;
}

/* Amélioration du style des cellules de total */
.total-row td {
  border-top: 2px solid #b4afaf !important;
  border-bottom: 2px solid #b4afaf !important;
}

.total-row .cell-agence,
.total-row .cell-nom {
  background: linear-gradient(135deg, #4b4c4e, #1565c0) !important;
  color: white !important;
  text-align: center !important;
}

/* Effet de survol pour la ligne de total */
.total-row:hover {
  background-color: #e3f2fd !important;
}

.encours-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 1rem;
 border-radius: 12px;
  overflow: hidden;
}

.encours-table th,
.encours-table td {
  padding: 14px 10px;
  border-bottom: 1px solid #e0e0e0;
  text-align: left;
  font-family: 'Segoe UI', Arial, sans-serif;
}

.encours-table th {
  font-weight: 700;
  position: sticky;
  top: 0;
  z-index: 10;
  font-size: 1.05rem;
  letter-spacing: 0.5px;
}

.header-agence {
  width: 120px;
  background-color: #cdd2d6 !important;
  color: #fff !important;
  text-align: center !important;
  border-top-left-radius: 12px;
}

.header-nom {
  width: 200px;
  background-color: #97a2ae !important;
  color: #fff !important;
}

.header-date {
  width: 140px;
    background-color: #324559 !important;

  text-align: center !important;
}

.encours-table tbody tr {
  transition: background 0.2s;
}
.encours-table tbody tr:hover {
}

.cell-agence {
  font-weight: bold;
  text-align: center;
  color: #067eef;
}

.cell-nom {
  font-weight: 500;
}

.cell-montant {
  text-align: right;
  font-family: 'Roboto Mono', 'Courier New', monospace;
  font-weight: 500;
    vertical-align: top; /* montant en haut */

}

.montant-container {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: space-between; /* espace entre montant et écart */
  height: 32px; /* fixe la hauteur pour séparer montant et écart */
}

.montant-value {
  font-size: 0.9rem;
    text-align: right;

}

.ecart-indicator {
  font-size: 0.85rem;
  font-weight: bold;
  padding: 2px 8px;
  border-radius: 6px;
  margin-top: 2px;
  box-shadow: 0 1px 4px rgba(44,62,80,0.07);
}

.ecart-positive {
  color: #388e3c;
}

.ecart-negative {
  color: #c62828;
}

.v-select,
.v-text-field,
.v-btn {
  border-radius: 12px !important;
  font-family: 'Montserrat', 'Segoe UI', Arial, sans-serif;
  font-size: 1rem !important;
  box-shadow: 0 1px 6px rgba(44,62,80,0.05);
}

.v-btn {
  font-weight: 600 !important;
  letter-spacing: 0.5px;
  box-shadow: 0 2px 8px rgba(44,62,80,0.08);
}

.v-alert {
  border-radius: 10px !important;
  font-size: 1rem !important;
  font-family: 'Segoe UI', Arial, sans-serif;
  box-shadow: 0 1px 8px rgba(44,62,80,0.07);
}

.fade-in {
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Responsive */
@media (max-width: 900px) {
  .encours-table {
    font-size: 0.85rem;
  }
  .encours-table th,
  .encours-table td {
    padding: 8px 4px;
  }
  .header-agence,
  .header-nom {
    width: 90px;
  }
  .header-date {
    width: 100px;
  }
  .v-card-title {
    font-size: 1.3rem !important;
  }
}
.encours-table th,
.encours-table td {
  padding: 14px 10px;
  border-bottom: 1px solid #b4afaf;
  text-align: left;
  font-family: 'Segoe UI', Arial, sans-serif;
  border-right: 1px solid #ada9a9; /* Ajoute la bordure verticale */
}

.encours-table th:last-child,
.encours-table td:last-child {
  border-right: none; /* Pas de bordure sur la dernière colonne */
}
</style>