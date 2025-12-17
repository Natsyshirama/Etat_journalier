<template>
  <v-container class="pa-0 full-container" fluid>
    <v-card class="pa-8 rounded-0 elevation-2 fade-in full-card" flat>
      <div class="navigation-container mb-6">
        <div class="navigation-header">
          <div class="header-title">
            <h1 class="text-h4 font-weight-bold mb-2">
              <v-icon color="primary" class="mr-3">mdi-bank</v-icon>
              Gestion des Agences
            </h1>
            <p class="text-subtitle-1 text-medium-emphasis">
              Gérez les agences bancaires de votre réseau
            </p>
          </div>
          
          <div class="navigation-buttons">
            <v-btn
              color="primary"
              size="large"
              rounded="lg"
              @click="openAddDialog"
              class="navigation-btn"
              prepend-icon="mdi-plus"
            >
              Nouvelle Agence
            </v-btn>
          </div>
        </div>
      </div>

      <!-- Barre de recherche et filtres -->
      <v-card class="mb-6 pa-4 rounded-lg elevation-1" variant="outlined">
        <v-row dense align="center">
          <!-- Recherche -->
          <v-col cols="12" md="6">
            <v-text-field
              v-model="searchTerm"
              placeholder="Rechercher une agence par code, sous-code ou nom..."
              prepend-inner-icon="mdi-magnify"
              variant="outlined"
              rounded="lg"
              clearable
              hide-details
              @update:model-value="handleSearch"
            />
          </v-col>
          
          <!-- Filtres -->
          <v-col cols="12" md="3">
            <v-select
              v-model="itemsPerPage"
              :items="[10, 25, 50, 100]"
              label="Éléments par page"
              variant="outlined"
              rounded="lg"
              density="comfortable"
              hide-details
            />
          </v-col>
          
          <v-col cols="12" md="3" class="text-right">
            <v-btn
              variant="text"
              color="grey-darken-1"
              @click="refreshAgences"
              :loading="loading"
              prepend-icon="mdi-refresh"
            >
              Actualiser
            </v-btn>
          </v-col>
        </v-row>
      </v-card>

      <!-- Tableau des agences -->
      <TableauAgence
        :agences="filteredAgences"
        :loading="loading"
        :items-per-page="itemsPerPage"
        @edit-agence="openEditDialog"
        @delete-agence="confirmDelete"
        @refresh="refreshAgences"
      />

      <!-- Statistiques -->
      <v-card v-if="!loading" class="mt-6 pa-4 rounded-lg elevation-1" variant="outlined">
        <v-row dense>
          <v-col cols="6" md="3">
            <div class="stat-card">
              <div class="stat-label text-caption text-medium-emphasis">
                Total Agences
              </div>
              <div class="stat-value text-h5 font-weight-bold">
                {{ agences.length }}
              </div>
            </div>
          </v-col>
          
          <v-col cols="6" md="3">
            <div class="stat-card">
              <div class="stat-label text-caption text-medium-emphasis">
                Résultats affichés
              </div>
              <div class="stat-value text-h5 font-weight-bold">
                {{ filteredAgences.length }}
              </div>
            </div>
          </v-col>
          
          <v-col cols="6" md="3">
            <div class="stat-card">
              <div class="stat-label text-caption text-medium-emphasis">
                Dernière mise à jour
              </div>
              <div class="stat-value text-body-1">
                {{ formatDate(lastUpdate) }}
              </div>
            </div>
          </v-col>
          
          <v-col cols="6" md="3">
            <div class="stat-card">
              <div class="stat-label text-caption text-medium-emphasis">
                Statut
              </div>
              <div class="stat-value text-body-1" :class="apiStatusClass">
                {{ apiStatusText }}
              </div>
            </div>
          </v-col>
        </v-row>
      </v-card>

      <!-- Dialogue Ajout/Modification -->
      <v-dialog v-model="showDialog" max-width="600px" persistent>
        <v-card class="rounded-lg">
          <v-card-title class="d-flex justify-space-between align-center pa-4">
            <span class="text-h5">
              <v-icon :color="isEditing ? 'warning' : 'primary'" class="mr-2">
                {{ isEditing ? 'mdi-pencil' : 'mdi-plus' }}
              </v-icon>
              {{ isEditing ? 'Modifier l\'agence' : 'Nouvelle Agence' }}
            </span>
            <v-btn icon @click="closeDialog" size="small">
              <v-icon>mdi-close</v-icon>
            </v-btn>
          </v-card-title>
          
          <v-divider />
          
          <v-card-text class="pa-6">
            <v-form ref="agenceForm" v-model="formValid" @submit.prevent="saveAgence">
              <v-row dense>
                <!-- Code -->
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="formData.code"
                    label="Code Agence *"
                    placeholder="Ex: MG0010009"
                    variant="outlined"
                    :rules="codeRules"
                    :readonly="isEditing"
                    required
                    density="comfortable"
                  >
                    <template #prepend-inner>
                      <v-icon color="grey">mdi-identifier</v-icon>
                    </template>
                  </v-text-field>
                </v-col>
                
                <!-- Sous-code -->
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="formData.souscode"
                    label="Sous-Code *"
                    placeholder="Ex: A09"
                    variant="outlined"
                    :rules="souscodeRules"
                    required
                    density="comfortable"
                  >
                    <template #prepend-inner>
                      <v-icon color="grey">mdi-tag</v-icon>
                    </template>
                  </v-text-field>
                </v-col>
                
                <!-- Nom -->
                <v-col cols="12">
                  <v-text-field
                    v-model="formData.nom"
                    label="Nom de l'agence *"
                    placeholder="Ex: Andavamamba"
                    variant="outlined"
                    :rules="nomRules"
                    required
                    density="comfortable"
                  >
                    <template #prepend-inner>
                      <v-icon color="grey">mdi-bank</v-icon>
                    </template>
                  </v-text-field>
                </v-col>
                <!-- Dans le template, après le champ nom -->
                <v-col cols="12">
                  <v-select
                    v-model="formData.id_zone"
                    :items="zones"
                    item-title="nom"
                    item-value="id"
                    label="Zone"
                    placeholder="Sélectionnez une zone"
                    variant="outlined"
                    :loading="loadingZones"
                    clearable
                    density="comfortable"
                  >
                    <template #prepend-inner>
                      <v-icon color="grey">mdi-map-marker</v-icon>
                    </template>
                    <template #item="{ props, item }">
                      <v-list-item v-bind="props">
                        <template #prepend>
                          <v-icon color="primary">mdi-map-marker</v-icon>
                        </template>
                      </v-list-item>
                    </template>
                  </v-select>
                </v-col>
              </v-row>
            </v-form>
          </v-card-text>
          
          <v-divider />
          
          <v-card-actions class="pa-4">
            <v-spacer />
            <v-btn
              variant="text"
              @click="closeDialog"
              :disabled="saving"
            >
              Annuler
            </v-btn>
            <v-btn
              color="primary"
              @click="saveAgence"
              :loading="saving"
              :disabled="!formValid"
              prepend-icon="mdi-content-save"
            >
              {{ isEditing ? 'Mettre à jour' : 'Créer' }}
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Dialogue de confirmation suppression -->
      <v-dialog v-model="showDeleteDialog" max-width="500px" persistent>
        <v-card class="rounded-lg">
          <v-card-title class="text-h6 pa-4">
            <v-icon color="error" class="mr-2">mdi-alert-circle</v-icon>
            Confirmer la suppression
          </v-card-title>
          
          <v-card-text class="pa-4">
            <p>Êtes-vous sûr de vouloir supprimer l'agence <strong>{{ agenceToDelete?.nom }}</strong> ?</p>
            <p class="text-caption text-medium-emphasis mt-2">
              Code: {{ agenceToDelete?.code }} | Sous-Code: {{ agenceToDelete?.souscode }}
            </p>
            <v-alert v-if="deleteError" type="error" class="mt-3">
              {{ deleteError }}
            </v-alert>
          </v-card-text>
          
          <v-divider />
          
          <v-card-actions class="pa-4">
            <v-spacer />
            <v-btn
              variant="text"
              @click="showDeleteDialog = false"
              :disabled="deleting"
            >
              Annuler
            </v-btn>
            <v-btn
              color="error"
              @click="deleteAgence"
              :loading="deleting"
              prepend-icon="mdi-delete"
            >
              Supprimer définitivement
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Snackbar pour notifications -->
      <v-snackbar v-model="showSnackbar" :color="snackbarColor" timeout="3000">
        <div class="d-flex align-center">
          <v-icon class="mr-2">
            {{ snackbarIcon }}
          </v-icon>
          {{ snackbarMessage }}
        </div>
        
        <template #actions>
          <v-btn icon @click="showSnackbar = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </template>
      </v-snackbar>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, inject } from 'vue'
