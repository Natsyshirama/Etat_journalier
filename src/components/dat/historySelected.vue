<template>
  <v-card class="pa-4" outlined>
    <v-card-title class="text-h6">Historique des insertions</v-card-title>
    <v-divider></v-divider>

    <v-list>
  <v-list-item
    v-for="item in history"
    :key="item.label"
    @click="selectHistory(item)"
    class="d-flex align-center justify-space-between"
  >
    <!-- Nom de la table -->
    <v-list-item-title>{{ item.label }}</v-list-item-title>

    <!-- Statuts -->
    <div class="d-flex gap-2">
      <!-- Statut DAT -->
      <v-chip
        :color="item.dat_status ? 'green' : 'red'"
        dark
        small
      >
        DAT
      </v-chip>

      <!-- Statut DAV -->
      <v-chip
        :color="item.dav_status ? 'green' : 'red'"
        dark
        small
      >
        DAV
      </v-chip>
    </div>
  </v-list-item>
</v-list>

  </v-card>
</template>

<script setup>
import { ref, onMounted, defineExpose } from "vue"
import axios from "axios"

const history = ref([])

const fetchHistory = async () => {
  try {
    const res = await axios.get("http://127.0.0.1:8000/api/history/liste")
    history.value = res.data.history || []
  } catch (err) {
    console.error("Erreur lors du chargement de l'history_insert:", err)
  }
}

// Émettre au parent quand on clique
const emit = defineEmits(["select"])
const selectHistory = (item) => {
  emit("select", item)
}

// Exposer la fonction pour le parent
defineExpose({ fetchHistory })

onMounted(fetchHistory)
</script>
