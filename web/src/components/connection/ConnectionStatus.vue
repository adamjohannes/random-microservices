<script setup lang="ts">
defineProps<{ status: 'PENDING' | 'ACCEPTED' | 'REJECTED' }>()

const colours: Record<string, string> = {
  PENDING: 'bg-yellow-100 text-yellow-700',
  ACCEPTED: 'bg-green-100 text-green-700',
  REJECTED: 'bg-red-100 text-red-600',
}
</script>

<template>
  <span :class="['text-xs px-2 py-0.5 rounded-full font-medium', colours[status]]">{{ status }}</span>
</template>
