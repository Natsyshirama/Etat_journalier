<template>
  <v-card class="mb-4" outlined>
    <v-card-title>
      Résumé de la table
    </v-card-title>
    <v-card-text v-if="summary">
      <v-row>
        <v-col cols="12" sm="6" md="3">
          <strong>Nom de table :</strong> {{ summary.table_name }}
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <strong>Nb lignes :</strong> {{ summary.nb_lignes }}
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <strong>Nb clients :</strong> {{ summary.nb_clients }}
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <strong>Total Capital :</strong> {{ summary.total_montant_capital }}
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <strong>Total Payé :</strong> {{ summary.total_montant_pay_total }}
        </v-col>
      </v-row>
    </v-card-text>
    <v-card-text v-else>
      <v-alert type="info" border="left" color="blue" dark>
        Aucun résumé disponible
      </v-alert>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, watch } from 'vue'
import axios from 'axios'


// Props : table sélectionnée depuis dat.vue
defineProps({
  tableName: String
})

const summary = ref(null)

// Charger le résumé depuis l'API
const fetchSummary = async (tableName) => {
  if (!tableName) {
    summary.value = null
    return
  }
  try {
    const res = await axios.get(`http://127.0.0.1:8000/api/dat/${tableName}/resume`)
    summary.value = res.data
  } catch (err) {
    console.error("Erreur fetch résumé :", err)
    summary.value = null
  }
}

// Watch la prop tableName pour mettre à jour le résumé
watch(() => tableName, (newTable) => {
  fetchSummary(newTable)
}, { immediate: true })
</script>
