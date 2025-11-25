// src/stores/notification.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export const useNotificationStore = defineStore('notification', () => {
  const demandesValidation = ref(0)
  const fetchDemandesValidation = async (api) => {
    try {
      const res = await axios.get(`${api}/api/users/pending_count`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
      })
      demandesValidation.value = res.data.count || 0
    } catch (e) {
      demandesValidation.value = 0
    }
  }
  return { demandesValidation, fetchDemandesValidation }
})