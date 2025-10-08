<template>
  <div style="max-height: 600px; overflow-y: auto;">
    <v-data-table
      :headers="headers"
      :items="rows"
      :items-per-page="itemsPerPage"
      :page.sync="page"
      class="elevation-1"
      :search="search"
      dense
    >
      <!-- Barre de recherche -->
      <template v-slot:top>
        <v-text-field
          v-model="search"
          label="Rechercher"
          class="mx-4"
          clearable
          dense
        />
      </template>

      <!-- Pagination -->
      <template v-slot:footer>
        <v-pagination
          v-model="page"
          :length="pageCount"
          circle
          class="my-2"
        />
      </template>

      <!-- Message si vide -->
      <template v-slot:no-data>
        <v-alert type="info" border="left" color="blue" dark>
          Aucune donnée trouvée
        </v-alert>
      </template>
    </v-data-table>
  </div>
</template>

<script setup>
import { ref, computed, watch } from "vue"

const props = defineProps({
  columns: {
    type: Array,
    required: true
  },
  rows: {
    type: Array,
    required: true
  }
})

const search = ref("")
const page = ref(1)
const itemsPerPage = ref(10)

const headers = computed(() =>
  props.columns.map(col => ({
    title: col,
    key: col
  }))
)

const pageCount = computed(() =>
  Math.ceil(props.rows.length / itemsPerPage.value)
)

watch(
  () => props.rows,
  () => (page.value = 1)
)
</script>
