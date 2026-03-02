// composables/format_date.js

/**
 * Composable pour le formatage des dates
 * Supporte les formats: yyyymmdd, yyyy/mm/dd, yyyy-mm-dd, etc.
 */
export function useDateFormat() {
  
  /**
   * Formate une date du format AAAAMMJJ vers JJ/MM/AAAA
   * Exemple: "20250306" → "06/03/2025"
   */
  const formatDateToFrench = (dateStr, separator = '/') => {
    if (!dateStr || typeof dateStr !== 'string') return dateStr
    
    // Nettoie la chaîne (enlève les séparateurs existants)
    const cleanDate = dateStr.replace(/[\/\-]/g, '')
    
    // Vérifie si c'est un format AAAAMMJJ valide (8 chiffres)
    if (!/^\d{8}$/.test(cleanDate)) return dateStr
    
    const year = cleanDate.substring(0, 4)
    const month = cleanDate.substring(4, 6)
    const day = cleanDate.substring(6, 8)
    
    return `${day}${separator}${month}${separator}${year}`
  }

  /**
   * Formate une date du format AAAAMMJJ vers MM/DD/AAAA (format US)
   * Exemple: "20250306" → "03/06/2025"
   */
  const formatDateToUS = (dateStr, separator = '/') => {
    if (!dateStr || typeof dateStr !== 'string') return dateStr
    
    const cleanDate = dateStr.replace(/[\/\-]/g, '')
    if (!/^\d{8}$/.test(cleanDate)) return dateStr
    
    const year = cleanDate.substring(0, 4)
    const month = cleanDate.substring(4, 6)
    const day = cleanDate.substring(6, 8)
    
    return `${month}${separator}${day}${separator}${year}`
  }

  /**
   * Formate une date avec option de personnalisation
   * Exemple: formatDate("20250306", { format: 'french', separator: '-' }) → "06-03-2025"
   */
  const formatDate = (dateStr, options = {}) => {
    const {
      format = 'french', // 'french', 'us', 'iso'
      separator = '/',
      includeTime = false,
      timeStr = null
    } = options

    if (!dateStr || typeof dateStr !== 'string') return dateStr
    
    const cleanDate = dateStr.replace(/[\/\-]/g, '')
    if (!/^\d{8}$/.test(cleanDate)) return dateStr
    
    const year = cleanDate.substring(0, 4)
    const month = cleanDate.substring(4, 6)
    const day = cleanDate.substring(6, 8)
    
    let formattedDate = ''
    
    switch (format) {
      case 'french':
        formattedDate = `${day}${separator}${month}${separator}${year}`
        break
      case 'us':
        formattedDate = `${month}${separator}${day}${separator}${year}`
        break
      case 'iso':
        formattedDate = `${year}-${month}-${day}`
        break
      default:
        formattedDate = `${day}${separator}${month}${separator}${year}`
    }
    
    if (includeTime && timeStr) {
      formattedDate += ` ${timeStr}`
    }
    
    return formattedDate
  }

  /**
   * Détecte automatiquement les colonnes de date dans les données
   * Retourne un tableau des noms de colonnes qui semblent contenir des dates
   */
  const detectDateColumns = (data, sample = null) => {
    if (!data || data.length === 0) return []
    
    const sampleItem = sample || data[0]
    const dateColumns = []
    
    Object.keys(sampleItem).forEach(key => {
      const value = sampleItem[key]
      // Vérifie si la valeur ressemble à une date AAAAMMJJ
      if (typeof value === 'string' && /^\d{8}$/.test(value.replace(/[\/\-]/g, ''))) {
        dateColumns.push(key)
      }
    })
    
    return dateColumns
  }

  /**
   * Crée une configuration d'en-têtes avec formatage automatique des dates
   */
  const createDateHeaders = (columns, dateColumns, options = {}) => {
    return columns.map(col => ({
      title: col,
      key: col,
      align: dateColumns.includes(col) ? 'center' : 'start',
      ...options
    }))
  }

  return {
    formatDateToFrench,
    formatDateToUS,
    formatDate,
    detectDateColumns,
    createDateHeaders
  }
}

// Export des fonctions individuelles pour utilisation directe
export const formatDateToFrench = (dateStr, separator = '/') => {
  if (!dateStr || typeof dateStr !== 'string') return dateStr
  const cleanDate = dateStr.replace(/[\/\-]/g, '')
  if (!/^\d{8}$/.test(cleanDate)) return dateStr
  const year = cleanDate.substring(0, 4)
  const month = cleanDate.substring(4, 6)
  const day = cleanDate.substring(6, 8)
  return `${day}${separator}${month}${separator}${year}`
}

export const formatDateToUS = (dateStr, separator = '/') => {
  if (!dateStr || typeof dateStr !== 'string') return dateStr
  const cleanDate = dateStr.replace(/[\/\-]/g, '')
  if (!/^\d{8}$/.test(cleanDate)) return dateStr
  const year = cleanDate.substring(0, 4)
  const month = cleanDate.substring(4, 6)
  const day = cleanDate.substring(6, 8)
  return `${month}${separator}${day}${separator}${year}`
}