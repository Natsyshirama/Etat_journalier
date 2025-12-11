<template>
  <div id="upload-container">
             
            <div class="text-center pa-4">
              <v-dialog
                v-model="dialog"
                max-width="200"
                max-height="400"
                persistent  
                style=" background-color: #000000EE;"           
              >
              
                <div class="   w-full flex-col flex items-center justify-center"  >    
                    <v-progress-circular :model-value="percentage" :rotate="360" :size="150" :width="1.5" color="green">
                      <div class="flex flex-col items-center justify-center" > 
                        <span  class=" text-xl font-bold" v-if="percentage!=0">{{!'100.00%'?'100%':percentage}}</span>
                        <span v-else class=" animate-ping"> Chargement ...</span>
                        <span title="Temps de chargement" class="  text-stone-100 font-bold" v-text=" percentage=='100.00%'?'Fait':'Encours'"></span>
                      </div>
                    </v-progress-circular> 

                    <div>
                      <span class="white underline">Telechargement</span>
                      <div class="flex flex-row  text-green-500 mt-2">
                         <v-icon icon="mdi-file-chart-outline ml-2 mr-5"></v-icon>
                        {{download_file_name}}
                      </div>
                    </div>
                </div  > 
              </v-dialog>
            </div> 

    <popup_view v-if="usePopupStore().show_notification.status" style=" z-index: 10000;"></popup_view>
    <v-card class="upload-box" outlined>
      <v-icon size="48" class="upload-icon">mdi-cloud-upload</v-icon>
      <p class="upload-text">Importer les Fichiers ici</p>
      <p class="upload-subtext">ou choisissez localement</p>
      <div style="display: flex; flex-direction: row; align-items: center;">
        <v-btn variant="outlined" class="upload-btn" @click="triggerFileInput" id="file_name">  {{ file_name }}</v-btn>
        <div v-if="is_exist_file" style="display: flex; flex-direction: row; align-items: center;">
          <v-icon @click="cancel" size="24" title="Annuler" style="color: red; padding: 20px; margin-left: 10px; border-radius: 25px;">mdi-file-remove-outline</v-icon>
          <v-icon @click="open_dialoge_date" size="16" title="Charger le fichier" style="background: green; padding: 12px; margin-left: 10px; border-radius: 25px;"> mdi-check</v-icon>
        </div>
      </div>
      <ul v-if="file_names.length > 0" style="margin-top: 10px; list-style: none; padding-left: 0; max-height: 40vh; overflow-y: auto;">
        <li v-for="(name, index) in file_names" :key="index" style="display: flex; align-items: center;">
          <v-icon size="14" style="margin-right: 5px;">mdi-file</v-icon> {{ name }}
        </li>
      </ul>
      <input type="file" accept=".csv" multiple ref="fileInput" class="hidden-file-input" @change="handleFileUpload">
    </v-card>
    <v-dialog max-width="500">
      <template v-slot:activator="{ props: activatorProps }">
        <v-btn @click="showFiles" id="history" v-bind="activatorProps" icon="mdi-history" variant="flat"></v-btn>
      </template>      
      <template v-slot:default="{ isActive }">
        <v-card title="Explorateur de fichier">
          <div style="max-height: 400px; overflow-y: auto; padding: 0 30px;">
            <v-treeview v-if="list_file.length" v-model:opened="open" :items="list_file" density="compact" item-value="title" activatable open-on-click >
              <template v-slot:prepend="{ item, isOpen }" >
                <v-icon v-if="!item.file" :icon="isOpen ? 'mdi-folder-open' : 'mdi-folder'" />
                <v-icon v-else icon="mdi-file-chart-outline" style=" font-size: 15px;" />
                <button v-if="!item.file" style="position:absolute; margin-left: 400px;" @click.stop="chargerDossier(item,isActive)" >
                  <v-icon icon="mdi mdi-database " size="24" style=" position: relative; margin-left: -20px; margin-top: 7px; " />
                  <v-icon :id="'refresh' + item.title.replaceAll(/[^a-zA-Z0-9_-]/g, '_')" icon="mdi mdi-sync " size="12" style=" position: relative; margin-top: 20px;margin-left:-7px; background-color: black;border-radius: 15px;" />
                </button>
                <button  v-if="item.file"  style="position:absolute; margin-left: 380px;"  @click.stop="downloadFile(item)" >  
                  <v-icon :id="'download' + item.title.replaceAll(/[^a-zA-Z0-9_-]/g, '_')" icon="mdi mdi-download" size="17" style="position: relative; margin-top: -7px; margin-left:-40px; background-color: transparent; border-radius: 15px;"  />
                </button>
              </template>
              <template #title="{ item }">
                <span :class="item.file ? 'custom_title' : ''">{{CastString( item.title )}} </span>
                
              </template>
            </v-treeview>
          </div>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn text="Fermer" @click="isActive.value = false" />
          </v-card-actions>
        </v-card>
      </template>
    </v-dialog>
    <v-dialog v-model="isDialogActive" max-width="500">
      <v-card title="Date du dossier" >
        <!-- contenu du dialogue -->
        <div style=" padding: 0px 70px;">
          <v-text-field
            v-model="date_dossier"
            label="Date de traitement dans fichier"
            type="date"
            dense
            :max="today"
            @change="check_data_state" variant="outlined"/></div>
        <v-card-actions>
          <v-btn @click="check_file"   :disabled="!is_full" :color="is_full ? 'red' : 'gray'"  variant="flat" class="ml-2">Importer?</v-btn>
          <v-btn text @click="isDialogActive = false">Fermer</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>



    <import_progress v-if="show_progress_import">
    </import_progress>

    <!-- Dialog pour l'exportation -->
    <v-dialog v-model="exportDialog" max-width="900">
      <template #activator="{ props }">
  <v-btn
    color="success"
    v-bind="props"
    prepend-icon="mdi-export"
    class="export-floating"
  >
    Export Multi
  </v-btn>
