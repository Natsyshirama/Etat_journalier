<template>
  <v-container  class="pa-0 full-container"fluid>
    <v-card class="pa-8 rounded-0 elevation-2 fade-in full-card" flat>
      <v-row class="justify-space-between align-center mb-6 px-4">
        <div>
<h1 class="text-h5 font-weight-bold text-blue">
          </h1>   <v-btn
            color="flat"
            size="large"
            rounded="lg"
            @click="goToAnalyseDecaissement"
            class="px-4"
          >
            <v-icon left>mdi-chart-bar</v-icon>
            Analyser Décaissement
          </v-btn>      </div>
        <div class="d-flex gap-3">
          
         
          
        </div>
      </v-row>
      <!-- TITRE -->
      <v-row align="center">
        <v-col cols="12" md="8">
          
          <p class="mt-2 text-white text-body-1 opacity-80">
          </p>
        </v-col>

        <v-col cols="12" md="4" class="text-md-right text-center">
          <v-btn
            :color="showGraphe ? 'blue' : 'grey'"
            variant="outlined"
            size="large"
            rounded="xl"
            prepend-icon="mdi-chart-line"
            class="mt-2 px-6"
            @click="showGraphe = !showGraphe"
          >
            Voir le graphe
          </v-btn>
        </v-col>
      </v-row>

      <v-row dense class="px-4 justify-left">
        <!-- Select agence -->
        <v-col cols="12" sm="4">
          <v-select
            v-model="selectedAgences"
            :items="agencesList"
            item-title="nom"
            item-value="code"
            label="Sélectionner les agences"
            class="label-visible"
            variant="outlined"
            rounded="lg"
            multiple
            chips
            clearable
            density="comfortable"
            :hint="selectedAgences.length > 0 ? `${selectedAgences.length} agence(s) sélectionnée(s)` : 'Sélectionnez une ou plusieurs agences'"
            persistent-hint
    style="max-height: 95px; overflow-y: auto;"

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
            hide-details
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
              hide-details
            />
            <v-checkbox
              v-model="compare"
              density="compact"

              label="comparer"
              color="primary"
              class="mt-2"
              :style="{ marginTop: '-8px', color: '#888' }"
    hide-details

              
            />
          </v-col>

        <!-- FILTRE PAR MOIS -->
        <v-col cols="12" sm="2" v-if="!compare">
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
                    <!-- Dans le tableau principal, par exemple dans depotAnalyse.vue -->
                      <div 
                        class="montant-value"
                        @click="goToDetail(column.key, agence.code )"
                        style="cursor:pointer;"
                      >
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

<div v-if="showGraphe && hasResults" class="mt-8">
  <v-card class="elevation-3 pa-4">
    <Line
  :data="{
    labels: graphLabels,
    datasets: [
      {
        label: 'Montant total',
        data: graphValues,
        borderColor: '#1976d2',
        tension: 0.4,
        pointRadius: 4,
        borderWidth: 3
      }
    ]
  }"
  :options="{
    responsive: true,
    plugins: {
      legend: { display: true, position: 'top' },
      title: { 
        display: true, 
        text: 'Évolution des encours de dépôts', 
        font: { size: 18 } 
      },
      tooltip: {
        useHTML: true,
        mode: 'index',
        intersect: false,
        callbacks: {
          label: (context) => {
            const montant = context.parsed.y
            const idx = context.dataIndex
            const ecart = graphEcarts[idx] || 0
              let sign = '⚫'
                if (ecart > 0) sign = '🟢'
                else if (ecart < 0) sign = '🔴​'
            return [
              `Montant total: ${formatNumber(montant)}`,
              `Écart:${sign} ${formatEcart(ecart)} `
            ]
          }
        }
      }
    },
    scales: {
      x: { title: { display: true, text: 'Date ou Mois', font: { size: 15 } } },
      y: { 
        title: { display: true, text: 'Montant total', font: { size: 15 } }, 
        beginAtZero: true,
        ticks: {
          callback: function(value) {
            return formatNumber(value)
          }
        }
      }
    }
  }"
  style="height:800px;"
