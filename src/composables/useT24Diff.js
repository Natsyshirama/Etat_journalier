import { ref } from 'vue'

export function useT24Diff() {
  const api = ref('')
  const loading = ref(false)
  const processingDate = ref('')
  const startDate = ref('')
  const endDate = ref('')
  const mode = ref('single')
  const message = ref('')
  const messageType = ref('')
  const diffs = ref([])
  const count = ref(0)

  const showReferenceDialog = ref(false)
  const referenceDetail = ref('')
  const referenceData = ref(null)
  const referenceSource = ref('')

  const startDateTime = ref(null)
const endDateTime = ref(null)

  const setApiUrl = (apiUrl) => {
    api.value = apiUrl
  }

  const clearMessage = () => {
    message.value = ''
    messageType.value = ''
    startDateTime.value = null
    endDateTime.value = null
  }

  const isFutureDate = (date) => {
  if (!date) return false

  const selected = new Date(date)
  selected.setHours(0, 0, 0, 0)

  const today = new Date()
  today.setHours(0, 0, 0, 0)

  return selected > today
}

  const fetchDiffs = async () => {
    clearMessage()

    if (mode.value === 'single') {
     
      if (!processingDate.value) {
        messageType.value = 'error'
        message.value = 'Veuillez sélectionner une date de traitement'
        return false
      }

      if (isFutureDate(processingDate.value)) {
        messageType.value = 'error'
        message.value = 'La date de traitement ne peut pas être dans le futur'
        return false
      }

    } else {
      if (!startDate.value || !endDate.value) {
        messageType.value = 'error'
        message.value = 'Veuillez sélectionner une date de début et une date de fin'
        return false
      }

      if (isFutureDate(startDate.value)) {
        messageType.value = 'error'
        message.value = 'La date de début ne peut pas être dans le futur'
        return false
      }

      if (isFutureDate(endDate.value)) {
        messageType.value = 'error'
        message.value = 'La date de fin ne peut pas être dans le futur'
        return false
      }
    }

    loading.value = true
    try {
      let url = ''
      if (mode.value === 'single') {
        url = `${api.value}/api/t24/diff?processing_date=${processingDate.value}`
      } else {
        const start = startDate.value.replace(/-/g, '')
        const end = endDate.value.replace(/-/g, '')
        url = `${api.value}/api/t24/diff_many?start_date=${start}&end_date=${end}`
      }

      const response = await fetch(url, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        }
      })
      const data = await response.json()

      if (response.ok && data.status === 'success') {
        const payload = data.data ?? data

        if (mode.value === 'single') {
          startDateTime.value = payload.start_datetime ?? null
          endDateTime.value = payload.end_datetime ?? null
          diffs.value = (payload.data || []).map((item) => ({
            ...item,
            t24_matches_count: item.t24_matches?.length || 0,
            processing_date: item.processing_date || processingDate.value
          }))
          count.value = payload.count || diffs.value.length
          messageType.value = 'success'
          message.value = `✅ ${count.value} différence(s) trouvée(s)`
          return true
        }

        const periods = payload.periods || []
        if (periods.length === 0) {
          diffs.value = []
          count.value = 0
          messageType.value = 'success'
          message.value = '✅ Aucune période T24 trouvée pour cet intervalle'
          return true
        }

        diffs.value = periods.flatMap((period) => {
          const diffItems = period.diff?.data || []
          return diffItems.map((item) => ({
            ...item,
            processing_date: period.processing_date,
            period_start_datetime: period.t24_period?.start_datetime,
            period_end_datetime: period.t24_period?.end_datetime,
            t24_matches_count: item.t24_matches?.length || 0
          }))
        })

        count.value = diffs.value.length
        startDateTime.value = null
        endDateTime.value = null
        messageType.value = 'success'
        message.value = `✅ ${count.value} différence(s) trouvée(s) dans ${periods.length} période(s)`
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
  
const openT24Reference = async (reference) => {
  if (!reference) return
  loading.value = true
  try {
    const response = await fetch(
      `${api.value}/api/t24/transactions/by_reference?reference=${encodeURIComponent(reference)}`,
      {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        }
      }
    )
    const data = await response.json()

    if (response.ok && data.status === 'success') {
      referenceDetail.value = reference
      referenceData.value = Array.isArray(data.data) ? data.data[0] ?? null : data.data
      referenceSource.value = 'T24'
      showReferenceDialog.value = true
    } else {
      messageType.value = 'error'
      message.value = `Erreur: ${data.detail || data.data?.error || 'Impossible de charger le détail'}`
    }
  } catch (err) {
    messageType.value = 'error'
    message.value = `Erreur: ${err.message}`
  } finally {
    loading.value = false
  }
}


  const openPowerCardReference = async (reference) => {
    if (!reference) return
    loading.value = true
    try {
      const response = await fetch(
        `${api.value}/api/powercard/transactions/by_reference?reference=${encodeURIComponent(reference)}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`
          }
        }
      )
      const data = await response.json()

      if (response.ok && data.status === 'success') {
        referenceDetail.value = reference
        referenceData.value = Array.isArray(data.data) ? data.data[0] ?? null : data.data
        referenceSource.value = 'PowerCard'
        showReferenceDialog.value = true
      } else {
        messageType.value = 'error'
        message.value = `Erreur: ${data.detail || data.data?.error || 'Impossible de charger le détail'}`
      }
    } catch (err) {
      messageType.value = 'error'
      message.value = `Erreur: ${err.message}`
    } finally {
      loading.value = false
    }
  }

  return {
    api,
    loading,
    processingDate,
    startDate,
    endDate,
    mode,
    message,
    messageType,
    diffs,
    count,
    showReferenceDialog,
    referenceDetail,
    referenceData,
    referenceSource,
    setApiUrl,
    fetchDiffs,
    clearMessage,
    openT24Reference,
    openPowerCardReference,
    startDateTime,
    endDateTime
  }
}