</template>

      <v-card>
        <v-card-title>Export Multi-fichiers</v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12">
              <v-select
                v-model="exportType"
                :items="['dav', 'dat', 'epr', 'decaissement', 'all']"
                label="Type de données"
                required
              />
            </v-col>
            <v-col cols="6">
              <v-text-field v-model="exportDateDebut" label="Date début" type="date" required />
            </v-col>
            <v-col cols="6">
              <v-text-field v-model="exportDateFin" label="Date fin" type="date" required />
            </v-col>
            <v-col cols="12">
              <v-select
                v-model="exportFormat"
                :items="['csv', 'excel']"
                label="Format"
                required
              />
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-btn color="primary" @click="exportMulti">Exporter</v-btn>
          <v-btn text @click="exportDialog = false">Fermer</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <!-- Ajoute dans ton template, par exemple dans file_manager.vue -->
 
    <v-dialog v-model="importDialog" max-width="900">
      <template #activator="{ props }">
        <v-btn color="primary" v-bind="props" prepend-icon="mdi-upload"
         class="export-floating_import">Importer Fichiers</v-btn>
      </template>
      <v-card>
        <v-card-title>
          <v-icon left>mdi-upload</v-icon>
          Importer des fichiers CSV
        </v-card-title>
        
        <v-card-text>
          <!-- Sélection de fichiers -->
          <div class="mb-4">
            <v-btn 
              color="primary" 
              prepend-icon="mdi-file-plus"
              @click="triggerImportFileSelect"
              class="mb-2"
            >
              Sélectionner des fichiers
            </v-btn>
            <input 
              type="file" 
              multiple 
              accept=".csv" 
              @change="handleImportFiles" 
              ref="importFilesInput" 
              style="display: none"
            />
            
            <!-- Liste des fichiers sélectionnés -->
            <div v-if="selectedFiles.length > 0" class="mt-4">
              <v-card variant="outlined">
                <v-card-title class="text-subtitle-1 font-weight-bold">
                  Fichiers à importer ({{ selectedFiles.length }})
                </v-card-title>
                <v-card-text>
                  <v-list density="compact">
                    <v-list-item 
                      v-for="(file, index) in selectedFiles" 
                      :key="index"
                      class="mb-1"
                    >
                      <template v-slot:prepend>
                        <v-icon color="blue" class="mr-2">mdi-file-document-outline</v-icon>
                      </template>
                      <v-list-item-title>
                        {{ file.name }}
                      </v-list-item-title>
                      <v-list-item-subtitle>
                        {{ formatFileSize(file.size) }} • 
                        Type: {{ getFileType(file.name) }}
                      </v-list-item-subtitle>
                      <template v-slot:append>
                        <v-btn
                          icon
                          size="small"
                          variant="text"
                          @click="removeFile(index)"
                          color="error"
                        >
                          <v-icon>mdi-close</v-icon>
                        </v-btn>
                      </template>
                    </v-list-item>
                  </v-list>
                </v-card-text>
              </v-card>
            </div>
          </div>
          
          <!-- Messages d'erreur -->
          <v-alert 
            v-if="importError" 
            type="error" 
            class="mt-2"
            :text="importError"
            closable
            @click:close="importError = ''"
          />
          
          <!-- Messages de succès -->
          <v-alert 
            v-if="importSuccess.length > 0" 
            type="success" 
            class="mt-2"
          >
            <div class="d-flex align-center">
              <v-icon class="mr-2">mdi-check-circle</v-icon>
              <span>Importation réussie !</span>
            </div>
            <div class="mt-2">
              <strong>Détails :</strong>
              <ul class="ml-4 mt-1">
                <li v-for="(success, index) in importSuccess" :key="index">
                  {{ success }}
                </li>
              </ul>
            </div>
          </v-alert>
          
          <!-- resultat apres import -->
          <v-expansion-panels v-if="importResults.length > 0" class="mt-4">
            <v-expansion-panel>
              <v-expansion-panel-title>
                <v-icon left>mdi-information</v-icon>
                Détails de l'importation
              </v-expansion-panel-title>
              <v-expansion-panel-text>
                <v-table density="compact">
                  <thead>
                    <tr>
                      <th>Fichier</th>
                      <th>Statut</th>
                      <th>Lignes</th>
                      <th>Message</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(result, index) in importResults" :key="index">
                      <td>{{ result.filename }}</td>
                      <td>
                        <v-chip 
                          :color="result.errors.length > 0 ? 'error' : 'success'" 
                          size="small"
                        >
                          {{ result.errors.length > 0 ? 'Erreur' : 'Succès' }}
                        </v-chip>
                      </td>
                      <td>{{ result.rows_inserted }}</td>
                      <td>
                        <span v-if="result.success.length > 0" class="text-success">
                          {{ result.success.join(', ') }}
                        </span>
                        <span v-if="result.errors.length > 0" class="text-error">
                          {{ result.errors.join(', ') }}
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </v-table>
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>
          
          <!-- Résumé après import -->
          <v-alert 
            v-if="importSummary" 
            type="info" 
            variant="tonal" 
            class="mt-4"
          >
            <div class="d-flex justify-space-between">
              <div>
                <strong>Résumé :</strong><br>
                Fichiers : {{ importSummary.total_files }}<br>
                Lignes insérées : {{ importSummary.total_rows_inserted }}<br>
                Dates : {{ importSummary.dates_imported ? importSummary.dates_imported.join(', ') : 'N/A' }}
              </div>
              <v-btn 
                v-if="importSummary.success_count > 0"
                color="success" 
                prepend-icon="mdi-check-all"
                @click="resetImport"
              >
                Nouvel import
              </v-btn>
            </div>
          </v-alert>
        </v-card-text>
        
        <v-card-actions class="pa-4">
          <v-btn 
            color="primary" 
            @click="triggerImport" 
            :loading="importLoading"
            :disabled="selectedFiles.length === 0 || importLoading"
            prepend-icon="mdi-database-import"
          >
            {{ importLoading ? 'Importation en cours...' : 'Importer' }}
          </v-btn>
          <v-btn 
            text 
            @click="resetImportDialog"
            :disabled="importLoading"
          >
            Annuler
          </v-btn>
          <v-spacer />
          <v-chip 
            v-if="selectedFiles.length > 0" 
            color="primary" 
            variant="outlined"
          >
            {{ selectedFiles.length }} fichier(s)
          </v-chip>
        </v-card-actions>
      </v-card>
    </v-dialog>

    
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
const download_file_name= ref('')
const api = inject('api') 
const file_names = ref([]);  // noms des fichiers
const file_name = ref("Importer un fichier");
const fileInput = ref(null)
const files_data = ref(null)
const is_exist_file = ref(false);
const today = new Date().toISOString().split('T')[0]
const isDialogActive = ref(false)
const show_progress_import = ref(false)
const percentage= ref(0)
// Fonction pour ouvrir la boîte de dialogue de sélection de fichiers
const triggerFileInput = () => {
  fileInput.value.click()
}
const list_file = ref([]);
const is_full=ref(false)
const date_dossier=ref()
const app_type=ref( Cookies.get('app'))

