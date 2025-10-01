<template>
  <v-container class="dav-container">
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
    <v-row class="mb-4">
      <v-col cols="12" md="6">
        <v-btn
          color="primary"
          class="mr-2"
          @click="displayComponent = 'tableau'"
          :outlined="displayComponent !== 'tableau'"
        >
          Tableau
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
        <!--  -->
      </v-col>
    </v-row>

    <!-- Graphique (affiché uniquement sur Dashboard) -->
   

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
// import DatGraphe from "@/components/dav/DatGraphe.vue"

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
.dav-container {
  max-height: 90vh; /* limite la hauteur globale pour que tout tienne à l'écran */
  overflow-y: auto;  /* scroll vertical si nécessaire */
  padding-bottom: 20px;
}
/* 
.component-wrapper {
  max-height: 600px; 
  overflow-y: auto; /* scroll vertical si nécessaire */
  /* padding-bottom: 10px; */
/* } */ 
</style>