import TableauAgence from '@/components/agence/TableauAgence.vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()

const api = inject("api")

const agences = ref([])
const filteredAgences = ref([])
const loading = ref(false)
const searchTerm = ref('')
const itemsPerPage = ref(10)
const lastUpdate = ref(new Date())

const showDialog = ref(false)
const showDeleteDialog = ref(false)
const isEditing = ref(false)
const saving = ref(false)
const deleting = ref(false)
const formValid = ref(false)
const agenceForm = ref(null)
const agenceToDelete = ref(null)
const deleteError = ref('')

const formData = ref({
  code: '',
  souscode: '',
  nom: ''
})

const showSnackbar = ref(false)
const snackbarMessage = ref('')
const snackbarColor = ref('success')
const snackbarIcon = ref('mdi-check-circle')

const codeRules = [
  v => !!v || 'Le code est requis',
  v => (v && v.length >= 5) || 'Minimum 5 caractères',
  v => (v && v.length <= 20) || 'Maximum 20 caractères',
  v => /^MG\d+$/.test(v) || 'Doit commencer par MG suivi de chiffres'
]

const souscodeRules = [
  v => !!v || 'Le sous-code est requis',
  v => (v && v.length >= 2) || 'Minimum 2 caractères',
  v => (v && v.length <= 10) || 'Maximum 10 caractères',
  v => /^[A-Z]\d+$/.test(v) || 'Format: Lettre majuscule + chiffres (ex: A09)'
]

