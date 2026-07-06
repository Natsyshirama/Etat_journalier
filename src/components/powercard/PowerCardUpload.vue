<template>
  <div class="power-card-upload">
    <!-- Message Alert -->
    <v-alert
      v-if="message"
      :type="messageType"
      closable
      @click:close="clearMessage"
      class="mb-4"
    >
      {{ message }}
    </v-alert>

    <!-- Formulaire d'import -->
    <v-card class="mb-4">
      <v-card-title>Import Power Card</v-card-title>
      <v-card-text>
        <v-container>
          <!-- Date Selection -->
          <v-row>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="importDate"
                type="date"
                label="Date d'import"
                :disabled="loading"
                outlined
                dense
              />
            </v-col>
          </v-row>

          <!-- File Selection -->
          <v-row>
            <v-col cols="12">
              <v-file-input
                v-model="selectedFile"
                accept=".csv"
                label="Sélectionner un fichier CSV"
                hint="Format: powercard_YYYYMMDD.csv"
                :disabled="loading"
                outlined
                dense
                @update:modelValue="handleFileSelect"
              />
            </v-col>
          </v-row>

          <!-- Upload Progress -->
          <v-row v-if="loading">
            <v-col cols="12">
              <v-progress-linear
                :value="uploadProgress"
                striped
              />
              <p class="text-center text-caption">
                {{ uploadProgress }}% - {{ loading ? 'Téléchargement en cours...' : '' }}
              </p>
            </v-col>
          </v-row>

          <!-- Import Stats Result -->
          <v-row v-if="importStats">
            <v-col cols="12">
              <v-card :class="importStats.error_count > 0 ? 'bg-orange-50' : 'bg-green-50'">
                <v-card-text>
                  <p><strong>Fichier:</strong> {{ importStats.filename }}</p>
                  <p><strong>Lignes importées:</strong> {{ importStats.rows_inserted }}</p>
                  <p v-if="importStats.error_count > 0" class="text-error">
                    <strong>❌ Erreurs:</strong> {{ importStats.error_count }}
                  </p>
                  <p v-else class="text-success">
                    <strong>✅ Succès!</strong> Tous les enregistrements ont été importés
                  </p>

                  <!-- List of Errors -->
                  <v-expansion-panels v-if="importStats.error_count > 0" class="mt-4">
                    <v-expansion-panel>
                      <template #title>
                        <v-icon color="error" class="mr-2">mdi-alert-circle</v-icon>
                        Détails des {{ importStats.error_count }} erreurs
                      </template>
                      <template #text>
                        <div class="error-list">
                          <div v-for="(msg, index) in importStats.messages" :key="index" class="error-item">
                            <v-chip v-if="msg.includes('Import réussi')" color="green" text-color="white" size="small" class="mb-2">
                              ✅ {{ msg }}
                            </v-chip>
                            <v-chip v-else color="red" text-color="white" size="small" class="mb-2">
                              ❌ {{ msg }}
                            </v-chip>
                          </div>
                        </div>
                      </template>
                    </v-expansion-panel>
                  </v-expansion-panels>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>

      <!-- Actions -->
      <v-card-actions>
        <v-spacer />
        <v-btn
          color="primary"
          :loading="loading"
          :disabled="!selectedFile || !importDate || loading"
          @click="handleUpload"
        >
          <v-icon start>mdi-upload</v-icon>
          Importer
        </v-btn>
        <v-btn
          variant="outlined"
          @click="resetForm"
        >
          Réinitialiser
        </v-btn>
      </v-card-actions>
    </v-card>

    <!-- Fichier d'aide -->
    <v-card class="info-card">
      <v-card-title class="text-subtitle-2">
        <v-icon>mdi-information</v-icon>
        Instructions
      </v-card-title>
      <v-card-text class="text-caption">
        <ul>
          <li>Le fichier doit être au format CSV</li>
          <li>Le nom doit suivre le format: <code>powercard_YYYYMMDD.csv</code></li>
          <li>Exemple: <code>powercard_20260705.csv</code></li>
          <li>Les colonnes attendues: External stan, Reference, Source, Destination, Message, Processing code, Action, PAN, Local time, Internal time, Transaction amount, Terminal no., Acceptor point, Authorization reference, Current table indicator, Source account number</li>
        </ul>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import { ref, inject, onMounted } from 'vue'
import { usePowerCardImport } from '../../composables/usePowerCardImport'

const api = inject('api')
const {
  importDate,
  loading,
  uploadProgress,
  message,
  messageType,
  importStats,
  selectFile,
  setImportDate,
  setApiUrl,
  uploadFile,
  clearMessage
} = usePowerCardImport()

const selectedFile = ref(null)

const handleFileSelect = () => {
  if (selectedFile.value) {
    const fileToUpload = Array.isArray(selectedFile.value) ? selectedFile.value[0] : selectedFile.value
    if (fileToUpload) {
      selectFile(fileToUpload)
    }
  }
}

const handleUpload = async () => {
  // Vérifier que les deux sont bien remplis avant d'uploader
  if (!selectedFile.value) {
    messageType.value = 'error'
    message.value = 'Veuillez sélectionner un fichier'
    return
  }
  
  if (!importDate.value) {
    messageType.value = 'error'
    message.value = 'Veuillez sélectionner une date'
    return
  }

  await uploadFile()
}

const resetForm = () => {
  selectedFile.value = null
  importDate.value = ''
  importStats.value = null
  clearMessage()
}

onMounted(() => {
  setApiUrl(api)
})
</script>

<style scoped>
.power-card-upload {
  padding: 16px;
}

.info-card {
  background-color: #f5f5f5;
}

code {
  background-color: #e0e0e0;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
}

.error-list {
  max-height: 400px;
  overflow-y: auto;
}

.error-item {
  margin-bottom: 8px;
}

.bg-green-50 {
  background-color: #e8f5e9;
}

.bg-orange-50 {
  background-color: #fff3e0;
}

.text-success {
  color: #4caf50;
}
</style>
