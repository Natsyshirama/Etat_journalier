<template>
  <div class="p-4">
    <h2 class="text-xl font-bold mb-4">Graphique dynamique</h2>

    <div class="flex gap-4 mb-6">
      <select v-model="x" @change="loadData" class="border p-2">
        <option disabled value="">-- Axe X --</option>
        <option value="code_client">Client</option>
        <option value="Agence">Agence</option>
        <option value="Produits">Produits</option>
      </select>

      <select v-model="y" @change="loadData" class="border p-2">
        <option disabled value="">-- Axe Y --</option>
        <option value="Agence">Agence</option>
        <option value="code_client">Client</option>
        <option value="Produits">Produits</option>
      </select>
    </div>

    <canvas id="myChart"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { Chart } from "chart.js/auto";

const x = ref("");
const y = ref("");
const tableName = "dat_20250915"; // 👈 table par défaut
let chart = null;

const loadData = async () => {
  if (!x.value || !y.value) return;

  const res = await fetch(`http://127.0.0.1:8000/api/dat/${tableName}?x=${x.value}&y=${y.value}`);
  const json = await res.json();

  if (json?.rows) {
    const labels = json.rows.map(item => item.y_value);
    const values = json.rows.map(item => item.count);

    if (chart) chart.destroy();

    const ctx = document.getElementById("myChart").getContext("2d");
    chart = new Chart(ctx, {
      type: "bar",
      data: {
        labels,
        datasets: [
          {
            label: `${x.value} par ${y.value}`,
            data: values,
            backgroundColor: "rgba(54, 162, 235, 0.6)",
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: true },
        },
      },
    });
  }
};

onMounted(() => {
  x.value = "code_client";
  y.value = "Agence";
  loadData();
});
</script>
