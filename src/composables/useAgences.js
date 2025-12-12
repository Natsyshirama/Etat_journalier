// composables/useAgences.js
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

export function useAgences(api) {
  const agencesList = ref([])
  const loading = ref(false)
  const error = ref(null)
  const initialized = ref(false)

  const defaultAgences = [
    { code: "MG0010009", nom: "Andavamamba", souscode: "A09" },
    { code: "MG0010004", nom: "Analamahitsy", souscode: "A04" },
    { code: "MG0010024", nom: "Andravoahangy", souscode: "A24" },
    { code: "MG0010052", nom: "Imerinafovoany", souscode: "A52" },
    { code: "MG0010011", nom: "Andoharanofotsy", souscode: "A11" },
    { code: "MG0010012", nom: "Anosizato", souscode: "A12" },
    { code: "MG0010010", nom: "67 Hectares", souscode: "A10" },
    { code: "MG0011001", nom: "Antanimena", souscode: "B01" },
    { code: "MG0010003", nom: "Antsahabe", souscode: "A03" },
    { code: "MG0010022", nom: "Behoririka", souscode: "A22" },
    { code: "MG0010053", nom: "Ivandry", souscode: "A53" },
    { code: "MG0010013", nom: "Mahamasina", souscode: "A13" },
    { code: "MG0010041", nom: "Soixante Sept Hectares", souscode: "A41" },
    { code: "MG0010023", nom: "Tanjombato", souscode: "A23" }
  ]

  const loadAgences = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await axios.get(`${api}/api/agences/`, {
        headers: { 
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      })

      if (response.data.response?.success) {
        agencesList.value = response.data.response.data.map(ag => ({
          code: ag.code,
          nom: ag.nom,
          souscode: ag.souscode || ""
        }))
        
        // Sauvegarder dans le cache local
        localStorage.setItem('agences_cache', JSON.stringify({
          data: agencesList.value,
          timestamp: new Date().getTime()
        }))
      } else {
        throw new Error('Structure de réponse invalide')
      }
    } catch (err) {
      console.error('Erreur chargement agences:', err)
      error.value = err.message
      
      // Essayer de charger depuis le cache
      const cached = loadFromCache()
      if (!cached) {
        // Sinon utiliser les valeurs par défaut
        agencesList.value = [...defaultAgences]
      }
    } finally {
      loading.value = false
      initialized.value = true
    }
  }

  // Charger depuis le cache local
  const loadFromCache = () => {
    try {
      const cache = localStorage.getItem('agences_cache')
      if (cache) {
        const { data, timestamp } = JSON.parse(cache)
        const now = new Date().getTime()
        const CACHE_DURATION = 30 * 60 * 1000 // 30 minutes
        
        if (now - timestamp < CACHE_DURATION) {
          agencesList.value = data
          return true
        }
      }
    } catch (e) {
      console.warn('Erreur lecture cache agences:', e)
    }
    return false
  }

  // Obtenir une agence par son code
  const getAgenceByCode = (code) => {
    return agencesList.value.find(ag => ag.code === code)
  }

  // Obtenir le nom d'une agence
  const getAgenceName = (code) => {
    const agence = getAgenceByCode(code)
    return agence ? agence.nom : `Agence ${code}`
  }

  // Obtenir le sous-code d'une agence
  const getAgenceSouscode = (code) => {
    const agence = getAgenceByCode(code)
    return agence ? (agence.souscode || code) : code
  }

  // Vérifier si une agence existe
  const agenceExists = (code) => {
    return agencesList.value.some(ag => ag.code === code)
  }

  // Computed properties
  const agencesCount = computed(() => agencesList.value.length)
  const agencesCodes = computed(() => agencesList.value.map(ag => ag.code))

  // Initialiser
  const initialize = () => {
    if (!initialized.value) {
      const cached = loadFromCache()
      if (!cached) {
        loadAgences()
      } else {
        initialized.value = true
      }
    }
  }

  // Appeler initialize au démarrage
  onMounted(() => {
    initialize()
  })

  return {
    agencesList,
    loading,
    error,
    initialized,
    loadAgences,
    getAgenceByCode,
    getAgenceName,
    getAgenceSouscode,
    agenceExists,
    agencesCount,
    agencesCodes
  }
}