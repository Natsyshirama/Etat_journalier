<template>
  <div class="bg_data">

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
</template><script setup>
import { onMounted, ref, watch } from 'vue';
import { usePopupStore } from '../stores';

const tab = ref('one');

const listes = {
  encours: ref([]),
  remboursement: ref([]),
  avm: ref([]),
  caution: ref([]),
};

const headersBase = [
  { align: 'start', sortable: false },
  { title: '#', value: 'index', sortable: false },
];

const headers = {
  encours: [
    ...headersBase,
    { key: 'Agence', title: 'Agence' },
    { key: 'identification_client', title: 'identification_client' },
    { key: 'Numero_pret', title: 'Numero_pret' },
    { key: 'linked_appl_id', title: 'linked_appl_id' },
    { key: 'Date_pret', title: 'Date_pret' },
    { key: 'Date_fin_pret', title: 'Date_fin_pret' },
    { key: 'Nom_client', title: 'Nom_client' },
    { key: 'Produits', title: 'Produits' },
    { key: 'Amount', title: 'Amount' },
    { key: 'Duree_Remboursement', title: 'Duree_Remboursement' },
    { key: 'taux_d_interet', title: 'taux_d_interet' },
    { key: 'Nombre_de_jour_retard', title: 'Nombre_de_jour_retard' },
    { key: 'payment_date', title: 'payment_date' },
    { key: 'Status_du_client', title: 'Status_du_client' },
    { key: 'capital_non_appele', title: 'capital_non_appele' },
    { key: 'capital_appele', title: 'capital_appele' },
    { key: 'Total_capital_echus_non_echus', title: 'Total_capital_echus_non_echus' },
    { key: 'Total_interet_echus', title: 'Total_interet_echus' },
    { key: 'OD Pen', title: 'OD Pen' },
    { key: 'OD & PEN', title: 'OD & PEN' },
    { key: 'Genre', title: 'Genre' },
    { key: 'Secteur_d_activité', title: 'Secteur_d_activité' },
    { key: 'Agent_de_gestion', title: 'Agent_de_gestion' },
    { key: 'Code_Garantie', title: 'Code_Garantie' },
    { key: 'Chiffre_Affaire', title: 'Chiffre_Affaire' },
    { key: 'Valeur_garantie', title: 'Valeur_garantie' },
    { key: 'CODE', title: 'Secteur_d_activité_code' },
    { key: 'status', title: 'status' },
    { key: 'local_refs', title: 'local_refs' }
  ],
  remboursement: [
    ...headersBase,
    { key: 'arrangement_id', title: 'arrangement_id' },
    { key: 'Date_pret', title: 'Date_pret' },
    { key: 'product', title: 'product' },
    { key: 'co_code', title: 'co_code' },
    { key: 'linked_appl_id', title: 'linked_appl_id' },
    { key: 'Nom_client', title: 'Nom_client' },
    { key: 'customer', title: 'customer' },
    { key: 'echeance', title: 'echeance' },
    { key: 'date_echeance', title: 'date_echeance' },
    { key: 'payment_date', title: 'payment_date' },
    { key: 'Capital', title: 'Capital' },
    { key: 'principal_int', title: 'principal_int' },
    { key: 'penality_int', title: 'penality_int' },
    { key: 'TOTAL', title: 'TOTAL' },
  ],
  avm: [
    ...headersBase,
    { key: 'id', title: 'id' },
    { key: 'Name', title: 'Name' },
    { key: 'approval_date', title: 'approval_date' },
    { key: 'expiry_date', title: 'expiry_date' },
    { key: 'internal_amount', title: 'internal_amount' },
    { key: 'total_os', title: 'total_os' },
    { key: 'avail_amt', title: 'avail_amt' },
  ],
  caution: [
    ...headersBase,
    { key: 'id', title: 'id' },
    { key: 'Name', title: 'Name' },
    { key: 'approval_date', title: 'approval_date' },
    { key: 'expiry_date', title: 'expiry_date' },
    { key: 'internal_amount', title: 'internal_amount' },
    { key: 'total_os', title: 'total_os' },
    { key: 'avail_amt', title: 'avail_amt' },
  ],
};

const tabs = ref([
  { value: 'one', label: 'Etat des cours', title: 'Etats des encours', liste: listes.encours, headers: headers.encours, search: '' },
  { value: 'two', label: 'Etat DE Remboursement', title: 'Etats de remboursement', liste: listes.remboursement, headers: headers.remboursement, search: '' },
  { value: 'three', label: 'Limit AVM', title: 'Limite AVM', liste: listes.avm, headers: headers.avm, search: '' },
  { value: 'four', label: 'Limit CAUTION', title: 'Limite CAUTION', liste: listes.caution, headers: headers.caution, search: '' }
]);

const popup = usePopupStore();

async function fetchData(url, listRef, storeKey) {
  // listRef doit être un ref (ex: listes.encours)
  popup[storeKey] = [];
  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Erreur HTTP : ${response.status}`);
    const data = await response.json();

    // reset
    listRef.value = [];

    // support structure: data.response.data ou tableau direct
    const rows = data?.response?.data ?? (Array.isArray(data) ? data : []);
    if (Array.isArray(rows)) {
      rows.forEach(item => listRef.value.push(item));
    }

    popup[storeKey] = listRef.value;

    // si tu veux garder la référence dans tabs (optionnel)
    if (storeKey === 'encours_actual_data') {
      tabs.value[0].liste = listRef;
    } else if (storeKey === 'remboursement_actual_data') {
      tabs.value[1].liste = listRef;
    }
  } catch (error) {
    console.error('❌ Erreur de chargement :', error);
  }
}

watch(() => popup.selected_date, (val) => {
  const date = val?.value ?? val;
  // vider les listes
  listes.encours.value = [];
  listes.remboursement.value = [];

  if (date) {
    fetchData(`http://127.0.0.1:8000/api/get_encours_credits?date=${date}`, listes.encours, 'encours_actual_data');
    fetchData(`http://127.0.0.1:8000/api/encours_remboursement?date=${date}`, listes.remboursement, 'remboursement_actual_data');
  }
});

onMounted(() => {
  const date = '20250829';
  fetchData(`http://127.0.0.1:8000/api/get_encours_credits?date=${date}`, listes.encours, 'encours_actual_data');
  fetchData(`http://127.0.0.1:8000/api/encours_remboursement?date=${date}`, listes.remboursement, 'remboursement_actual_data');
  fetchData(`http://127.0.0.1:8000/api/encours_limit?limit_type=8400`, listes.avm, 'limit_avm_actual_data');
  fetchData(`http://127.0.0.1:8000/api/encours_limit?limit_type=2900`, listes.caution, 'limit_caution_actual_data');
});
</script>
