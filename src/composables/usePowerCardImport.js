import { ref } from 'vue'

export function usePowerCardImport() {
  const api = ref('')
  const loading = ref(false)
  const file = ref(null)
  const importDate = ref('')
  const uploadProgress = ref(0)
  const message = ref('')
  const messageType = ref('') // 'success', 'error', 'info'
  const importStats = ref(null)
  const lastLocalTime = ref(null)

  const setApiUrl = (apiUrl) => {
    api.value = apiUrl
  }

  
// nouvelle fonction à ajouter dans le composable
const fetchLastLocalTime = async () => {
  try {
    const response = await fetch(`${api.value}/api/powercard/last_local_time`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    })
    const data = await response.json()
    if (response.ok && data.status === 'success') {
      lastLocalTime.value = data.last_local_time
    } else {
      lastLocalTime.value = null
    }
  } catch (err) {
    console.error('fetchLastLocalTime error', err)
    lastLocalTime.value = null
  }
}
  const selectFile = (selectedFile) => {
    if (selectedFile) {
      // Vérifier que c'est un CSV
      if (!selectedFile.name.toLowerCase().endsWith('.csv')) {
        messageType.value = 'error'
        message.value = 'Veuillez sélectionner un fichier CSV'
        return false
      }

      // Vérifier le format du nom: powercard_YYYYMMDD.csv
      const pattern = /^powercard_\d{8}\.csv$/i
      if (!pattern.test(selectedFile.name)) {
        messageType.value = 'error'
        message.value = 'Format de nom invalide. Utilisez: powercard_YYYYMMDD.csv'
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
        `${api.value}/api/powercard/import?import_date=${importDate.value}`,
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

const fetchStats = async (date = null) => {
  try {
    const url = date 
      ? `${api.value}/api/powercard/stats?import_date=${date}`
      : `${api.value}/api/powercard/stats`

    const response = await fetch(url, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    })

    const data = await response.json()

    if (response.ok) {
      return data.data?.data ?? data.data
    } else {
      throw new Error(data.detail || 'Erreur lors de la récupération des stats')
    }
  } catch (error) {
    console.error('Erreur fetchStats:', error)
    return null
  }
}

  const normalizeDate = (date) => {
  if (!date) return date
  const parts = date.split('/')
  if (parts.length === 3) {
    return `${parts[2]}-${parts[1].padStart(2, '0')}-${parts[0].padStart(2, '0')}`
  }
  return date
}

  const fetchTransactions = async (date, limit = 100, offset = 0) => {
    try {
      const normalizedDate = normalizeDate(date)

      const response = await fetch(
        `${api.value}/api/powercard/transactions?import_date=${normalizedDate}&limit=${limit}&offset=${offset}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      )

      const data = await response.json()

      if (response.ok) {
        return data.data?.data ?? data.data
      } else {
        throw new Error(data.detail || 'Erreur lors de la récupération des transactions')
      }
    } catch (error) {
      console.error('Erreur fetchTransactions:', error)
      return []
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
    fetchStats,
    fetchTransactions,
    fetchLastLocalTime,   // <-- ajouter
    lastLocalTime,    
    clearMessage
  }
}