const open = ref([]);

// Créer une variable réactive pour stocker le nom du fichier
// Fonction pour gérer l'upload (facultatif)



const normalizeTree = (data) => {
  return data.map(item => ({
    title: item.title,
    children: Array.isArray(item.children) ? item.children.map(child => ({
      title: child.title,
      file: !!child.file
    })) : []
  }));
};

const CastString = (str) => {
  if (str.length <= 40) return str
  else return str.substring(0, 37) + '...' 
}

const handleFileUpload = (event) => {
  const files = event.target.files;
  const elt_ = document.getElementById('file_name');

  if (files.length < 5 || files.length > 21) {
    alert("Vous ne pouvez sélectionner que de 18 à 21  fichiers.");
    event.target.value = ""; // reset
    file_name.value = "Importer un fichier";
    file_names.value = [];
    files_data.value = [];
    elt_.classList.remove('file_loaded');
    is_exist_file.value = false;
    return;
  }

  const file = files[0];
  if (file) {
    // console.log('Fichier sélectionné :', file.name);
    files_data.value = Array.from(files); // tous les fichiers
    file_names.value = Array.from(files).map(f => f.name); // noms des fichiers
    file_name.value = `${files.length} fichier(s) sélectionné(s)`;
    elt_.classList.add('file_loaded');
    is_exist_file.value = true;
  }

    event.target.value = ""; // reset
};

