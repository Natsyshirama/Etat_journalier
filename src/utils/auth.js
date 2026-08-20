const cacheKeys = [
  't24_diff_cache',
  't24_transactions_cache',
  'powercard_transactions_cache'
]

export const clearAppCache = () => {
  cacheKeys.forEach((key) => {
    sessionStorage.removeItem(key)
  })
}