/>
  </v-card>
</div>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted,inject } from "vue"
import axios from "axios"
import { Line } from "vue-chartjs"
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale
} from "chart.js"
import { useRouter } from 'vue-router'
ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale)


const router = useRouter()
const goToDetail = (columnKey, agenceCode) => {
  
  router.push({
    path: "/app/analyseDetails",
    query: { tableName: columnKey, agence: agenceCode }
  })
}

const goToAnalyseDecaissement = () => {
  router.push('/app/decaisAnalyse')
}


const api = inject("api")

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
const compare = ref(false)

const selectedMonths = ref([])
const loading = ref(false)
const message = ref("")
const messageType = ref("info")

// Résultats
const datesList = ref([])
const agencesData = ref([])
const availableMonths = ref([])
const allData = ref({})

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
  if (selectedMonths.value.length === 0) return 'Affichage journalier'
  return `${selectedMonths.value.length} mois sélectionné(s) - Affichage mensuel`
})

//colonnes du tableau
const tableColumns = computed(() => {
  if (selectedMonths.value.length === 0) {
//daily
    return datesList.value.map(date => ({
      key: date,
      label: formatDateDisplay(date),
      type: 'daily'
    }))
  } else {
    //monthly
    return availableMonths.value
      .filter(month => selectedMonths.value.includes(month.value))
      .map(month => ({
        key: month.value,
        label: month.label,
        type: 'monthly'
      }))
  }
})

// methodes
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
// valeur par cellule
const getCellValue = (agence, column) => {
  if (column.type === 'daily') {
    return agence.encours[column.key]?.montant || 0
  } else {
    return agence.monthlyEncours[column.key]?.montant || 0
  }
}

// ecart par cellule
const getCellEcart = (agence, column) => {
  if (column.type === 'daily') {
    return agence.encours[column.key]?.ecart || 0
  } else {
    
    return agence.monthlyEncours[column.key]?.ecart || 0
  }
}

