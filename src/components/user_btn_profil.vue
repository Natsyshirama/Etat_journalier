<template>
  <div class="text-center">
    <v-menu
      v-model="menu"
      :close-on-content-click="false"
      location="bottom"
    >
      <template v-slot:activator="{ props }">
        <v-btn
          color="green"
          v-bind="props"
          icon="mdi mdi-cog-box"
          style="font-size: 24px;"
        > 
        </v-btn>
      </template>

      <v-card min-width="300">
        <v-list>
          <v-list-item
            prepend-avatar=""
            subtitle="Compte"
            :title="popupStore.user_access.name"
          >
            <template v-slot:append>
              <v-btn
                class=" text-red"
                icon="mdi mdi-power"
                variant="text"
                @click="logout()"
              ></v-btn>
            </template>
          </v-list-item>
        </v-list>

        <v-divider></v-divider>

        <v-list>
          <v-list-item>
            <v-switch
              v-model="isDark"
              color="green"
              label="Mode Sombre"
              hide-details 
              @update:modelValue="toggleTheme"
            ></v-switch>
          </v-list-item> 
        </v-list> 
      </v-card>
    </v-menu>
  </div>
</template>

<script setup>
import { ref , onMounted,inject} from 'vue'
import { usePopupStore } from '../stores'  
import { clearAppCache } from '@/utils/auth'

const api = inject('api') 
const menu = ref(false) 
const hints = ref(true)
const popupStore = usePopupStore()
const isDark=ref(false)
 
import { useTheme } from 'vuetify'
const { global } = useTheme() 
 
  
// Définit le thème en clair
const setLightTheme=()=> {
  global.name.value = 'light'
  localStorage.setItem('theme', 'light')
}

// Définit le thème en sombre
const setDarkTheme=()=> {
  global.name.value = 'dark'
  localStorage.setItem('theme', 'dark')
} 

const toggleTheme=()=> { 
  
  if (isDark.value) {
    setDarkTheme()
  } else {
    setLightTheme()
  }
}

const logout = async () => {
  try {
    await fetch(`${api}/api/logout`, {
      method: 'POST',
      credentials: 'include'
    })
  } finally {
    clearAppCache()
    localStorage.removeItem('access_token')
    localStorage.removeItem('privilege')
    location.replace('/login')
  }
}

onMounted(() => { 
 
  const theme = localStorage.getItem('theme')
  if (theme) {
    global.name.value = theme 
    if (theme=='dark') {
      isDark.value=true
    }
    
  }
   
})
</script>