<template>
  <v-container class="dat-container">
    <!-- Sélecteur de table -->
    <v-row class="mb-4">
      <v-col cols="12" md="6">
        <v-select
          v-model="selectedTable"
          :items="tables"
          label="Choisir une table"
          outlined
          dense
        />
      </v-col>
    </v-row>

    <!-- Résumé -->
    <Resumer v-if="selectedTable" :tableName="selectedTable" />

    <!-- Bouton Dashboard / Tableau -->
    <!-- Bouton Toggle -->
   <!-- Bouton Toggle avec icône -->
<v-row class="mb-4">
  <v-col cols="12" md="6">
    <v-btn
      variant="text"
      @click="toggleComponent"
      class="toggle-btn"
    >
      <v-icon size="28">
        {{ displayComponent === 'tableau' ? 'mdi-view-dashboard' : 'mdi-table' }}
      </v-icon>
    </v-btn>
  </v-col>
</v-row>


    <!-- Composants conditionnels -->
    <v-row>
      <v-col cols="12" class="component-wrapper">
        <Tableau
          v-if="selectedTable && displayComponent === 'tableau'"
          :tableName="selectedTable"
        />
        <Dashboard
          v-if="selectedTable && displayComponent === 'dashboard'"
          :tableName="selectedTable"
        />
      </v-col>
    </v-row>

    Graphique (affiché uniquement sur Dashboard)
    <v-row>
      <v-col cols="12" class="component-wrapper">
        <DatGraphe
          v-if="selectedTable && displayComponent === 'dashboard'"
          :tableName="selectedTable"
        />
      </v-col>
    </v-row>

    <!-- Alerte par défaut -->
    <v-alert
      v-if="!selectedTable"
      type="info"
      border="left"
      color="blue"
      dark
      class="mb-4"
    >
      Sélectionnez une table
    </v-alert>
  </v-container>
</template>
<script setup>
import { ref, onMounted, watch } from "vue"
import axios from "axios"
import Resumer from "@/components/dav/ResumerDav.vue"
import Tableau from "@/components/dav/TableauDav.vue"
import DatGraphe from "@/components/dav/DavGraphe.vue"

const tables = ref([])
const selectedTable = ref(localStorage.getItem("selectedTable") || null) // récupère la valeur sauvegardée
const displayComponent = ref("tableau")

const fetchTables = async () => {
  try {
    const res = await axios.get("http://127.0.0.1:8000/api/dav/liste_dav")
    tables.value = res.data.tables
  } catch (err) {
    console.error("Erreur lors du chargement des tables:", err)
  }
}

const toggleComponent = () => {
  displayComponent.value = displayComponent.value === "tableau" ? "dashboard" : "tableau"
}


// Sauvegarder automatiquement dans localStorage dès que selectedTable change
watch(selectedTable, (newVal) => {
  if (newVal) {
    localStorage.setItem("selectedTable", newVal)
  }
})

onMounted(() => {
  fetchTables()
})
</script>


<style scoped>
.dat-container {
  max-height: 90vh; /* limite la hauteur globale pour que tout tienne à l'écran */
  overflow-y: auto;  /* scroll vertical si nécessaire */
  padding-bottom: 20px;
}
.toggle-btn {
  background-color: transparent !important;
  box-shadow: none !important;
  color: #3f4143; /* couleur de l’icône (bleu Vuetify par défaut) */
}

.toggle-btn:hover {
  background: rgb(9, 161, 62) !important; /* léger effet hover */
}

/* 
.component-wrapper {
  max-height: 600px; 
  overflow-y: auto; /* scroll vertical si nécessaire */
  /* padding-bottom: 10px; */
/* } */ 
</style>
