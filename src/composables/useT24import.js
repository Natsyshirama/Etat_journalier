import { ref } from 'vue'

export function useT24CardImport() {
  const api = ref('')
  const loading = ref(false)
  const file = ref(null)
  const importDate = ref('')
  const uploadProgress = ref(0)
  const message = ref('')
  const messageType = ref('') // 'success', 'error', 'info'
  const importStats = ref(null)

  const setApiUrl = (apiUrl) => {
    api.value = apiUrl
  }

  const selectFile = (selectedFile) => {
    if (selectedFile) {
      // Vérifier que c'est un CSV
      if (!selectedFile.name.toLowerCase().endsWith('.csv')) {
        messageType.value = 'error'
        message.value = 'Veuillez sélectionner un fichier CSV'
        return false
      }

      // Vérifier le format du nom: t24_YYYYMMDD.csv
      const pattern = /^t24_\d{8}\.csv$/i
      if (!pattern.test(selectedFile.name)) {
        messageType.value = 'error'
        message.value = 'Format de nom invalide. Utilisez: t24_YYYYMMDD.csv'
        return false
      }

      file.value = selectedFile
      messageType.value = ''
      message.value = ''
      return true
    }
    return false
  }

  const setImportDate = (date) => {
    importDate.value = date
  }

  const uploadFile = async () => {
    if (!file.value || !importDate.value) {
      messageType.value = 'error'
      message.value = 'Veuillez sélectionner un fichier et une date'
      return false
    }

    loading.value = true
    uploadProgress.value = 0
    message.value = ''
    messageType.value = ''

    try {
      const formData = new FormData()
      formData.append('file', file.value)

      const response = await fetch(
        `${api.value}/api/t24/import?import_date=${importDate.value}`,
        {
          method: 'POST',
          body: formData,
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      )

      uploadProgress.value = 100

      const data = await response.json()

      if (response.ok && data.status === 'success') {
        messageType.value = 'success'
        message.value = `✅ ${data.data.messages[0]}`
        importStats.value = data.data
        
        // Réinitialiser le formulaire après succès
        file.value = null
        importDate.value = ''
        
        return true
      } else {
        messageType.value = 'error'
        message.value = `❌ ${data.data?.messages?.[0] || 'Erreur lors de l\'import'}`
        return false
      }
    } catch (error) {
      console.error('Erreur upload:', error)
      messageType.value = 'error'
      message.value = `❌ Erreur: ${error.message}`
      return false
    } finally {
      loading.value = false
    }
  }


  const clearMessage = () => {
    message.value = ''
    messageType.value = ''
  }

  return {
    file,
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
  }
}
