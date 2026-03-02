<template>
  <v-container class="pa-0 full-container" fluid>
    <v-card class="pa-8 rounded-0 elevation-2 fade-in full-card" flat>
     <div class="navigation-container mb-6">
        <div class="navigation-header">
          <div class="header-title">
            <h1 class="text-h6 font-weight-bold mb-0">Decaissement Analyse</h1>
          </div>
          <div class="navigation-buttons">
            <v-btn
              color="primary"
              size="large"
              rounded="lg"
              @click="goToAnalyseEncours"
              class="navigation-btn"
              variant="outlined"
            >
              <v-icon left>mdi-chart-box</v-icon>
              Analyse Dépôts
              <v-icon right size="small">mdi-arrow-right</v-icon>
            </v-btn>
          </div>
        </div>
      </div>

      <v-row dense class="px-4 justify-left">
        <!-- Select agence -->
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
        </v-col>

        <v-col cols="12" sm="2">
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
      
      <v-row v-if="hasResults" class="mt-8">
        <v-col cols="12" md="4" class="text-md-left">
          <div class="d-flex gap-2">

          <v-btn
            :color="showGraphe ? 'blue' : 'grey'"
            variant="outlined"
            rounded="lg"
            prepend-icon="mdi-chart-bar"
            @click="showGraphe = !showGraphe"

          >
            Voir le graphe
          </v-btn>
          <!-- Nouveau bouton Vue par Zone -->
      <v-btn
        :color="viewByZone ? 'green' : 'grey'"
        variant="outlined"
        rounded="xl"
        prepend-icon="mdi-map-marker-multiple"
        @click="toggleViewByZone"
      >
        Vue par Zone
      </v-btn>
          </div>
       
      <!-- Indicateur à droite -->
    <div class="text-caption text-medium-emphasis">
      {{ viewByZone ? `${zonesCount} zones` : `${agencesData.length} agences` }}
    </div>
        </v-col>
        <v-col cols="12">
          <v-card class="elevation-3">
            <v-card-text class="pa-0">
                              <!-- Remplacer le tableau actuel par une version conditionnelle -->
                <div class="table-container" v-if="!showGraphe">
                  <div class="text-body-1 text-medium-emphasis">
                    Période couverte: {{ graphLabels[0] }} → {{ graphLabels[graphLabels.length - 1] }}
                    <v-chip v-if="viewByZone" color="green" size="small" class="ml-2">
                      Vue par Zone
                    </v-chip>
                  </div>

                  <table class="encours-table">
                    <thead>
                      <tr>
                        <!-- En-tête dynamique selon la vue -->
                        <th v-if="!viewByZone" class="header-agence">AGENCE</th>
                        <th v-if="viewByZone" class="header-agence">ZONE</th>
                        
                        <th class="header-nom">{{ viewByZone ? 'NOM ZONE' : 'NOM AGENCE' }}</th>
                        
                        <!-- Colonne nombre d'agences uniquement en vue zone -->
                        <th v-if="viewByZone" class="header-agence-count">
                          NOMBRE D'AGENCES
                        </th>
                        
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
                      <!-- Vue par agence -->
                      <template v-if="!viewByZone">
                        <tr v-for="agence in agencesData" :key="agence.code">
                          <td class="cell-agence">{{ agence.code }}</td>
                          <td class="cell-nom">{{ agence.nom }}</td>
                          <td 
                            v-for="column in tableColumns" 
                            :key="column.key"
                            class="cell-montant"
                          >
                            <div class="montant-container">
                              <div 
                                class="montant-value"
                                @click="goToDetail(column.key, agence.code)"
                                style="cursor:pointer;"
                              >
                                {{ formatUSD(getCellValue(agence, column)) }}
                              </div>
                              <div 
                                v-if="getCellEcart(agence, column) !== 0" 
                                class="ecart-indicator"
                                :class="getEcartClass(getCellEcart(agence, column))"
                              >
                                {{ formatUSD(getCellEcart(agence, column)) }}
                              </div>
                            </div>
                          </td>
                        </tr>
                      </template>
                      
                      <!-- Vue par zone -->
                      <template v-else>
                        <tr v-for="zone in zonesData" :key="zone.id">
                          <td class="cell-agence">
                            <v-chip size="small" color="green" variant="outlined">
                              Z{{ zone.id }}
                            </v-chip>
                          </td>
                          <td class="cell-nom">{{ zone.nom }}</td>
                          <td class="cell-agence-count">{{ zone.agenceCount }}</td>
                          <td 
                            v-for="column in tableColumns" 
                            :key="column.key"
                            class="cell-montant"
                          >
                            <div class="montant-container">
                              <div 
                                class="montant-value"
                               
                              >
                                {{ formatUSD(getZoneCellValue(zone, column)) }}
                              </div>
                              <div 
                                v-if="getZoneCellEcart(zone, column) !== 0" 
                                class="ecart-indicator"
                                :class="getEcartClass(getZoneCellEcart(zone, column))"
                              >
                                {{ formatUSD(getZoneCellEcart(zone, column)) }}
                              </div>
                            </div>
                          </td>
                        </tr>
                      </template>
                      
                      <!-- LIGNE DE TOTAL  -->
                      <tr v-if="hasResults" class="total-row">
                        <td class="cell-agence total-cell">
                          <strong>TOTAL</strong>
                        </td>
                        <td class="cell-nom total-cell">
                          <strong>
                            {{ viewByZone ? `${zonesData.length} zones` : `${agencesData.length} agences` }}
                          </strong>
                        </td>
                        
                        <!-- colonne par zone -->
                        <td v-if="viewByZone" class="cell-agence-count total-cell">
                          <strong>{{ getTotalAgenceCount() }}</strong>
                        </td>
                        
                        <td 
                          v-for="column in tableColumns" 
                          :key="column.key"
                          class="cell-montant total-cell"
                        >
                          <div class="montant-container">
                            <div class="montant-value total-montant">
                              {{ formatUSD(getTotalValue(column, viewByZone)) }}
                            </div>
                            <div 
                              v-if="getTotalEcart(column, viewByZone) !== 0" 
                              class="ecart-indicator total-ecart"
                              :class="getEcartClass(getTotalEcart(column, viewByZone))"
                            >
                              {{ formatUSD(getTotalEcart(column, viewByZone)) }}
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
        <v-card class="elevation-4 pa-4 rounded-lg">
          <div class="graph-header d-flex justify-space-between align-center mb-4">
            <div>
              <h3 class="text-h5 font-weight-bold graph-title">
                <v-icon color="primary" class="mr-2">mdi-chart-bar</v-icon>
                Évolution Décaissement
              </h3>
              <div class="graph-subtitle text-caption text-medium-emphasis">
                Analyse temporelle des montants totaux - Graphique en barres
              </div>
            </div>
            
            <div class="graph-legend d-flex align-center gap-3">
               <div class="legend-item d-flex align-center">
                <span class="text-caption ml-1">🔵Stable</span>
              </div>
              <div class="legend-item d-flex align-center">
                <span class="text-caption ml-1">🟢Hausse</span>
              </div>
              <div class="legend-item d-flex align-center">
                <span class="text-caption ml-1">🔴Baisse</span>
              </div>
            </div>
          </div>

          <div class="graph-container" style="position: relative; height: 600px;">
            <Bar
              :data="{
                labels: graphLabels,
                datasets: [{
                  label: 'Montant total',
                  data: graphValues,
                  backgroundColor: graphValues.map((value, index) => {
                    const ecart = graphEcarts[index] || 0
                    // if (ecart > 0) return 'rgba(76, 175, 80, 0.8)' // Vert pour hausse
                    // if (ecart < 0) return 'rgba(244, 67, 54, 0.8)' // Rouge pour baisse
                    return 'rgba(54, 162, 235, 0.6)' // Bleu pour stable
                  }),
                  borderColor: graphValues.map((value, index) => {
                    const ecart = graphEcarts[index] || 0
                    // if (ecart > 0) return 'rgba(76, 175, 80, 1)'
                    // if (ecart < 0) return 'rgba(244, 67, 54, 1)'
                    return 'rgba(25, 118, 210, 1)'
                  }),
                  borderWidth: 2,
                  borderRadius: 4,
                  barPercentage: 0.6,
                  categoryPercentage: 0.8
                }]
              }"
              :options="{
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                  intersect: false,
                  mode: 'index'
                },
                plugins: {
                  legend: { 
                    display: false
                  },
                  tooltip: {
                    usePointStyle: true,
                    borderWidth: 1,
                    cornerRadius: 8,
                    padding: 12,
                    boxPadding: 6,
                    callbacks: {
                      title: (context) => {
                        return ` ${context[0].label}`
                      },
                      label: (context) => {
                        const montant = context.parsed.y
                        const idx = context.dataIndex
                        const ecart = graphEcarts[idx] || 0
                        const trend = ecart > 0 ? 'Hausse' : ecart < 0 ? 'Baisse' : 'Stable'
                        
                        return [
                          ` Montant total: ${formatUSD(montant)}`,
                          ` Écart: ${formatUSD(ecart)} (${trend})`
                        ]
                      },
                      labelColor: (context) => {
                        const idx = context.dataIndex
                        const ecart = graphEcarts[idx] || 0
                        let color = '#1976d2'
                        if (ecart > 0) color = '#4caf50'
                        if (ecart < 0) color = '#f44336'
                        
                        return {
                          borderColor: color,
                          backgroundColor: color,
                          borderWidth: 2
                        }
                      }
                    }
                  }
                },
                scales: {
                  x: {
                    grid: {
                      display: true,
                      color: 'rgba(0, 0, 0, 0.05)',
                      drawBorder: false
                    },
                    ticks: {
                      padding: 10,
                      font: {
                        size: 12,
                        weight: '500'
                      },
                      maxRotation: 45,
                      minRotation: 45
                    },
                    title: {
                      display: true,
                      text: 'Période',
                      color: '#666',
                      font: {
                        size: 14,
                        weight: '600'
                      },
                      padding: { top: 10, bottom: 5 }
                    }
                  },
                  y: {
                    beginAtZero: true,
                    grid: {
                      display: true,
                      color: 'rgba(0, 0, 0, 0.05)',
                      drawBorder: false
                    },
                    ticks: {
                      padding: 10,
                      callback: function(value) {
                        if (value >= 1000000) {
                          return (value / 1000000).toFixed(1) + 'M'
                        } else if (value >= 1000) {
                          return (value / 1000).toFixed(0) + 'k'
                        }
                        return formatUSD(value)
                      },
                      font: {
                        size: 12,
                        weight: '500'
                      }
                    },
                    title: {
                      display: true,
                      text: 'Montant (en unités)',
                      color: '#666',
                      font: {
                        size: 14,
                        weight: '600'
                      },
                      padding: { top: 5, bottom: 10 }
                    }
                  }
                },
                animation: {
                  duration: 1000,
                  easing: 'easeInOutQuart'
                },
                hover: {
                  mode: 'nearest',
                  intersect: true
                }
              }"
            />
          </div>

          <div class="graph-footer mt-4 pt-3 border-top">
            <div class="d-flex justify-space-between align-center">
              <div class="graph-stats d-flex gap-4">
                <div class="stat-item">
                  <div class="text-caption text-medium-emphasis">Période couverte</div>
                  <div class="text-body-2 font-weight-medium">
                    {{ graphLabels[0] }} → {{ graphLabels[graphLabels.length - 1] }}
                  </div>
                </div>
                <div class="stat-item">
                  <div class="text-caption text-medium-emphasis">Points de données</div>
                  <div class="text-body-2 font-weight-medium">{{ graphValues.length }}</div>
                </div>
                <div class="stat-item">
                  <div class="text-caption text-medium-emphasis">Écart moyen</div>
                  <div class="text-body-2 font-weight-medium" :style="{ color: averageEcart >= 0 ? '#4caf50' : '#f44336' }">
                    {{ formatUSD(averageEcart) }}
                  </div>
                </div>
              </div>
              
              <div class="graph-actions">
                <v-btn
                  size="small"
                  variant="text"
                  color="primary"
                  @click="downloadChart"
                  class="mr-2"
                >
                  <v-icon left small>mdi-download</v-icon>
                  Exporter
                </v-btn>
                <v-btn
                  size="small"
                  variant="text"
                  color="primary"
                  @click="toggleFullscreen"
                >
                  <v-icon left small>mdi-fullscreen</v-icon>
                  Plein écran
                </v-btn>
              </div>
            </div>
          </div>
        </v-card>
      </div>
    </v-card>
  </v-container>
