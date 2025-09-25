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
     <!-- <div>
    <h1 class="text-2xl font-bold mb-6">Page Données</h1>
    <Dashboard />
    </div> -->
    <!-- Résumé (au-dessus du tableau) -->
    <Resumer v-if="selectedTable" :tableName="selectedTable" />

    <!-- Tableau des données -->
    <v-row>
      <v-col cols="12">
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
            <template v-slot:top>
              <v-text-field
                v-model="search"
                label="Rechercher"
                class="mx-4"
                clearable
                dense
              />
            </template>

            <template v-slot:footer>
              <v-pagination
                v-model="page"
                :length="pageCount"
                circle
                class="my-2"
              />
            </template>

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
import Resumer from "@/components/dat/Resumer.vue"
import Dashboard from "@/components/dat/grapheDat.vue";


const tables = ref([])
const selectedTable = ref(null)
const headers = ref([])
const items = ref([])
const search = ref("")
const page = ref(1)
const itemsPerPage = ref(10)

const pageCount = computed(() => Math.ceil(items.value.length / itemsPerPage.value))

const fetchTables = async () => {
  try {
    const res = await axios.get("http://127.0.0.1:8000/api/dat/liste_dat")
    tables.value = res.data.tables
  } catch (err) {
    console.error("Erreur lors du chargement des tables:", err)
  }
}

const fetchTableData = async (tableName) => {
  if (!tableName) {
    items.value = []
    headers.value = []
    return
  }
  try {
    const res = await axios.get(`http://127.0.0.1:8000/api/dat/${tableName}`)
    items.value = res.data.rows || []
    headers.value = res.data.columns.map((col) => ({
      title: col,
      key: col
    }))
    page.value = 1
  } catch (err) {
    console.error("Erreur lors du chargement de la table:", err)
  }
}

watch(selectedTable, (newVal) => {
  fetchTableData(newVal)
})

onMounted(() => {
  fetchTables()
})
</script>