// getmois dispo
const getMoisDispo = (dates) => {
  const monthSet = new Set()
  const monthLabels = []
  
  dates.forEach(date => {
    const year = date.substring(0, 4)
    const month = date.substring(4, 6)
    const monthKey = `${year}${month}`
    
    if (!monthSet.has(monthKey)) {
      monthSet.add(monthKey)
      
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
  
  return monthLabels.sort((a, b) => a.value.localeCompare(b.value))
}

//total par mois /agence
const calculateMonthlyEncours = (agences) => {
  const monthlyData = []

  agences.forEach(agenceCode => {
    const agenceInfo = agencesList.value.find(ag => ag.code === agenceCode)
    const monthlyEncours = {}

    // les mois dispo
    availableMonths.value.forEach((month, index) => {
      // date dispo sur cette mois
      const monthDates = datesList.value.filter(date => 
        date.startsWith(month.value)
      )

      // calc total mois
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

      // calc ecart du mois prev
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
      encours: {}, 
      monthlyEncours: monthlyEncours 
    })
  })

  return monthlyData
}

// organsation des data journaliers
const organizeDailyData = (agences) => {
  const dailyData = []

  agences.forEach(agenceCode => {
    const agenceInfo = agencesList.value.find(ag => ag.code === agenceCode)
    const encours = {}

// calcule encours depots
    datesList.value.forEach((date, index) => {
      const davData = allData.value.dav[agenceCode]?.[date] || {}
      const datData = allData.value.dat[agenceCode]?.[date] || {}
      const eprData = allData.value.epr[agenceCode]?.[date] || {}

      const davDebit = davData.total_debit || 0
      const datMontant = datData.total_montant || 0
      const eprDebit = eprData.total_debit || 0

      const encoursDepot = davDebit + datMontant + eprDebit

//ecart
      let ecart = 0
      if (index > 0) {
        const previousDate = datesList.value[index - 1]
        const previousEncours = encours[previousDate]?.montant || 0
        ecart = encoursDepot - previousEncours
      }
console.log('Ecart pour', date, ':', ecart)
      encours[date] = {
        montant: encoursDepot,
        ecart: ecart
      }
    })

    dailyData.push({
      code: agenceInfo.code,
      nom: agenceInfo.nom,
      encours: encours,
      monthlyEncours: {} //por total par mois
    })
  })

  return dailyData
}




const saveToLocalStorage = () => {
  try {
    const snapshot = {
      timestamp: new Date().toISOString(),
      selectedAgences: selectedAgences.value,
      dateDebut: dateDebut.value,
      dateFin: dateFin.value,
      selectedMonths: selectedMonths.value,
      datesList: datesList.value,
      availableMonths: availableMonths.value,
      agencesData: agencesData.value,
      message: message.value,
      messageType: messageType.value
    }
    localStorage.setItem("depotAnalyse_snapshot", JSON.stringify(snapshot))
    console.log('Snapshot saved to localStorage: depotAnalyse_snapshot')
  } catch (err) {
    console.error('Failed to save snapshot to localStorage', err)
  }
}



const analyserEncours = async () => {
  loading.value = true
  message.value = ""
  datesList.value = []
  agencesData.value = []
  availableMonths.value = []
  selectedMonths.value = [] 

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
    availableMonths.value = getMoisDispo(datesList.value)
    
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
     
    try {
            saveToLocalStorage()
            console.log('Snapshot auto-sauvegardé après analyse')
          } catch (err) {
            console.warn('Erreur lors de la sauvegarde automatique:', err)
          }
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

  for (const product of ['dav', 'dat', 'epr']) {
    console.log(`Récupération des données ${product} pour agences:`, agences)

    for (const agenceCode of agences) {
      const params = {
        agence: agenceCode,
        date_debut: dateDebut.value || undefined,
        date_fin: dateFin.value || undefined,
        compare: compare.value || undefined

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
  const allDates = new Set()
  
  //convertir sous forme tableau
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


// total pour une colonne
const getTotalValue = (column) => {
  let total = 0
  agencesData.value.forEach(agence => {
    total += getCellValue(agence, column)
  })
  return total
}

// ecart total pour une column
const getTotalEcart = (column) => {
  let totalEcart = 0
  agencesData.value.forEach(agence => {
    totalEcart += getCellEcart(agence, column)
  })
  return totalEcart
}
const showGraphe = ref(false)


const restaurerDataCacher = () => {
  const raw = localStorage.getItem("depotAnalyse_snapshot")
  if (!raw) return false
  try {
    const parsed = JSON.parse(raw)

    selectedAgences.value = (parsed.selectedAgences && parsed.selectedAgences.length)
      ? parsed.selectedAgences
      : agencesList.value.map(ag => ag.code)

    dateDebut.value = parsed.dateDebut || ""
    dateFin.value = parsed.dateFin || ""
    selectedMonths.value = parsed.selectedMonths || []
    datesList.value = parsed.datesList || []
    availableMonths.value = parsed.availableMonths || (datesList.value.length ? getMoisDispo(datesList.value) : [])
    agencesData.value = parsed.agencesData || []
    message.value = parsed.message || ""
    messageType.value = parsed.messageType || "info"

    console.log("Snapshot restored from localStorage: depotAnalyse_snapshot")
    return true
  } catch (err) {
    console.warn("Failed to parse depotAnalyse_snapshot:", err)
    return false
  }
}

onMounted(() => {
  const restored = restaurerDataCacher()
  if (!restored) {
    selectedAgences.value = agencesList.value.map(ag => ag.code)
  }
})
// ...existing code...
onMounted(() => {
  selectedAgences.value = agencesList.value.map(ag => ag.code)
})
const graphLabels = computed(() => tableColumns.value.map(col => col.label))

const graphValues = computed(() =>
  tableColumns.value.map(col => getTotalValue(col))
)

const graphEcarts = computed(() =>
  tableColumns.value.map(col => getTotalEcart(col))
)

</script>

<style scoped>
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
/* Ajoute ceci dans le <style scoped> */
.chips-scroll {
  max-height: 60px;
  overflow-y: auto;
  display: flex;
  flex-wrap: wrap;
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