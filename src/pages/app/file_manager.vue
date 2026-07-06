<template>
  <div id="upload-container">
             
            <div class="text-center pa-4">
              <v-dialog
                v-model="dialog"
                max-width="200"
                max-height="400"
                persistent  
              >
              
                
              </v-dialog>
            </div>
    
  </div>

</template>

<script setup>
import { ref,inject } from 'vue'
import axios from '@/api/axios'
import { usePopupStore } from '../../stores'
import Cookies from 'js-cookie'
import import_progress from '../../components/loading/import_progress.vue'
import { VTreeview } from 'vuetify/labs/VTreeview'

const dialog = ref(false)



</script>



<style scoped>
.export-floating {
  position: absolute;
  top: 14px;
  right: 70px;
  z-index: 500;
  font-weight: bold;
    width: 150px;

}
.export-floating_import {
  position: absolute;
  top: 100px;
  right: 70px;
  z-index: 500;
  font-weight: bold;
    width: 250px;

}

.custom_title{

  font-size: 12px;
}
.file_loaded{
  background: green;
}
#list_{
  margin:71px 0px;
}
#separateur{
  height: 1px;
  margin-top: 20px;
  margin-bottom: 12px;
}
#modal-content{
  display: flex;
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  backdrop-filter: blur(4px);
  align-items: center;
  justify-content: center;
  z-index: 100;
}
#modal-list{
  display: flex;
  flex-direction: column;
  padding: 10px 20px;
  border-radius: 5px;

}
#title{
  font-size: 19px;
  font-weight: bold;
}
#history{
  position: absolute;
  bottom: 80px;
  right: 80px;
  font-size: 20px;
}
#history:hover{
  cursor: pointer;
}
/* Conteneur principal centré */
#upload-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh; 
}

/* Boîte d'upload */
.upload-box {
  width: 500px;
  border: 2px dashed ;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 20px;
}

/* Icône Upload */
.upload-icon {
  margin-bottom: 10px;
}

/* Texte principal */
.upload-text {
  font-size: 20px;
  font-weight: bold;
  margin: 0;
}

/* Texte secondaire */
.upload-subtext {
  font-size: 14px;
  margin: 10px 0;
}


/* Cacher l'input file */
.hidden-file-input {
  display: none;
}
.animIt{
 animation:   spin .5s linear infinite;
}
@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* Styles pour le dialogue d'import */
.import-file-list {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid ;
  border-radius: 4px;
  padding: 8px;
}

.import-file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.import-file-item:last-child {
  border-bottom: none;
}

.import-file-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.import-file-name {
  font-weight: 500;
}

.import-file-size {
  font-size: 0.8em;
}

.import-status-chip {
  font-size: 0.7em;
  padding: 2px 8px;
  border-radius: 12px;
}

.import-success {
  color: #2e7d32;
}

.import-error {
  color: #c62828;
}

.import-warning {
  color: #ef6c00;
}

/* Animation pour les notifications */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}

/* Bouton flottant d'import */
.export-floating_import {
  position: absolute;
  top: 100px;
  right: 70px;
  z-index: 500;
  font-weight: bold;
  width: 250px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.export-floating_import:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
  transform: translateY(-1px);
}


</style>
