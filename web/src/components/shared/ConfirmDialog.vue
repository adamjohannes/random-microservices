<script setup lang="ts">
defineProps<{ message: string }>()
defineEmits<{ confirm: []; cancel: [] }>()
</script>

<template>
  <div class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
    <div class="bg-white rounded-xl shadow-lg p-6 max-w-sm w-full mx-4">
      <p class="mb-5 text-gray-700">{{ message }}</p>
      <div class="flex gap-3 justify-end">
        <button @click="$emit('cancel')" class="border rounded-lg px-4 py-2 text-sm hover:bg-gray-50">Cancel</button>
        <button @click="$emit('confirm')" class="bg-red-600 text-white rounded-lg px-4 py-2 text-sm font-semibold hover:bg-red-700">Confirm</button>
      </div>
    </div>
  </div>
</template>