const chargerDossier = (file,activatorProps) => {
  activatorProps.value=false
  let date_string= file.title.replace(/-/g, "")
  const id = 'refresh' + file.title.replaceAll(/[^a-zA-Z0-9_-]/g, '_');
  const refresh = document.getElementById(id);

  if (refresh) {
    refresh.classList.add('animIt')
  }
  // console.log(file.children);
  usePopupStore().cdi_list_stream=file.children  
  load_database(refresh,file.children,file.title,date_string) 
  setTimeout(() => {
    usePopupStore().togglePopupCDI();
  }, 300);

};


const cancel = () => {
  fileInput.value.value = "";
  file_name.value = "Importer un fichier";
  file_names.value = [];
  files_data.value = [];
  is_exist_file.value = false;
  document.getElementById('file_name').classList.remove('file_loaded');

};

const check_data_state = () => {
  if (date_dossier.value) {
    is_full.value = true
  }
}

const open_dialoge_date=()=> {
  isDialogActive.value = true
}

const load_database = async (refresh, files, folder,date_string) => {

  var index_table=0;
  try {
    const response = await fetch(`${api}/api/create_multiple_table`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        files: files.map(f => f.title),
        app: null,
        folder: folder,
        str_date:date_string
      })
    });

    if (!response.body) {
      throw new Error("Pas de flux en réponse !");
    } 
    

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    usePopupStore().precentage=0
    let partial = "";
    while (true) {
      
      const { done, value } = await reader.read();
      if (done) break;

      partial += decoder.decode(value, { stream: true });

      // Découper les lignes (JSON par ligne)
      let lines = partial.split("\n");  
      // console.log(lines);
      
      partial = lines.pop();
      for (const line of lines) {
        if (line.trim()) {
          try {
            const msg = JSON.parse(line);
            if (msg.fait) {
              usePopupStore().precentage=0
              usePopupStore().cdi_list_file_stream[index_table].success=true
              index_table++
              if (index_table==files.length) {
                setTimeout(() => {
                  usePopupStore().showPopupCDI = false
                }, 200);
              }

            }
            if(msg.filename ){
              usePopupStore().cdi_list_file_stream.push([
                {file_name:msg.filename},
                {task:msg.task},
                {row_count:msg.row_count},
                {success:false},
                {total:msg.total}])

            }else{
               if(msg.task){
                usePopupStore().cdi_list_file_stream[index_table].task=msg.task
                }
                if(msg.row_count){
                    usePopupStore().cdi_list_file_stream[index_table].row_count=msg.row_count
                }
                if(msg.total){
                    usePopupStore().cdi_list_file_stream[index_table].total=msg.total
                }
                if(msg.percentage){
                    usePopupStore().precentage=parseFloat(msg.percentage)
                }
            }

          } catch (e) {
            console.warn("Impossible de parser la ligne :", line,e);
          }
        }
      }
    }

  } catch (error) {
    console.error("Erreur lors du chargement du fichier dans la base :", error);
  } finally {
    refresh.classList.remove('animIt');
    index_table=0
    usePopupStore().cdi_list_file_stream=[]
  }
};

