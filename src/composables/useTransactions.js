import { ref } from 'vue'

export function useTransactions() {
  const api = ref('')
  const loading = ref(false)
  const startDate = ref('')
  const endDate = ref('')
  const message = ref('')
  const messageType = ref('')
  const transactions = ref([])
  const count = ref(0)
  const startDateTime = ref(null)
  const endDateTime = ref(null)
  const lastSaisieLe = ref(null)


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
    if (!startDate.value) {
      messageType.value = 'error'
      message.value = 'Veuillez sélectionner une date de début'
      return false
    }

    // Validation: vérifier que les dates ne sont pas dans le futur
    const today = new Date()
    today.setHours(0, 0, 0, 0)

    const normalizedStart = normalizeDate(startDate.value)
    const startDateObj = new Date(normalizedStart)

    if (startDateObj > today) {
      messageType.value = 'error'
      message.value = 'La date de début ne peut pas être dans le futur'
      return false
    }

    if (endDate.value) {
      const normalizedEnd = normalizeDate(endDate.value)
      const endDateObj = new Date(normalizedEnd)

      if (endDateObj > today) {
        messageType.value = 'error'
        message.value = 'La date de fin ne peut pas être dans le futur'
        return false
      }
    }

    loading.value = true
    message.value = ''
    messageType.value = ''

    try {
      let url = `${api.value}/api/t24/transactions?start_date=${normalizedStart}`

      if (endDate.value) {
        const normalizedEnd = normalizeDate(endDate.value)
        url += `&end_date=${normalizedEnd}`
      }

      url += `&limit=${limit}&offset=${offset}`

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      })

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



  // get last saisie le
const fetchLastSaisieLe = async () => {
  try {
    const response = await fetch(`${api.value}/api/t24/last_saisie_le`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    })
    const data = await response.json()

    if (response.ok && data.status === 'success') {
      lastSaisieLe.value = data.data?.formatted ?? null
      return lastSaisieLe.value
    }

    lastSaisieLe.value = null
    return null
  } catch (error) {
    console.error('Erreur fetchLastSaisieLe:', error)
    lastSaisieLe.value = null
    return null
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
    startDate,
    endDate,
    message,
    messageType,
    transactions,
    count,
    startDateTime,
    endDateTime,
    setApiUrl,
    fetchTransactions,
    fetchLastSaisieLe,
    lastSaisieLe,
    clearMessage
  }
}