</template>
<script setup>
import { ref, computed, onMounted, inject } from "vue"
import axios from "axios"
import { Bar } from "vue-chartjs"
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
} from "chart.js"
import { useRouter } from 'vue-router'
import { formatUSD } from "../../composables/format_money"

import { useAgences } from '@/composables/useAgences'
import { formatDateToFrench,dateToYYYYMMDD,yyyymmddToDate } from "../../composables/format_date"


ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

const router = useRouter()
const api = inject("api")

// ========== REFS ==========
const selectedAgences = ref([])
const dateDebut = ref("")
const dateFin = ref("")
const selectedMonths = ref([])
const compare = ref(false)
const loading = ref(false)
const message = ref("")
const messageType = ref("info")
const showGraphe = ref(false)
const showSnackbar = ref(false)
const snackbarMessage = ref('')
const snackbarColor = ref('success')
const snackbarIcon = ref('mdi-check-circle')

// Vue par zone
const viewByZone = ref(false)
const zonesData = ref([])
const zonesList = ref([])

// Données
const datesList = ref([])
const agencesData = ref([])
const availableMonths = ref([])
const allData = ref({})


const dateDebutModel = ref(null)
const dateFinModel = ref(null)

const maxDate = computed(() => {
  return new Date() // Aujourd'hui
})


