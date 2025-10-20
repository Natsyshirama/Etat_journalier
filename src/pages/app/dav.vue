<template>
  <v-container class="unified-container" fluid>
    <!-- Sélecteur de table commun -->
    <v-row class="mb-4">
      <v-col cols="12" md="6">
        <v-select
          v-model="selectedTable"
          :items="history.map(item => item.label)"
          label="Choisir une table"
          outlined
          dense
        />
      </v-col>
    </v-row>

    <!-- Résumé conditionnel selon l'onglet -->
    <ResumerDat v-if="selectedTable && activeTab === 0" :tableName="selectedTable" />
    <ResumerDav v-if="selectedTable && activeTab === 1" :tableName="selectedTable" />
    <ResumerEpr v-if="selectedTable && activeTab === 2" :tableName="selectedTable" />
    <!-- Onglets DAT/DAV -->
    <v-tabs v-model="activeTab" class="mb-4">
      <v-tab>DAT</v-tab>
      <v-tab>DAV</v-tab>
      <v-tab>EPR</v-tab>
    </v-tabs>

    <!-- Boutons Tableau/Dashboard -->
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
        <v-btn
          color="primary"
          @click="displayComponent = 'dashboard'"
          :outlined="displayComponent !== 'dashboard'"
        >
          Dashboard
        </v-btn>
      </v-col>
    </v-row>

    <!-- Contenu des onglets -->
    <v-window v-model="activeTab">
      <!-- Onglet DAT -->
      <v-window-item>
        <div v-if="selectedTable">
          <TableauDat
            v-if="displayComponent === 'tableau'"
            :tableName="selectedTable"
          />
          
          <DatGraphe
            v-if="displayComponent === 'dashboard'"
            :tableName="selectedTable"
          />
        </div>
      </v-window-item>

      <!-- Onglet DAV -->
      <v-window-item>
        <div v-if="selectedTable">
          <TableauDav
            v-if="displayComponent === 'tableau'"
            :tableName="selectedTable"
          />
          <DashboardDav
            v-if="displayComponent === 'dashboard'"
            :tableName="selectedTable"
          />
          
        </div>
      </v-window-item>
      
      <!-- Onglet EPR -->
      
      <v-window-item>
        <div v-if="selectedTable">
          <TableauEpr
            v-if="displayComponent === 'tableau'"
            :tableName="selectedTable"
          />
          
          <EprGraphe
            v-if="displayComponent === 'dashboard'"
            :tableName="selectedTable"
          />
        </div>
      </v-window-item>
    </v-window>

    <!-- Alerte si aucune table sélectionnée -->
    <v-alert
      v-if="!selectedTable"
      type="info"
      border="left"
      color="blue"
      dark
      class="mb-4"
    >
      Sélectionnez une table pour afficher les données
    </v-alert>
  </v-container>
</template>

<script setup>
import { ref, onMounted, watch } from "vue"
import axios from "axios"

// Composants DAT
import ResumerDat from "@/components/dat/ResumerDat.vue"
import TableauDat from "@/components/dat/TableauDat.vue"
import DatGraphe from "@/components/dat/DatGraphe.vue"

// Composants DAV
import ResumerDav from "@/components/dav/ResumerDav.vue"
import TableauDav from "@/components/dav/TableauDav.vue"
import DashboardDav from "@/components/dav/DavGraphe.vue" 

//composent Epr
import ResumerEpr from "@/components/epr/resumerEpr.vue"
import TableauEpr from "@/components/epr/TableauEpr.vue"
import EprGraphe from "@/components/epr/EprGraphe.vue"

const history = ref([])
const selectedTable = ref(localStorage.getItem("selectedTable") || null)
const activeTab = ref(0) // 0 = DAT, 1 = DAV
const displayComponent = ref("tableau") // "tableau" ou "dashboard"

const fetchTables = async () => {
  try {
    const res = await axios.get("http://127.0.0.1:8000/api/history/liste")
    history.value = res.data.history || []
  } catch (err) {
    console.error("Erreur lors du chargement de l'history:", err)
  }
}

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
.unified-container {
  max-height: 90vh;
  overflow-y: auto;
  padding-bottom: 20px;
}
</style>