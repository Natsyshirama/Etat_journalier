// composables/format_money.js
export function useMoneyFormat() {
  
  // Format anglais (en-US) avec décimales
  const formatUSD = (value, decimals = 2) => {
    if (value === null || value === undefined) return ''
    
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(value)
  }

  // Format anglais sans décimales (pour nombres entiers)
  const formatUSDInteger = (value) => {
    if (value === null || value === undefined) return ''
    
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value)
  }

  // Format avec symbole dollar
  const formatUSDCurrency = (value, decimals = 2) => {
    if (value === null || value === undefined) return ''
    
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(value)
  }

  // Version plus flexible avec options
  const formatMoney = (value, options = {}) => {
    if (value === null || value === undefined) return ''
    
    const {
      locale = 'en-US',
      currency = 'USD',
      style = 'decimal',
      decimals = 2,
      useGrouping = true
    } = options

    return new Intl.NumberFormat(locale, {
      style,
      currency: style === 'currency' ? currency : undefined,
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
      useGrouping
    }).format(value)
  }

  return {
    formatUSD,
    formatUSDInteger,
    formatUSDCurrency,
    formatMoney
  }
}

// Export aussi en tant que fonction utilitaire simple si besoin
export const formatUSD = (value, decimals = 2) => {
  if (value === null || value === undefined) return ''
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  }).format(value)
}