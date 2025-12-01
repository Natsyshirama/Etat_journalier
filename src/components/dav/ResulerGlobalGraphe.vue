<template>
  <v-card class="pa-4" outlined>
    <v-row align="center">
      <v-col cols="12" md="4">
        <v-select
          v-model="selectedType"
          :items="['dat', 'dav', 'epr','decaissement']"
          label="Type de table"
          outlined
          dense
        />
      </v-col>
      <v-col cols="12" md="8" class="d-flex align-center justify-end">
        <v-btn
          v-for="option in periodOptions"
          :key="option.value"
          :color="selectedPeriod === option.value ? 'success' : 'grey'"
          class="ml-2"
          size="small"
          @click="selectedPeriod = option.value"
          variant="tonal"
        >
          {{ option.label }}
        </v-btn>
      </v-col>
    </v-row>

    <!-- Graphique -->
    <div v-if="chartData" class="chart-container mt-6" style="width:100%;">
      <Line :data="filteredChartData" :options="chartOptions" />
    </div>

    <!-- Alerte -->
    <v-alert
      v-else
      type="info"
      border="left"
      color="green"
      dark
      class="mt-4"
    >
      Sélectionnez un type pour voir l’évolution.
    </v-alert>
  </v-card>
</template>

<script setup>
import { ref, watch, computed, inject } from "vue"
import axios from "axios"
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Filler
} from "chart.js"
import { Line } from "vue-chartjs"

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale, Filler)

const selectedType = ref("dat")
const chartData = ref(null)
const selectedPeriod = ref("1mo")
const periodOptions = [
  { label: "1j", value: "1d" },
  { label: "5j", value: "5d" },
  { label: "1 mois", value: "1mo" },
  { label: "1 an", value: "1y" },
  { label: "max", value: "" } // Ajout ici

]

const api = inject('api')
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: "top" },
    title: { display: true, text: "Évolution des totaux par table" },
    tooltip: {
      mode: 'index',
      intersect: false,
      callbacks: {
        label: function(context) {
          // Format nombre avec espace
          return `${context.dataset.label}: ${Number(context.parsed.y).toLocaleString('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
        }
      }
    }
  },
  interaction: {
    mode: 'nearest',
    axis: 'x',
    intersect: false
  },
  elements: {
    line: {
      tension: 0.3,
      borderWidth: 3,
      fill: true
    },
    point: {
      radius: 5,
      hoverRadius: 8,
      backgroundColor: "#fff",
      borderWidth: 2
    }
  },
  scales: {
    x: {
      grid: { display: false }
    },
    y: {
      grid: { color: "#e0e0e0" },
      ticks: {
        callback: function(value) {
          return Number(value).toLocaleString('fr-FR', { maximumFractionDigits: 0 })
        }
      }
    }
  }
}

watch(selectedType, async (newType) => {
  if (!newType) {
    chartData.value = null
    return
  }
  await fetchData(newType)
})

const fetchData = async (type) => {
  try {
    const res = await axios.get(`${api}/api/resume/all/${type}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
    })
    const data = res.data || []

    if (!data.length) {
      chartData.value = null
      return
    }

    data.sort((a, b) => a.table_name.localeCompare(b.table_name))
    const labels = data.map(d => d.table_name.replace(`${type}_`, ""))

    let datasets = []

    if (type === "dav") {
      datasets = [
        { label: "Total Débit DAV", data: data.map(d => d.total_debit_dav || 0), borderColor: "#F59E0B", backgroundColor: "rgba(245,158,11,0.10)" },
        { label: "Total Crédit DAV", data: data.map(d => d.total_credit_dav || 0), borderColor: "#EF4444", backgroundColor: "rgba(239,68,68,0.10)" },
      ]
    }

    if (type === "dat") {
      datasets = [
        { label: "Montant Capital", data: data.map(d => d.total_montant_capital || 0), borderColor: "#10B981", backgroundColor: "rgba(16,185,129,0.15)" },
        { label: "Montant Payé Total", data: data.map(d => d.total_montant_pay_total || 0), borderColor: "#F59E0B", backgroundColor: "rgba(245,158,11,0.10)" },
      ]
    }

    if (type === "epr") {
      datasets = [
        { label: "Total Débit EPR", data: data.map(d => d.total_debit_epr || 0), borderColor: "#F59E0B", backgroundColor: "rgba(245,158,11,0.10)" },
        { label: "Total Crédit EPR", data: data.map(d => d.total_credit_epr || 0), borderColor: "#EF4444", backgroundColor: "rgba(239,68,68,0.10)" },
      ]
    }
    if (type === "decaissement") {
      datasets = [
        { label: "Montant capital", data: data.map(d => d.total_montant_capital || 0), borderColor: "#10B981", backgroundColor: "rgba(16,185,129,0.15)" },
        { label: "Frais de dossier", data: data.map(d => d.total_frais_de_dossier || 0), borderColor: "#F59E0B", backgroundColor: "rgba(245,158,11,0.10)" },
      ]
    }

    chartData.value = {
      labels,
      datasets: datasets.map(ds => ({
        ...ds,
        borderWidth: 3,
        pointBorderColor: ds.borderColor,
        fill: true,
        tension: 0.3,
      })),
    }

  } catch (err) {
    console.error("Erreur lors du chargement :", err)
  }
}

const filteredChartData = computed(() => {
  if (!chartData.value) return null
  let nb = chartData.value.labels.length
  if (selectedPeriod.value === "1d") nb = 1
  else if (selectedPeriod.value === "5d") nb = 5
  else if (selectedPeriod.value === "1mo") nb = 30
  else if (selectedPeriod.value === "1y") nb = 365
  else if (selectedPeriod.value === "") nb = chartData.value.labels.length 

  // Prend les nb derniers points (si moins, prend tout)
  const start = Math.max(0, chartData.value.labels.length - nb)
  const labels = chartData.value.labels.slice(start)
  const datasets = chartData.value.datasets.map(ds => ({
    ...ds,
    data: ds.data.slice(start)
  }))
  return { labels, datasets }
})

fetchData(selectedType.value)
</script>

<style scoped>
.v-card {
  width: 100%;
  max-width: 100%;
  margin: 0;
  padding: 16px;
  box-sizing: border-box;
  background-color:#000000;
}
.chart-container {
  width: 100%;
  max-width: 100%;
  height: 500px;
}
</style>