const onDateDebutChange = (newDate) => {
  dateDebut.value = dateToYYYYMMDD(newDate)
}

const onDateFinChange = (newDate) => {
  dateFin.value = dateToYYYYMMDD(newDate)
}


// Composables
const { 
  agencesList, 
  loading: agencesLoading, 
  error: agencesError,
  getAgenceByCode 
} = useAgences(api)

// ========== COMPUTED PROPERTIES ==========
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
  if (selectedMonths.value.length === 0) return 'Affichage Journalier'
  return `${selectedMonths.value.length} mois sélectionné(s) - Affichage mensuel`
})

const tableColumns = computed(() => {
  if (selectedMonths.value.length === 0) {
    return datesList.value.map(date => ({
      key: date,
      label: formatDateDisplay(date),
      type: 'daily'
    }))
  } else {
    return availableMonths.value
      .filter(month => selectedMonths.value.includes(month.value))
      .map(month => ({
        key: month.value,
        label: month.label,
        type: 'monthly'
      }))
  }
})

const graphLabels = computed(() => tableColumns.value.map(col => col.label))


const graphValues = computed(() => {
  if (viewByZone.value) {
    const totals = tableColumns.value.map(column => {
      return zonesData.value.reduce((sum, zone) => {
        return sum + getZoneCellValue(zone, column)
      }, 0)
    })
    return totals
  } else {
    return tableColumns.value.map(col => getTotalValue(col, false))
  }
})


