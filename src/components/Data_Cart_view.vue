<template>
  <div class="bg_data mr-4">
    <div class="flex flex-row justify-end items-center space-x-4">
      <h3 class="mr-5 text-xl">Date d'arrêt</h3>

      <v-menu
        v-model="menu"
        close-on-content-click
        offset-y
        max-width="200"
        min-width="200"
      >
        <template #activator="{ props }">
          <v-btn v-bind="props" prepend-icon="mdi-calendar-range" variant="outlined">
            <template #prepend>
              <v-icon color="success" />
            </template>
            <span class="text-2xl">{{ selectedDate }}</span>
          </v-btn>
        </template>

      <v-list style="max-height: 200px; overflow-y: auto;">
        <v-list-item
          v-for="date in historyDates"
          :key="date.label"
          @click="() => selectDate(date.label)"
          role="button"
        >

        <div class="flex" :title="date.stat_of!='init'? 'Base non initialisé':''">
          
          <v-icon v-if="date.stat_of !== 'init'"   class=" mr-2 text-red-700">mdi-database-alert</v-icon> 
          <v-icon v-else color="success" class=" mr-2">mdi-database-check</v-icon> 
          <v-list-item-title>{{ date.label }}</v-list-item-title>
        </div>
        </v-list-item>
      </v-list>
      </v-menu>
    </div>
    <div class="flex flex-row   w-full   "> 
      <div   v-for="(item) in charts" key="item.id" class=" w-full h-full flex justify-between"> 
         
        <div   class=" flex flex-col">
          <doughnut 
            :key="item.id"
            :id="item.id"
            :title="item.title"
            :data="item.data"
            :labels="item.labels"
            :colors="item.colors"
            :circumference="item.circumference"
            :heigth="item.heigths"
          />
        </div> 
      </div>
    </div> 
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import doughnut from './doughnut/Dougnut.vue'
import { usePopupStore } from '../stores'

const charts = ref([])

const menu = ref(false)
const selectedDate = ref('Chargement en cours...')

// Tableau des dates prédéfinies
const historyDates  = ref([])
const stat_local_ref  = ref([])
const stat_PA  = ref([])

async function selectDate(date) {
  
 charts.value = []
  selectedDate.value = date
  usePopupStore().selected_date.value = date
  menu.value = false
   
  stat_PA.value = await fetchData('http://192.168.1.212:8000/api/get_pa_class',date) 
  updateSecondChartFromData(stat_PA.value,'theard_chart',180,['#FF0031',  '#FF00FF','#00FFFF','#00c62b','#ffffff'], '300px') 
   
  stat_local_ref.value = await fetchData('http://192.168.1.212:8000/api/get_local_ref',date,'1000px') 
  updateSecondChartFromData(stat_local_ref.value,'second_chart',360)
 
}

// history_insert
async function fetchData(baseUrl, date = null) {
  try {
    // Si une date est fournie, on l’ajoute à l’URL
    const url = date ? `${baseUrl}?date=${date}` : baseUrl

    const response = await fetch(url)
    if (!response.ok) throw new Error(`Erreur HTTP : ${response.status}`)

    const data = await response.json()
    return data.response.data
  } catch (error) {
    console.error('❌ Erreur de chargement :', error)
    return []
  }
}

function updateSecondChartFromData(dataArray,name, circumference,color = null,height = null) {
  if (!Array.isArray(dataArray) || dataArray.length === 0) return

  const labels = []
  const data = []
  const colors = [] 

  dataArray.forEach((item) => {
    labels.push(item.initial || 'Inconnu')
    data.push(item.total || 0)
    colors.push(generateRandomColor())
  })
  var chart_Data= {
                    id: name,
                    title: 'Local ref',
                    data: [25, 25, 25, 25],
                    labels: ['Q1', 'Q2', 'Q3', 'Q4'],
                    colors: ['#eab308', '#3b82f6', '#f43f5e', '#10b981'],
                    circumference: circumference, 
                    heigths:'400px' 
                  }
  chart_Data.data=data
  chart_Data.labels=labels
  chart_Data.colors=color===null?colors: color
  chart_Data.heigths=color===null?'400px': height 
  charts.value.push(chart_Data) 
}

function generateRandomColor() {
  const letters = '0123456789ABCDEF'
  let color = '#'
  for (let i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)]
  }
  return color
}



watch(historyDates, (val) => {
  if (Array.isArray(val) && val.length > 0) { 
    selectedDate.value = val[0].label
    console.log("📅 Date sélectionnée automatiquement :", selectedDate.value)
  }
}, { immediate: true })

onMounted(() => {
  
 (async () => {
    historyDates.value = await fetchData('http://192.168.1.212:8000/api/history_insert')
  })();

 (async () => {
    stat_PA.value = await fetchData('http://192.168.1.212:8000/api/get_pa_class','20250731') 
    updateSecondChartFromData(stat_PA.value,'theard_chart',180,['#FF0031',  '#FF00FF','#00FFFF','#00c62b','#ffffff'], '300px') 
  })();

  
 (async () => {
    stat_local_ref.value = await fetchData('http://192.168.1.212:8000/api/get_local_ref','20250731','1000px') 
    updateSecondChartFromData(stat_local_ref.value,'second_chart',360)
    
  })();
})

</script>

<style scoped>
.bg_data {
  background-color: #00000022;
  border-radius: 20px;
  padding: 10px 20px;
}
</style>
