import { ref } from 'vue'

export function useInsertProcessing() {
  const api = ref('')
  const loading = ref(false)
  const startDate = ref('')
  const endDate = ref('')
  const result = ref(null)
  const message = ref('')
  const messageType = ref('') // 'success'|'error'|'info'

  const setApiUrl = (url) => { api.value = url }

  const normalizeForApi = (d) => {
    if (!d) return ''
    return d.replace(/-/g, '') // YYYY-MM-DD -> YYYYMMDD
  }

  const insertProcessingDates = async () => {
    message.value = ''
    messageType.value = ''
    result.value = null

    if (!startDate.value) {
      messageType.value = 'error'
      message.value = 'Date de début requise'
      return false
    }

    const s = normalizeForApi(startDate.value)
    const e = endDate.value ? normalizeForApi(endDate.value) : s

    loading.value = true
    try {
      const url = `${api.value}/api/t24/insert_processing_date_to_power_many?start_date=${s}&end_date=${e}`
      const resp = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      })
      const data = await resp.json()
      if (resp.ok && data.status === 'success') {
        // backend returns data.data which is the controller result
        result.value = data.data
        messageType.value = 'success'
        message.value = 'Traitement terminé'
        return true
      } else {
        messageType.value = 'error'
        message.value = data.detail || data.data?.error || 'Erreur serveur'
        return false
      }
    } catch (err) {
      console.error('insertProcessingDates error', err)
      messageType.value = 'error'
      message.value = err.message || 'Erreur réseau'
      return false
    } finally {
      loading.value = false
    }
  }

  const clear = () => {
    startDate.value = ''
    endDate.value = ''
    result.value = null
    message.value = ''
    messageType.value = ''
  }

  return {
    api,
    setApiUrl,
    loading,
    startDate,
    endDate,
    result,
    message,
    messageType,
    insertProcessingDates,
    clear
  }
}