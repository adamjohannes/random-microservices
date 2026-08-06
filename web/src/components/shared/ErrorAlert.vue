<script setup lang="ts">
defineProps<{ message: string }>()
</script>

<template>
  <div class="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 text-sm">{{ message }}</div>
</template>
