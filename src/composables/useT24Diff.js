import { ref } from 'vue'

export function useT24Diff() {
  const api = ref('')
  const loading = ref(false)
  const processingDate = ref('')
  const message = ref('')
  const messageType = ref('')
  const diffs = ref([])
  const count = ref(0)

  const setApiUrl = (apiUrl) => {
    api.value = apiUrl
  }

  const clearMessage = () => {
    message.value = ''
    messageType.value = ''
  }

  const fetchDiffs = async () => {
    clearMessage()

    if (!processingDate.value) {
      messageType.value = 'error'
      message.value = 'Veuillez sélectionner une date de traitement'
      return false
    }

    loading.value = true
    try {
      const response = await fetch(
        `${api.value}/api/t24/diff?processing_date=${processingDate.value}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      )
      const data = await response.json()

      if (response.ok && data.status === 'success') {
        diffs.value = (data.data.data || []).map((item) => ({
          ...item,
          t24_matches_count: item.t24_matches?.length || 0,
        }))
        count.value = data.data.count || diffs.value.length
        messageType.value = 'success'
        message.value = `✅ ${count.value} différence(s) trouvée(s)`
        return true
      }

      messageType.value = 'error'
      message.value = `❌ ${data.detail || data.data?.error || 'Erreur lors de la recherche'}`
      return false
    } catch (error) {
      console.error('Erreur fetchDiffs:', error)
      messageType.value = 'error'
      message.value = `❌ Erreur: ${error.message}`
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    api,
    loading,
    processingDate,
    message,
    messageType,
    diffs,
    count,
    setApiUrl,
    fetchDiffs,
    clearMessage
  }
}
