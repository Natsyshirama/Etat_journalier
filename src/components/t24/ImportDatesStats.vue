<template>
  <v-card class="import-dates-card">
    <v-card-title class="d-flex align-center justify-space-between">
      <span>
        <v-icon start>mdi-history</v-icon>
        Historique des imports
      </span>

      <v-btn
        icon="mdi-refresh"
        :loading="loading"
        title="Actualiser"
        aria-label="Actualiser"
        @click="loadImportDates"
      />
    </v-card-title>

    <v-divider />

    <v-card-text>
      <v-alert
        v-if="error"
        type="error"
        closable
        class="mb-4"
      >
        {{ error }}
      </v-alert>

      <v-tabs v-model="activeTab" color="primary" class="mb-4">
        <v-tab value="t24">
          <v-icon start>mdi-file-table</v-icon>
          Imports T24
        </v-tab>

        <v-tab value="powercard">
          <v-icon start>mdi-credit-card</v-icon>
          Imports PowerCard
        </v-tab>
      </v-tabs>

      <v-window v-model="activeTab">
        <v-window-item value="t24">
          <v-data-table
            :headers="headers"
            :items="t24Imports"
            :loading="loading"
            :items-per-page="10"
            fixed-header
            height="450"
            hover
          >
            <template #item.import_date="{ item }">
              <v-chip color="primary" size="small" variant="tonal">
                {{ item.import_date }}
              </v-chip>
            </template>

            <template #item.row_count="{ item }">
              <v-chip color="blue" size="small">
                {{ item.row_count }}
              </v-chip>
            </template>

            <template #item.start_datetime="{ item }">
              {{ item.start_datetime || '-' }}
            </template>

            <template #item.end_datetime="{ item }">
              {{ item.end_datetime || '-' }}
            </template>

            <template #item.created_at="{ item }">
              {{ item.created_at || '-' }}
            </template>

            <template #item.actions="{ item }">
              <v-btn
                icon="mdi-delete"
                color="error"
                variant="text"
                size="small"
                title="Supprimer cet import"
                aria-label="Supprimer cet import"
                @click="askDelete(item, 't24')"
              />
            </template>

            <template #no-data>
              Aucune importation T24 trouvée
            </template>
          </v-data-table>
        </v-window-item>

        <v-window-item value="powercard">
          <v-data-table
            :headers="headers"
            :items="powerCardImports"
            :loading="loading"
            :items-per-page="10"
            fixed-header
            height="450"
            hover
          >
            <template #item.import_date="{ item }">
              <v-chip color="primary" size="small" variant="tonal">
                {{ item.import_date }}
              </v-chip>
            </template>

            <template #item.row_count="{ item }">
              <v-chip color="blue" size="small">
                {{ item.row_count }}
              </v-chip>
            </template>

            <template #item.start_datetime="{ item }">
              {{ item.start_datetime || '-' }}
            </template>

            <template #item.end_datetime="{ item }">
              {{ item.end_datetime || '-' }}
            </template>

            <template #item.created_at="{ item }">
              {{ item.created_at || '-' }}
            </template>

            <template #item.actions="{ item }">
              <v-btn
                icon="mdi-delete"
                color="error"
                variant="text"
                size="small"
                title="Supprimer cet import"
                aria-label="Supprimer cet import"
                @click="askDelete(item, 'powercard')"
              />
            </template>

            <template #no-data>
              Aucune importation PowerCard trouvée
            </template>
          </v-data-table>
        </v-window-item>
      </v-window>

      
      <v-dialog v-model="deleteDialog" max-width="450">
  <v-card>
    <v-card-title>
      Confirmer la suppression
    </v-card-title>

    <v-card-text>
      <p class="mb-4">
        Voulez-vous supprimer toutes les transactions
        <strong>{{ selectedSource }}</strong>
        de la date
        <strong>{{ selectedImport?.import_date }}</strong> ?
      </p>

      <v-alert
        v-if="deleteError"
        type="error"
        variant="tonal"
        class="mb-4"
      >
        {{ deleteError }}
      </v-alert>

      <v-text-field
        v-model="deletePassword"
        type="password"
        label="Mot de passe administrateur"
        variant="outlined"
        :disabled="deleteLoading"
        @keyup.enter="confirmDelete"
      />
    </v-card-text>

    <v-card-actions>
      <v-spacer />

      <v-btn
        variant="text"
        :disabled="deleteLoading"
        @click="deleteDialog = false"
      >
        Annuler
      </v-btn>

      <v-btn
        color="error"
        :loading="deleteLoading"
        @click="confirmDelete"
      >
        <v-icon start>mdi-delete</v-icon>
        Supprimer
      </v-btn>
    </v-card-actions>
  </v-card>
</v-dialog>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { inject, onMounted, ref } from 'vue'
import { useImportDates } from '../../composables/useImportDates'

const api = inject('api')
const activeTab = ref('t24')

const {
  loading,
  error,
  t24Imports,
  powerCardImports,
  setApiUrl,
  loadImportDates
} = useImportDates()

const headers = [
  {
    title: "Date d'import",
    key: 'import_date',
    width: 140
  },
  {
    title: 'Nombre de lignes',
    key: 'row_count',
    width: 150
  },
  {
    title: 'Date début',
    key: 'start_datetime',
    width: 180
  },
  {
    title: 'Date fin',
    key: 'end_datetime',
    width: 180
  },
  {
    title: 'Créé le',
    key: 'created_at',
    width: 180
  },
  {
    title: 'Actions',
    key: 'actions',
    sortable: false,
    width: 90
  }
]

const deleteDialog = ref(false)
const deleteLoading = ref(false)
const deleteError = ref('')
const deletePassword = ref('')
const selectedImport = ref(null)
const selectedSource = ref('')

const askDelete = (item, source) => {
  selectedImport.value = item
  selectedSource.value = source
  deletePassword.value = ''
  deleteError.value = ''
  deleteDialog.value = true
}

const confirmDelete = async () => {
  if (!deletePassword.value) {
    deleteError.value = 'Veuillez saisir votre mot de passe'
    return
  }

  deleteLoading.value = true
  deleteError.value = ''

  try {
    const formData = new FormData()
    formData.append('admin_password', deletePassword.value)

    const response = await fetch(
      `${api}/api/imports/${selectedSource.value}/${selectedImport.value.import_date}`,
      {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        },
        body: formData
      }
    )

    const data = await response.json()

    if (!response.ok || data.status !== 'success') {
      throw new Error(data.detail || 'Erreur lors de la suppression')
    }

    deleteDialog.value = false
    selectedImport.value = null
    deletePassword.value = ''

    await loadImportDates()
  } catch (exception) {
    deleteError.value = exception.message
  } finally {
    deleteLoading.value = false
  }
}

onMounted(async () => {
  setApiUrl(api)
  await loadImportDates()
})
</script>

<style scoped>
.import-dates-card {
  border-radius: 12px;
}

:deep(.v-table__wrapper) {
  overflow-y: auto;
  overflow-x: auto;
}

:deep(.v-data-table__th) {
  white-space: nowrap;
}

:deep(.v-data-table__td) {
  white-space: nowrap;
}
</style>