import { ref } from 'vue'

export function useTransactions() {
  const api = ref('')
  const loading = ref(false)
  const importDate = ref('')
  const message = ref('')
  const messageType = ref('')
  const transactions = ref([])
  const count = ref(0)
  const startDateTime = ref(null)
  const endDateTime = ref(null)

  const setApiUrl = (apiUrl) => {
    api.value = apiUrl
  }

  const normalizeDate = (date) => {
    if (!date) return date
    const parts = date.split('/')
    if (parts.length === 3) {
      return `${parts[2]}-${parts[1].padStart(2, '0')}-${parts[0].padStart(2, '0')}`
    }
    return date
  }

  const fetchTransactions = async (limit = 100, offset = 0) => {
    if (!importDate.value) {
      messageType.value = 'error'
      message.value = 'Veuillez sélectionner une date'
      return false
    }

    loading.value = true
    message.value = ''
    messageType.value = ''

    try {
      const normalizedDate = normalizeDate(importDate.value)
      const response = await fetch(
        `${api.value}/api/t24/transactions?import_date=${normalizedDate}&limit=${limit}&offset=${offset}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      )

      const data = await response.json()

      if (response.ok && data.status === 'success') {
        transactions.value = data.data.data ?? data.data
        count.value = data.data.count ?? data.count ?? transactions.value.length
        startDateTime.value = data.data.start_datetime ?? data.start_datetime ?? null
        endDateTime.value = data.data.end_datetime ?? data.end_datetime ?? null
        messageType.value = 'success'
        message.value = `✅ ${count.value} transactions chargées`
        return true
      }

      messageType.value = 'error'
      message.value = `❌ ${data.detail || data.data?.error || 'Erreur lors de la récupération'}`
      return false
    } catch (error) {
      console.error('Erreur fetchTransactions:', error)
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
    startDateTime.value = null
    endDateTime.value = null
  }

  return {
    api,
    loading,
    importDate,
    message,
    messageType,
    transactions,
    count,
    startDateTime,
    endDateTime,
    setApiUrl,
    fetchTransactions,
    clearMessage
  }
}