<template>
  <v-card class="rounded-lg elevation-1" variant="outlined">
    <!-- En-tête du tableau -->
    <v-card-title class="d-flex align-center pa-4">
      <v-icon color="primary" class="mr-2">mdi-table</v-icon>
      Liste des Agences
      <v-chip v-if="agences.length > 0" class="ml-2" color="primary" size="small">
        {{ agences.length }}
      </v-chip>
    </v-card-title>
    
    <v-divider />
    
    <!-- Tableau -->
    <v-data-table
      :headers="headers"
      :items="paginatedAgences"
      :loading="loading"
      :search="search"
      hide-default-footer
      class="elevation-0"
      item-value="code"
      density="comfortable"
      hover
    >
    
      <!-- En-têtes personnalisées -->
      <template #headers>
        <tr>
          <th v-for="header in headers" :key="header.key" class="text-left">
            <div class="d-flex align-center">
              {{ header.title }}
              <v-icon v-if="header.sortable" size="small" class="ml-1">mdi-sort</v-icon>
            </div>
          </th>
        </tr>
      </template>
      
      <!-- Skeleton loader -->
      <template #loading>
        <tbody>
          <tr v-for="i in 5" :key="i">
            <td v-for="header in headers" :key="header.key">
              <v-skeleton-loader type="text" width="80%" />
            </td>
          </tr>
        </tbody>
      </template>
      
      <!-- Aucune donnée -->
      <template #no-data>
        <div class="pa-8 text-center">
          <v-icon size="large" color="grey-lighten-1" class="mb-2">mdi-database-off</v-icon>
          <div class="text-body-1 text-medium-emphasis">Aucune agence trouvée</div>
          <v-btn v-if="!loading" color="primary" variant="text" @click="$emit('refresh')" class="mt-2">
            <v-icon left>mdi-refresh</v-icon>
            Recharger
          </v-btn>
        </div>
      </template>
      
      <!-- Ligne de données -->
      <template #item="{ item }">
        <tr>
          <!-- Code -->
          <td>
            <div class="d-flex align-center">
              <v-chip size="small"  class="mr-2">
                <v-icon size="small" class="mr-1">mdi-identifier</v-icon>
                {{ item.code }}
              </v-chip>
            </div>
          </td>
          
          <!-- Sous-code -->
          <td>
            <v-chip size="small" ">
              <v-icon size="small" class="mr-1">mdi-tag</v-icon>
              {{ item.souscode }}
            </v-chip>
          </td>
          
          <!-- Nom -->
          <td>
            <div class="d-flex align-center">
              <v-icon color="grey" size="small" class="mr-2">mdi-bank</v-icon>
              {{ item.nom }}
            </div>
          </td>
          <!-- Dans le template, ajouter une nouvelle colonne -->
          <td>
            <v-chip v-if="item.nom_zone" size="small" color="primary" variant="outlined">
              <v-icon size="small" class="mr-1">mdi-map-marker</v-icon>
              {{ item.nom_zone }}
            </v-chip>
            <span v-else class="text-caption text-medium-emphasis">Non définie</span>
          </td>
          
          <!-- Date de création -->
          <td>
            <div class="text-caption">
              {{ formatDate(item.created_at) }}
            </div>
          </td>
          
          <!-- Dernière modification -->
          <td>
            <div class="text-caption">
              {{ formatDate(item.updated_at) }}
            </div>
          </td>
          
          <!-- Actions -->
          <td>
            <div class="d-flex gap-1">
              <!-- Modifier -->
              <v-btn
                icon
                size="small"
                color="warning"
                variant="text"
                @click="$emit('edit-agence', item)"
                title="Modifier"
              >
                <v-icon size="small">mdi-pencil</v-icon>
              </v-btn>
              
              <!-- Supprimer -->
              <v-btn
                icon
                size="small"
                color="error"
                variant="text"
                @click="$emit('delete-agence', item)"
                title="Supprimer"
              >
                <v-icon size="small">mdi-delete</v-icon>
              </v-btn>
              
              
            </div>
          </td>
        </tr>
      </template>
      
      <template #bottom>
        <div class="d-flex justify-space-between align-center pa-4">
          <div class="text-caption text-medium-emphasis">
            Affichage de {{ pageStart }} à {{ pageEnd }} sur {{ agences.length }} agences
          </div>
          <v-pagination
            v-model="currentPage"
            :length="pageCount"
            :total-visible="10"
            density="comfortable"
          />
        </div>
      </template>
    </v-data-table>
  </v-card>
</template>

<script setup>
import { ref, watch,computed, defineProps, defineEmits } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  agences: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  itemsPerPage: {
    type: Number,
    default: 10
  }
})

const emit = defineEmits(['edit-agence', 'delete-agence', 'refresh'])

const router = useRouter()
const search = ref('')
const currentPage = ref(1)

const headers = [
  {
    title: 'Code',
    key: 'code',
    sortable: true,
    width: '15%'
  },
  {
    title: 'Sous-Code',
    key: 'souscode',
    sortable: true,
    width: '10%'
  },
  {
    title: 'Nom',
    key: 'nom',
    sortable: true,
    width: '30%'
  },
  
  {
    title: 'Zone',
    key: 'nom_zone',
    sortable: true,
    width: '15%'
  },
  {
    title: 'Créé le',
    key: 'created_at',
    sortable: true,
    width: '15%'
  },
  {
    title: 'Modifié le',
    key: 'updated_at',
    sortable: true,
    width: '15%'
  },
  {
    title: 'Actions',
    key: 'actions',
    sortable: false,
    width: '15%',
    align: 'center'
  }
]

const pageCount = computed(() => {
  return Math.ceil(props.agences.length / props.itemsPerPage)
})

const pageStart = computed(() => {
  return (currentPage.value - 1) * props.itemsPerPage + 1
})

const pageEnd = computed(() => {
  const end = currentPage.value * props.itemsPerPage
  return end > props.agences.length ? props.agences.length : end
})

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}


const paginatedAgences = computed(() => {
  const start = (currentPage.value - 1) * props.itemsPerPage
  const end = start + props.itemsPerPage
  return props.agences.slice(start, end)
})


const viewDetails = (agence) => {
  router.push({
    path: '/app/agence-details',
    query: { code: agence.code }
  })
}
watch(() => props.agences, () => {
  currentPage.value = 1
})

</script>

<style scoped>
.v-data-table :deep(.v-data-table__td) {
  padding: 12px 16px;
}

.v-data-table :deep(.v-data-table__th) {
  background-color: #f8f9fa;
  font-weight: 600;
}

.v-data-table :deep(tr:hover) {
  background-color: rgba(25, 118, 210, 0.04) !important;
}

.v-btn--icon.v-btn--density-default {
  width: 32px;
  height: 32px;
}
</style>