const check_file = () => {
  if (date_dossier.value) {
    show_progress_import.value=true
    uploadFile(date_dossier.value)
    isDialogActive.value = false
  }
  date_dossier.value=''
}

const uploadFile = async (folder_name) => {
  const formData = new FormData();
  files_data.value.forEach((file) => {
    formData.append('files', file);
  });
  formData.append('app', app_type.value);
  formData.append('folder_name', folder_name);
  try {
    const response = await fetch(`${api}/api/upload_multiple_files`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let { value: chunk, done: readerDone } = await reader.read();
    let buffer = '';

    while (!readerDone) {
      buffer += decoder.decode(chunk, { stream: true });

      // Découper par lignes (chaque ligne = un JSON)
      let lines = buffer.split('\n');
      buffer = lines.pop(); // dernière ligne incomplète

      for (const line of lines) {
        if (line.trim()) {
          try {
            const msg = JSON.parse(line);
            // console.log('Progress:', msg);
            if (msg.total_files) {
              // console.log(msg.total_files);
              
            }
            if (msg.status=="info" && msg.file) { 
              usePopupStore().loadFile="Chargement de "+msg.file
            }
            // if (msg.status==='success') {
           
            // }

            // // Mettre à jour ton store ou UI ici avec msg
            // if (msg.percentage) {
            //   usePopupStore().precentage = msg.percentage;
            //   console.log(usePopupStore().precentage);
              
            // }
            // if (msg.message) {
            //   usePopupStore().show_notification.message = msg.message;
            // }
            // etc...
          } catch (e) {
            console.warn('Erreur JSON:', e);
          } 
        }
      }

      ({ value: chunk, done: readerDone } = await reader.read());
    }

    // Fin de lecture
    if (buffer.trim()) {
      try {
        const msg = JSON.parse(buffer);
        // console.log('Final message:', msg);
      } catch(e) {
        console.warn('Erreur JSON fin de flux:', e);
      }
    }

    // Après upload, réinitialiser si besoin
    files_data.value = [];
    file_names.value = [];
    file_name.value = "Importer un fichier";
    is_exist_file.value = false;
    usePopupStore().loadFile='Fait'
    setTimeout(() => {
                show_progress_import.value=false
                usePopupStore().loadFile="Préparation ..."
              }, 2000);

    usePopupStore().show_notification.status = true;
    usePopupStore().show_notification.message = 'Fichier importé';
    usePopupStore().show_notification.ico = 'mdi mdi-check';

  } catch (error) {
    console.error('Erreur upload:', error);
  }
};



// Méthode pour afficher les fichiers
const showFiles = async () => {
  try {
    const response = await axios.get('/api/show_files', {
      params: {
        app:app_type.value
      }
    });
    console.log(response.data.files);
    list_file.value = normalizeTree(response.data.files);// Affichage des fichiers reçus
  } catch (error) {
    console.error("Erreur lors de la récupération des fichiers:", error); // Gestion des erreurs
  }
};

const show_popup=()=>{
  usePopupStore().togglePopup()
  // console.log(usePopupStore().showPopup,file_name);
  // usePopupStore().loadFile=file_name

}

const exportDialog = ref(false)
const exportType = ref('dav')
const exportDateDebut = ref('')
const exportDateFin = ref('')
const exportFormat = ref('csv')

const exportMulti = async () => {
  if (!exportDateDebut.value || !exportDateFin.value) {
    alert('Veuillez choisir une période')
    return
  }
  const params = new URLSearchParams({
    type: exportType.value,
    date_debut: exportDateDebut.value.replaceAll('-', ''),
    date_fin: exportDateFin.value.replaceAll('-', ''),
    format: exportFormat.value
  })
  const url = `${api}/api/export/multi?${params.toString()}`
  window.open(url, '_blank')
  exportDialog.value = false
}





const importDialog = ref(false)
const importError = ref("")
const importSuccess = ref([])
const importFilesInput = ref(null)
const selectedFiles = ref([])
const importLoading = ref(false)
const importResults = ref([])
const importSummary = ref(null)

// Fonctioselection fichier
const triggerImportFileSelect = () => {
  importFilesInput.value.click()
}

// Gestion selection fichier
const handleImportFiles = (event) => {
  const files = Array.from(event.target.files)
  
  // Valide
  const invalidFiles = []
  const validFiles = []
  
  files.forEach(file => {
    if (!file.name.toLowerCase().endsWith('.csv')) {
      invalidFiles.push(file.name)
    } else if (!/^(dav|dat|epr|decaissement)_\d{8}\.csv$/i.test(file.name)) {
      invalidFiles.push(`Format invalide: ${file.name}`)
    } else {
      validFiles.push(file)
    }
  })
  
  if (invalidFiles.length > 0) {
    importError.value = `Fichiers invalides : ${invalidFiles.join(', ')}`
  }
  
  selectedFiles.value = [...selectedFiles.value, ...validFiles]
  
  event.target.value = ''
}


const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getFileType = (filename) => {
  const match = filename.match(/^(dav|dat|epr|decaissement)_/)
  if (match) {
    const type = match[1]
    const typeMap = {
      'dav': 'Dépôts à vue',
      'dat': 'Dépôts à terme',
      'epr': 'Épargne',
      'decaissement': 'Décaissement'
    }
    return typeMap[type] || type.toUpperCase()
  }
  return 'Inconnu'
}

const removeFile = (index) => {
  selectedFiles.value.splice(index, 1)
}



const resetImportDialog = () => {
  selectedFiles.value = []
  importError.value = ""
  importSuccess.value = []
  importResults.value = []
  importSummary.value = null
  importLoading.value = false
  importDialog.value = false
}

const resetImport = () => {
  selectedFiles.value = []
  importError.value = ""
  importSuccess.value = []
  importResults.value = []
  importSummary.value = null
}

const triggerImport = async () => {
  importError.value = ""
  importSuccess.value = []
  importResults.value = []
  importSummary.value = null
  importLoading.value = true
  
  if (!selectedFiles.value.length) {
    importError.value = "Veuillez sélectionner au moins un fichier."
    importLoading.value = false
    return
  }
  
  if (selectedFiles.value.length > 1000) {
    importError.value = "Maximum 1000 fichiers par import."
    importLoading.value = false
    return
  }
  
  const formData = new FormData()
  selectedFiles.value.forEach(file => formData.append("files", file))
  
  try {
    const response = await fetch(`${api}/api/import/multi`, {
      method: "POST",
      body: formData
    })
    
    if (!response.ok) {
      throw new Error(`Erreur HTTP ${response.status}`)
    }
    
    const data = await response.json()
    
    if (data.errors && data.errors.length > 0) {
      importError.value = data.errors.join("\n")
    }
    
    if (data.success && data.success.length > 0) {
      importSuccess.value = data.success
    }
    
    if (data.details && Array.isArray(data.details)) {
      importResults.value = data.details
    }
    
    if (data.summary) {
      importSummary.value = data.summary
      
      if (data.summary.success_count > 0) {
        usePopupStore().show_notification.status = true
        usePopupStore().show_notification.message = `Importation réussie : ${data.summary.success_count} fichier(s) traité(s)`
        usePopupStore().show_notification.ico = 'mdi mdi-check'
      }
    }
    
    if (data.status === "completed" && data.summary.error_count === 0) {
      // Ne pas vider la liste immédiatement pour permettre la visualisation
      // selectedFiles.value = []
    }
    
  } catch (error) {
    console.error("Erreur lors de l'import :", error)
    importError.value = `Erreur lors de l'import : ${error.message}`
    
    usePopupStore().show_notification.status = true
    usePopupStore().show_notification.message = "Erreur lors de l'importation"
    usePopupStore().show_notification.ico = 'mdi mdi-alert'
    
  } finally {
    importLoading.value = false
  }
}




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
  color: white;
}
#list_{
  margin:71px 0px;
}
#separateur{
  height: 1px;
  margin-top: 20px;
  margin-bottom: 12px;
  background: gray;
}
#modal-content{
  display: flex;
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  backdrop-filter: blur(4px);
  background: rgba(0, 0, 0, 0.257);
  align-items: center;
  justify-content: center;
  z-index: 100;
}
#modal-list{
  display: flex;
  flex-direction: column;
  background: wheat;
  color: black ;
  padding: 10px 20px;
  border-radius: 5px;

}
#title{
  font-size: 19px;
  font-weight: bold;
  color: rgb(49, 49, 49);
}
#history{
  position: absolute;
  bottom: 80px;
  right: 80px;
  font-size: 20px;
}
#history:hover{
  cursor: pointer;
  color: white;
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
  background: #00000000;
  border: 2px dashed #666;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: white;
  text-align: center;
  padding: 20px;
}

/* Icône Upload */
.upload-icon {
  color: #ccc;
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
  color: #bbb;
  margin: 10px 0;
}

/* Bouton pour choisir un fichier */
.upload-btn {
  border-color: #fff;
  color: #fff;
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
  border: 1px solid #e0e0e0;
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
  color: #666;
}

.import-status-chip {
  font-size: 0.7em;
  padding: 2px 8px;
  border-radius: 12px;
}

.import-success {
  background-color: #e8f5e8;
  color: #2e7d32;
}

.import-error {
  background-color: #ffebee;
  color: #c62828;
}

.import-warning {
  background-color: #fff3e0;
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
