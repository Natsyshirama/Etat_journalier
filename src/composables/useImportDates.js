import { ref } from 'vue'

export function useImportDates() {
  const api = ref('')
  const loading = ref(false)
  const error = ref('')

  const t24Imports = ref([])
  const powerCardImports = ref([])

  const setApiUrl = (apiUrl) => {
    api.value = apiUrl
  }

  const fetchImportDates = async (endpoint) => {
    const response = await fetch(`${api.value}${endpoint}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`
      }
    })

    const data = await response.json()

    if (!response.ok || data.status !== 'success') {
      throw new Error(data.detail || 'Erreur lors du chargement')
    }

    return data.data || []
  }

  const loadImportDates = async () => {
    loading.value = true
    error.value = ''

    try {
      const [t24Data, powerCardData] = await Promise.all([
        fetchImportDates('/api/t24/import-dates'),
        fetchImportDates('/api/powercard/import-dates')
      ])

      t24Imports.value = t24Data
      powerCardImports.value = powerCardData
    } catch (exception) {
      console.error('Erreur import dates:', exception)
      error.value = exception.message
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    t24Imports,
    powerCardImports,
    setApiUrl,
    loadImportDates
  }
}