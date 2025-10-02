<template>
  <v-container>
    <!-- Liste des history_insert -->
    <HistorySelected ref="historyRef" @select="onSelectHistory" />

    <v-row class="mt-6" v-if="selectedHistory">
      <v-col cols="12" class="text-center">
        <h3>Table sélectionnée : {{ selectedHistory.label }}</h3>

        <!-- Si non initialisé -->
        <v-btn
          v-if="!selectedHistory.dat_status || !selectedHistory.dav_status"
          color="primary"
          class="mt-4"
          @click="initializeTable"
          :loading="loading"
        >
          Initialiser                         
        </v-btn>

        <!-- Si déjà initialisé -->
        <v-alert
          v-else
          type="success"
          border="start"
          class="mt-4"
        >
          Déjà initialisé
        </v-alert>

        <!-- Message de retour après action -->
        <v-alert
          v-if="message"
          :type="messageType"
          border="start"
          class="mt-4"
        >
          {{ message }}
        </v-alert>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from "vue"
import axios from "axios"
import HistorySelected from "@/components/dat/HistorySelected.vue"

const selectedHistory = ref(null)
const loading = ref(false)
const message = ref("")
const messageType = ref("info")

// Référence vers le composant enfant pour rafraîchir la liste
const historyRef = ref(null)

const onSelectHistory = (item) => {
  selectedHistory.value = item
  message.value = "" // reset message à chaque sélection
}

const initializeTable = async () => {
  if (!selectedHistory.value) return

  loading.value = true
  try {
    const res = await axios.post(
      `http://127.0.0.1:8000/api/dat/initialise/${selectedHistory.value.label}`
    )

    // Vérifier si le backend renvoie status "success"
    if (res.data.status === "success") {
      message.value = res.data.message || "Initialisation réussie ✅"
      messageType.value = "success"

      // Rafraîchir la liste
      await historyRef.value.fetchHistory()

      // Mettre à jour selectedHistory
      const updated = historyRef.value.history.find(
        h => h.label === selectedHistory.value.label
      )
      if (updated) selectedHistory.value = updated
    } else {
      // Si backend renvoie "error" mais status HTTP 200
      message.value = res.data.message || "tss lors de l'initialisation ❌"
      messageType.value = "error"
    }

  } 
  finally {
    loading.value = false
  }
}

</script>
