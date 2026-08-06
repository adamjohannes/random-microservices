<script setup lang="ts">
defineProps<{ user: { id: string; name: string; email: string } }>()
</script>

<template>
  <div>
    <div class="font-medium text-sm">{{ user.name }}</div>
    <div class="text-xs text-gray-400">{{ user.email }}</div>
  </div>
</template>