const graphEcarts = computed(() => {
  if (viewByZone.value) {
    const ecarts = []
    const values = graphValues.value
    
    for (let i = 0; i < values.length; i++) {
      if (i === 0) {
        ecarts.push(0)
      } else {
        ecarts.push(values[i] - values[i-1])
      }
    }
    return ecarts
  } else {
    return tableColumns.value.map(col => getTotalEcart(col, false))
  }
})

const averageEcart = computed(() => {
  if (!graphEcarts.value || graphEcarts.value.length === 0) return 0
  const validEcarts = graphEcarts.value.filter(e => !isNaN(e))
  if (validEcarts.length === 0) return 0
  const sum = validEcarts.reduce((a, b) => a + b, 0)
  return sum / validEcarts.length
})

const zonesCount = computed(() => zonesList.value.length)

// Navigation
const goToDetail = (columnKey, agenceCode) => {
  router.push({
    path: "/app/detailDecais",
    query: { tableName: columnKey, agence: agenceCode }
  })
}


const goToAnalyseEncours = () => {
  router.push('/app/depotAnalyse')
}

// Notifications
const showNotification = (message, type = 'success') => {
  snackbarMessage.value = message
  snackbarColor.value = type
  
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

// Sélection agences/mois
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

// Gestion des zones
const loadZones = async () => {
  try {
    const response = await axios.get(`${api}/api/zones`, {
      headers: { 
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    })
    
    if (response.data.response?.success) {
      zonesList.value = response.data.response.data.map(zone => ({
        id: zone.id,
        nom: zone.nom,
        agences: []
      }))
      console.log('Zones chargées:', zonesList.value)
    }
  } catch (error) {
    console.error('Erreur chargement zones:', error)
    showNotification('Erreur lors du chargement des zones', 'error')
  }
}

const toggleViewByZone = async () => {
  console.log('=== toggleViewByZone ===')
  console.log('Mode mensuel actif:', selectedMonths.value.length > 0)
  console.log('Mois sélectionnés:', selectedMonths.value)
  
  if (viewByZone.value) {
    // passage vers le zone ou agence
    viewByZone.value = false
    showNotification(
      `Affichage par agence - ${agencesData.value.length} agences`,
      'info'
    )
    return
  }
  
  // if on a les donne a annalyser
  if (!agencesData.value.length || !datesList.value.length) {
    showNotification(
      'Veuillez d\'abord analyser des données d\'agences',
      'warning'
    )
    return
  }
  
  loading.value = true
  
  try {
    // Charger les zones si nécessaire
    if (zonesList.value.length === 0) {
      await loadZones()
    }
    
    // Regrouper par zone
    zonesData.value = await groupDataByZone()
    
    if (zonesData.value.length === 0) {
      showNotification(
        'Aucune donnée disponible pour l\'affichage par zone',
        'info'
      )
      loading.value = false
      return
    }
    
    // Passer en vue zone
    viewByZone.value = true
    
    const messageText = selectedMonths.value.length > 0
      ? `Affichage par zone - ${zonesData.value.length} zones (vue mensuelle)`
      : `Affichage par zone - ${zonesData.value.length} zones`
    
    showNotification(messageText, 'success')
    
  } catch (error) {
    console.error('Erreur regroupement par zone:', error)
    showNotification('Erreur lors du regroupement par zone', 'error')
  } finally {
    loading.value = false
  }
}

const groupDataByZone = async () => {
  console.log('=== groupDataByZone (version corrigée) ===')
  console.log('Mois sélectionnés:', selectedMonths.value)
  console.log('datesList:', datesList.value)
  
  // 1. Charger les agences avec zones depuis l'API
  let agencesWithZones = []
  try {
    const response = await axios.get(`${api}/api/agences/`, {
      headers: { 
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    })
    
    if (response.data.response?.success) {
      agencesWithZones = response.data.response.data
    }
  } catch (error) {
    console.error('Erreur chargement agences avec zones:', error)
    return []
  }
  
  // 2. Créer un mapping zone -> agences
  const zoneToAgences = {}
  zonesList.value.forEach(zone => {
    zoneToAgences[zone.id] = {
      nom: zone.nom,
      agences: []
    }
  })
  
  // 3. Associer chaque agence à sa zone
  agencesData.value.forEach(agence => {
    const agenceWithZone = agencesWithZones.find(a => a.code === agence.code)
    
    if (agenceWithZone && agenceWithZone.id_zone) {
      const zoneId = agenceWithZone.id_zone
      
      if (zoneToAgences[zoneId]) {
        zoneToAgences[zoneId].agences.push(agence)
      }
    }
  })
  
  // 4. Calculer les totaux
  const zonesWithData = []
  
  Object.entries(zoneToAgences).forEach(([zoneId, zoneData]) => {
    if (zoneData.agences.length > 0) {
      const zoneEncours = {}
      
      // Si on a une sélection de mois, filtrer les dates
      let datesToProcess = datesList.value
      if (selectedMonths.value.length > 0) {
        // Filtrer pour ne garder que les dates des mois sélectionnés
        datesToProcess = datesList.value.filter(date => {
          const monthKey = date.substring(0, 6) // YYYYMM
          return selectedMonths.value.includes(monthKey)
        })
      }
      
      // Calculer les totaux par date
      datesToProcess.forEach(date => {
        let totalMontant = 0
        let totalEcart = 0
        
        zoneData.agences.forEach(agence => {
          const agenceData = agence.encours[date] || {}
          totalMontant += agenceData.montant || 0
          totalEcart += agenceData.ecart || 0
        })
        
        zoneEncours[date] = {
          montant: totalMontant,
          ecart: totalEcart
        }
      })
      
      zonesWithData.push({
        id: zoneId,
        nom: zoneData.nom,
        encours: zoneEncours,
        agenceCount: zoneData.agences.length
      })
    }
  })
  
  return zonesWithData
}

// Ajouter cette computed property
const isMonthlyView = computed(() => selectedMonths.value.length > 0)

// Et modifier getZoneCellValue
const getZoneCellValue = (zone, column) => {
  if (column.type === 'daily') {
    // Vue journalière
    return zone.encours[column.key]?.montant || 0
  } else if (column.type === 'monthly') {
    // Vue mensuelle
    // Option 1: Si vous avez stocké monthlyEncours
    if (zone.monthlyEncours && zone.monthlyEncours[column.key]) {
      return zone.monthlyEncours[column.key].montant || 0
    }
    
    // Option 2: Calculer à la volée
    const monthKey = column.key
    const monthDates = datesList.value.filter(date => 
      date.startsWith(monthKey)
    )
    
    let totalMontant = 0
    monthDates.forEach(date => {
      totalMontant += zone.encours[date]?.montant || 0
    })
    
    return totalMontant
  }
  return 0
}
const getZoneCellEcart = (zone, column) => {
  if (column.type === 'daily') {
    return zone.encours[column.key]?.ecart || 0
  } else if (column.type === 'monthly') {
    // Pour les mois, on doit calculer l'écart différemment
    // Soit on calcule l'écart entre mois, soit on le laisse à 0
    return 0 // Ou implémenter un calcul d'écart mensuel si nécessaire
  }
  return 0
}


const getTotalAgenceCount = () => {
  if (!viewByZone.value) return 0
  return zonesData.value.reduce((sum, zone) => sum + zone.agenceCount, 0)
}

// Méthodes pour les cellules
const getCellValue = (agence, column) => {
  if (column.type === 'daily') {
    return agence.encours[column.key]?.montant || 0
  } else {
    return agence.monthlyEncours[column.key]?.montant || 0
  }
}

const getCellEcart = (agence, column) => {
  if (column.type === 'daily') {
    return agence.encours[column.key]?.ecart || 0
  } else {
    return agence.monthlyEncours[column.key]?.ecart || 0
  }
}

// Calculs totaux
const getTotalValue = (column, useZoneView = null) => {
  const isZoneView = useZoneView !== null ? useZoneView : viewByZone.value
  
  if (isZoneView) {
    let total = 0
    zonesData.value.forEach(zone => {
      total += getZoneCellValue(zone, column)
    })
    return total
  } else {
    let total = 0
    agencesData.value.forEach(agence => {
      total += getCellValue(agence, column)
    })
    return total
  }
}

const getTotalEcart = (column, useZoneView = null) => {
  const isZoneView = useZoneView !== null ? useZoneView : viewByZone.value
  
  if (isZoneView) {
    let totalEcart = 0
    zonesData.value.forEach(zone => {
      totalEcart += getZoneCellEcart(zone, column)
    })
    return totalEcart
  } else {
    let totalEcart = 0
    agencesData.value.forEach(agence => {
      totalEcart += getCellEcart(agence, column)
    })
    return totalEcart
  }
}

// Utilitaires de formatage
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

// Organisations de données
const calculateMonthlyEncours = (agences) => {
  const monthlyData = []

  agences.forEach(agenceCode => {
    const agenceInfo = agencesList.value.find(ag => ag.code === agenceCode)
    const monthlyEncours = {}

    availableMonths.value.forEach((month, index) => {
      const monthDates = datesList.value.filter(date => 
        date.startsWith(month.value)
      )

      let totalMontant = 0

      monthDates.forEach(date => {
        const decData = allData.value.decaissement[agenceCode]?.[date] || {}
        const decDebit = decData.total_montant_capital || 0
        totalMontant += decDebit 
      })

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

const organizeDailyData = (agences) => {
  const dailyData = []

  agences.forEach(agenceCode => {
    const agenceInfo = agencesList.value.find(ag => ag.code === agenceCode)
    const encours = {}

    datesList.value.forEach((date, index) => {
      const decData = allData.value.decaissement[agenceCode]?.[date] || {}
      const decDebit = decData.total_montant_capital || 0
      const decaissement = decDebit

      let ecart = 0
      if (index > 0) {
        const previousDate = datesList.value[index - 1]
        const previousEncours = encours[previousDate]?.montant || 0
        ecart = decaissement - previousEncours
      }

      encours[date] = {
        montant: decaissement,
        ecart: ecart
      }
    })

    dailyData.push({
      code: agenceInfo.code,
      nom: agenceInfo.nom,
      encours: encours,
      monthlyEncours: {}
    })
  })

  return dailyData
}

const organizeBaseData = (allData, agences) => {
  const allDates = new Set()
  
  Object.values(allData.decaissement).forEach(agenceData => {
    Object.keys(agenceData).forEach(date => allDates.add(date))
  })

  datesList.value = Array.from(allDates).sort()
}

// API calls
const fetchAllAgencesData = async (agences) => {
  const allData = {
    decaissement: {}
  }

  for (const agenceCode of agences) {
    const params = {
      agence: agenceCode,
      date_debut: dateDebut.value || undefined,
      date_fin: dateFin.value || undefined,
      compare: compare.value || false
    }

    Object.keys(params).forEach(key => params[key] === undefined && delete params[key])

    try {
      const response = await axios.get(`${api}/api/resume/decaissement`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
        params
      })

      if (Array.isArray(response.data) && response.data.length > 0) {
        if (!allData.decaissement[agenceCode]) {
          allData.decaissement[agenceCode] = {}
        }
        
        response.data.forEach(item => {
          const date = item.date_agence.date
          allData.decaissement[agenceCode][date] = item.data
        })
      }
    } catch (error) {
      console.error(`Erreur récupération décaissement - ${agenceCode}:`, error)
    }
  }

  return allData
}
const analyserEncours = async () => {
  loading.value = true
  message.value = ""
  datesList.value = []
  agencesData.value = []
  availableMonths.value = []
  selectedMonths.value = []
  viewByZone.value = false
  zonesData.value = []

  try {
    const agencesToAnalyze = selectedAgences.value.length > 0 
      ? selectedAgences.value 
      : agencesList.value.map(ag => ag.code)

    allData.value = await fetchAllAgencesData(agencesToAnalyze)
    
    organizeBaseData(allData.value, agencesToAnalyze)

    availableMonths.value = getMoisDispo(datesList.value)
    
    const dailyData = organizeDailyData(agencesToAnalyze)
    const monthlyData = calculateMonthlyEncours(agencesToAnalyze)
    
    agencesData.value = dailyData.map((dailyAgence, index) => ({
      ...dailyAgence,
      monthlyEncours: monthlyData[index].monthlyEncours
    }))

    if (agencesData.value.length === 0 || datesList.value.length === 0) {
      messageType.value = "info"
      message.value = " Aucune donnée disponible pour les critères sélectionnés"
      showNotification("Aucune donnée disponible pour les critères sélectionnés", 'info')
      return
    }
    
    // Si on est en vue par zone, recalculer les données zones
    if (viewByZone.value) {
      zonesData.value = await groupDataByZone()
    }
    
    messageType.value = "success"
    message.value = `Analyse terminée : ${agencesData.value.length} agences, ${datesList.value.length} dates disponibles`
    showNotification(`Analyse terminée : ${agencesData.value.length} agences, ${datesList.value.length} dates disponibles`, 'success')

    saveToLocalStorage()
    
  } catch (error) {
    console.error("Erreur analyse:", error)
    messageType.value = "error"
    message.value = "❌ Erreur lors de l'analyse des encours"
    showNotification("Erreur lors de l'analyse des encours", 'error')
  } finally {
    loading.value = false
  }
}

// Gestion du cache
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
      zonesData: zonesData.value,
      viewByZone: viewByZone.value,
      message: message.value,
      messageType: messageType.value
    }
    localStorage.setItem("decaissement_cache", JSON.stringify(snapshot))
  } catch (err) {
    console.error('Failed to save snapshot to localStorage', err)
  }
}

const restaurerDataCacher = () => {
  const raw = localStorage.getItem("decaissement_cache")
  if (!raw) return false
  
  try {
    const parsed = JSON.parse(raw)

    selectedAgences.value = (parsed.selectedAgences && parsed.selectedAgences.length)
      ? parsed.selectedAgences
      : agencesList.value.map(ag => ag.code)

    dateDebut.value = parsed.dateDebut || ""
    dateFin.value = parsed.dateFin || ""

    dateDebutModel.value = yyyymmddToDate(parsed.dateDebut) || null
    dateFinModel.value = yyyymmddToDate(parsed.dateFin) || null

    selectedMonths.value = parsed.selectedMonths || []
    datesList.value = parsed.datesList || []
    availableMonths.value = parsed.availableMonths || (datesList.value.length ? getMoisDispo(datesList.value) : [])
    agencesData.value = parsed.agencesData || []
    zonesData.value = parsed.zonesData || []
    viewByZone.value = parsed.viewByZone || false
    message.value = parsed.message || ""
    messageType.value = parsed.messageType || "info"

    return true
  } catch (err) {
    console.warn("Failed to parse decaissement_snapshot:", err)
    return false
  }
}

// Graphique
const downloadChart = () => {
  const canvas = document.querySelector('canvas')
  if (canvas) {
    const link = document.createElement('a')
    link.download = 'evolution-decaissement.png'
    link.href = canvas.toDataURL('image/png')
    link.click()
  }
}

const toggleFullscreen = () => {
  const graphContainer = document.querySelector('.graph-container')
  if (!document.fullscreenElement) {
    graphContainer?.requestFullscreen?.()
  } else {
    document.exitFullscreen?.()
  }
}

// ========== LIFECYCLE ==========
onMounted(() => {
  const restored = restaurerDataCacher()
  if (!restored) {
    selectedAgences.value = agencesList.value.map(ag => ag.code)
  }
  
  // Charger les zones au démarrage
  loadZones()
})
import { watch } from 'vue'

// Ajouter ce watch pour recalculer les données zones quand les mois changent
watch(selectedMonths, async (newMonths, oldMonths) => {
  if (viewByZone.value && newMonths.length !== oldMonths.length) {
    console.log('Mois changés, recalcul des données zones...')
    
    // Si on a déjà des données zones, les recalculer
    if (zonesData.value.length > 0) {
      loading.value = true
      try {
        zonesData.value = await groupDataByZone()
        showNotification('Données zones recalculées avec le nouveau filtre mois', 'info')
      } catch (error) {
        console.error('Erreur recalcul zones:', error)
      } finally {
        loading.value = false
      }
    }
  }
})
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
 /* STYLES DE NAVIGATION */
.navigation-container {
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 24px;
}

.navigation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.header-title {
  flex: 1;
}

.navigation-buttons {
  display: flex;
  flex-direction: row;
  gap: 16px;
  align-items: center;
  justify-content: flex-end;
}

.navigation-btn {
  min-width: 200px;
  border: 2px solid #1976d2;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.navigation-btn:hover {
  background-color: #1976d2;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(25, 118, 210, 0.3);
}

.navigation-btn .v-icon--left {
  margin-right: 8px;
}

.navigation-btn .v-icon--right {
  margin-left: 8px;
  opacity: 0.8;
}

/* Responsive design */
@media (max-width: 768px) {
  .navigation-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .navigation-buttons {
    justify-content: flex-start;
    width: 100%;
  }
  
  .navigation-btn {
    width: 100%;
    min-width: unset;
  }
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
/* Styles pour colonne "NOMBRE D'AGENCES" et mise en forme tableau (copié depuis depotAnalyse) */
.total-row {
  border-top: 2px solid #dee2e6;
}
.total-cell {
  font-weight: bold !important;
}
.total-montant {
  font-size: 1rem !important;
  color: #698bab !important;
  vertical-align: top;
}
.total-ecart {
  font-size: 0.9rem !important;
  background-color: rgba(164, 174, 185, 0.1) !important;
}
.total-row td {
  border-top: 2px solid #b4afaf !important;
  border-bottom: 2px solid #b4afaf !important;
}
.total-row .cell-agence,
.total-row .cell-nom {
  background: linear-gradient(135deg, #4b4c4e, #1565c0) !important;
  text-align: left !important;
}
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
  background-color: #7f8992 !important;
  text-align: center !important;
  border-top-left-radius: 12px;
}

.header-nom {
  width: 200px;
  background-color: hsl(211, 12%, 64%) !important;
}

.header-date {
  width: 140px;
  background-color: #324559 !important;
  text-align: center !important;
}

.header-agence-count {
  width: 100px;
  background-color: #546e7a !important;
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
  vertical-align: top;
}

.cell-agence-count {
  text-align: center;
  font-weight: 500;
  color: #546e7a;
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

.legend-color {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 2px;
  margin-right: 4px;
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