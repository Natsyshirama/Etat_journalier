<template>
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
</template>

<script setup>
import { ref, watch, computed } from "vue"
import axios from "axios"

// Props : tableName choisi dans dat.vue
const props = defineProps({
  tableName: {
    type: String,
    required: true
  }
})

const headers = ref([])
const items = ref([])
const search = ref("")
const page = ref(1)
const itemsPerPage = ref(10)

const pageCount = computed(() =>
  Math.ceil(items.value.length / itemsPerPage.value)
)
const fetchTableData = async (tableName) => {
  if (!tableName) {
    items.value = []
    headers.value = []
    return
  }
  try {
    const res = await axios.get(`http://127.0.0.1:8000/api/dav/${tableName}`)
    console.log("Réponse API:", res.data)

    items.value = res.data.data || []  // <-- ici
    headers.value = (res.data.columns || []).map((col) => ({
      title: col,
      key: col
    }))
    page.value = 1
  } catch (err) {
    console.error("Erreur lors du chargement de la table:", err)
  }
}

// Recharger quand tableName change
watch(
  () => props.tableName,
  (newVal) => {
    fetchTableData(newVal)
  },
  { immediate: true }
)
</script>