const nomRules = [
  v => !!v || 'Le nom est requis',
  v => (v && v.length >= 2) || 'Minimum 2 caractères',
  v => (v && v.length <= 100) || 'Maximum 100 caractères'
]

const apiStatusClass = computed(() => {
  return agences.value.length > 0 ? 'text-success' : 'text-warning'
})

const apiStatusText = computed(() => {
  return agences.value.length > 0 ? 'Connecté' : 'En attente...'
})

const loadAgences = async () => {
  loading.value = true
  try {
    const response = await axios.get(`${api}/api/agences/`)
    
    if (response.data.response?.success) {
      agences.value = response.data.response.data
      filteredAgences.value = [...agences.value]
      lastUpdate.value = new Date()
      
      showNotification('Agences chargées avec succès', 'success')
    } else {
      showNotification('Erreur lors du chargement des agences', 'error')
    }
  } catch (error) {
    console.error('Erreur chargement agences:', error)
    showNotification('Impossible de charger les agences', 'error')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  if (!searchTerm.value) {
    filteredAgences.value = [...agences.value]
    return
  }
  
  const term = searchTerm.value.toLowerCase()
  filteredAgences.value = agences.value.filter(agence => 
    agence.code.toLowerCase().includes(term) ||
    agence.souscode.toLowerCase().includes(term) ||
    agence.nom.toLowerCase().includes(term)
  )
}

const refreshAgences = () => {
  loadAgences()
}

const openAddDialog = () => {
  resetForm()
  isEditing.value = false
  showDialog.value = true
}

const openEditDialog = (agence) => {
  formData.value = {
    code: agence.code,
    souscode: agence.souscode,
    nom: agence.nom
  }
  isEditing.value = true
  showDialog.value = true
}

const closeDialog = () => {
  showDialog.value = false
  resetForm()
  if (agenceForm.value) {
    agenceForm.value.resetValidation()
  }
}

const resetForm = () => {
  formData.value = {
    code: '',
    souscode: '',
    nom: ''
  }
}

// Ajouter dans les data
const zones = ref([])
const loadingZones = ref(false)

// Méthode pour charger les zones
const loadZones = async () => {
  loadingZones.value = true
  try {
    const response = await axios.get(`${api}/api/zones`)
    if (response.data.response?.success) {
      zones.value = response.data.response.data
    }
  } catch (error) {
    console.error('Erreur chargement zones:', error)
  } finally {
    loadingZones.value = false
  }
}

const saveAgence = async () => {
  if (!formValid.value) return
  
  saving.value = true
  
  try {
    if (isEditing.value) {
      const response = await axios.put(
        `${api}/api/agences/${formData.value.code}`,
        {
          souscode: formData.value.souscode,
          nom: formData.value.nom
        }
      )
      
      if (response.data.response?.success) {
        const index = agences.value.findIndex(a => a.code === formData.value.code)
        if (index !== -1) {
          agences.value[index] = {
            ...agences.value[index],
            souscode: formData.value.souscode,
            nom: formData.value.nom
          }
          filteredAgences.value = [...agences.value]
        }
        
        deleteAgencesCache()


        showNotification('Agence mise à jour avec succès', 'success')
        closeDialog()
      }
    } else {
      // Création
      const response = await axios.post(
        `${api}/api/agences/create_agence`,
        formData.value
      )
      
      if (response.data.response?.success) {
        // Ajouter à la liste
        agences.value.push({
          id: response.data.response.id,
          code: formData.value.code,
          souscode: formData.value.souscode,
          nom: formData.value.nom,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        })
        filteredAgences.value = [...agences.value]
        
        
        deleteAgencesCache()


        showNotification('Agence créée avec succès', 'success')
        closeDialog()
      }
    }
  } catch (error) {
    console.error('Erreur sauvegarde agence:', error)
    const message = error.response?.data?.detail || 'Erreur lors de la sauvegarde'
    showNotification(message, 'error')
  } finally {
    saving.value = false
  }
}

const deleteAgencesCache = () => {
  try {
    localStorage.removeItem('agences_cache')
    
    const cacheKeys = Object.keys(localStorage)
    cacheKeys.forEach(key => {
      if (key.includes('agence') || key.includes('agences')) {
        localStorage.removeItem(key)
        console.log(`🗑️ Cache supprimé: ${key}`)
      }
    })
    
    window.dispatchEvent(new CustomEvent('agences-updated'))
    
    console.log('✅ Cache des agences supprimé avec succès')
  } catch (error) {
    console.error('❌ Erreur lors de la suppression du cache:', error)
  }
}

const confirmDelete = (agence) => {
  agenceToDelete.value = agence
  deleteError.value = ''
  showDeleteDialog.value = true
}

const deleteAgence = async () => {
  if (!agenceToDelete.value) return
  
  deleting.value = true
  
  try {
    const response = await axios.delete(
      `${api}/api/delete_agence/${agenceToDelete.value.code}`
    )
    
    if (response.data.response?.success) {
      // Supprimer de la liste
      const index = agences.value.findIndex(a => a.code === agenceToDelete.value.code)
      if (index !== -1) {
        agences.value.splice(index, 1)
        filteredAgences.value = [...agences.value]
      }
      
      showNotification('Agence supprimée avec succès', 'success')
      showDeleteDialog.value = false
      agenceToDelete.value = null
    }
  } catch (error) {
    console.error('Erreur suppression agence:', error)
    deleteError.value = error.response?.data?.detail || 'Erreur lors de la suppression'
  } finally {
    deleting.value = false
  }
}

const showNotification = (message, type = 'success') => {
  snackbarMessage.value = message
  snackbarColor.value = type
  snackbarIcon.value = type === 'success' ? 'mdi-check-circle' : 'mdi-alert-circle'
  showSnackbar.value = true
}

const formatDate = (date) => {
  return new Date(date).toLocaleString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Initialisation
onMounted(() => {
  loadAgences()
  loadZones()
})
</script>

<style scoped>
.full-container {
  max-height: 90vh;
  overflow-y: auto;
  padding-bottom: 20px;
  padding: 0 10px; 
}

.full-card {
  min-height: calc(100vh - 32px);
}

.navigation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.header-title {
  flex: 1;
  min-width: 300px;
}

.navigation-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.stat-card {
  padding: 12px;
  border-radius: 8px;
  background-color: rgba(0, 0, 0, 0.02);
}

.stat-label {
  margin-bottom: 4px;
}

.stat-value {
  color: #1976d2;
}

.fade-in {
  animation: fadeIn 0.5s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.encours-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 16px;
}

.encours-table th {
  background-color: #f8f9fa;
  padding: 12px;
  text-align: left;
  font-weight: 600;
  border-bottom: 2px solid #dee2e6;
}

.encours-table td {
  padding: 12px;
  border-bottom: 1px solid #e9ecef;
}

.encours-table tr:hover {
  background-color: #f8f9fa;
}
</style>