<template>
  <v-container>
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

    <!-- Tableau des données -->
    <v-row>
      <v-col cols="12">
        <!-- Conteneur scroll vertical -->
        <div style="max-height: 600px; overflow-y: auto;">
          <v-data-table
            :headers="headers"
            :items="items"
            :items-per-page="itemsPerPage"
            :page.sync="page"
            class="elevation-1"
            :search="search"
            dense
          >
            <!-- Recherche -->
            <template v-slot:top>
              <v-text-field
                v-model="search"
                label="Rechercher"
                class="mx-4"
                clearable
                dense
              />
            </template>

            <!-- Pagination footer -->
            <template v-slot:footer>
              <v-pagination
                v-model="page"
                :length="pageCount"
                circle
                class="my-2"
              />
            </template>

            <!-- Message quand pas de données -->
            <template v-slot:no-data>
              <v-alert type="info" border="left" color="blue" dark>
                Aucune donnée trouvée
              </v-alert>
            </template>
          </v-data-table>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted, watch, computed } from "vue"
import axios from "axios"

const tables = ref([])             // Liste des tables DAT
const selectedTable = ref(null)    // Table sélectionnée
const headers = ref([])            // Colonnes dynamiques
const items = ref([])              // Lignes de données
const search = ref("")             // Texte de recherche

// Pagination frontend
const page = ref(1)
const itemsPerPage = ref(10)

const pageCount = computed(() => {
  return Math.ceil(items.value.length / itemsPerPage.value)
})

// Liste des items affichés sur la page courante
const paginatedItems = computed(() => {
  const start = (page.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return items.value.slice(start, end)
})

// Charger la liste des tables depuis le backend
const fetchTables = async () => {
  try {
    const res = await axios.get("http://127.0.0.1:8000/api/dat/liste_dat")
    tables.value = res.data.tables
  } catch (err) {
    console.error("Erreur lors du chargement des tables:", err)
  }
}

// Charger les données d'une table sélectionnée
const fetchTableData = async (tableName) => {
  try {
    const res = await axios.get(`http://127.0.0.1:8000/api/dat/${tableName}`)
    items.value = res.data.rows || []

    // Colonnes dynamiques depuis backend
    headers.value = res.data.columns.map((col) => ({
      title: col,
      key: col
    }))

    page.value = 1  // reset pagination
  } catch (err) {
    console.error("Erreur lors du chargement de la table:", err)
  }
}

// Recharger les données quand une table est sélectionnée
watch(selectedTable, (newVal) => {
  if (newVal) fetchTableData(newVal)
})

onMounted(() => {
  fetchTables()
})
</script>
