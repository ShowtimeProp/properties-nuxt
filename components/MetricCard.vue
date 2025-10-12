<template>
  <div class="metric-card bg-white rounded-lg shadow-md p-6 border-l-4" :class="borderColor">
    <div class="flex items-center justify-between">
      <div>
        <p class="text-sm font-medium text-gray-600">{{ title }}</p>
        <p class="text-2xl font-bold text-gray-900">{{ formattedValue }}</p>
        <div class="flex items-center mt-2">
          <span 
            class="text-sm font-medium flex items-center"
            :class="changeColor"
          >
            <svg 
              v-if="change >= 0" 
              class="w-4 h-4 mr-1" 
              fill="currentColor" 
              viewBox="0 0 20 20"
            >
              <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
            <svg 
              v-else 
              class="w-4 h-4 mr-1" 
              fill="currentColor" 
              viewBox="0 0 20 20"
            >
              <path fill-rule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clip-rule="evenodd" />
            </svg>
            {{ Math.abs(change) }}%
          </span>
          <span class="text-sm text-gray-500 ml-2">vs mes anterior</span>
        </div>
      </div>
      <div class="flex-shrink-0">
        <div class="w-12 h-12 rounded-full flex items-center justify-center" :class="iconBgColor">
          <svg class="w-6 h-6" :class="iconColor" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <!-- Users Icon -->
            <path v-if="icon === 'users'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
            <!-- User Check Icon -->
            <path v-else-if="icon === 'user-check'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            <!-- Target Icon -->
            <path v-else-if="icon === 'target'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            <!-- Dollar Sign Icon -->
            <path v-else-if="icon === 'dollar-sign'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
          </svg>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [Number, String],
    required: true
  },
  change: {
    type: Number,
    default: 0
  },
  icon: {
    type: String,
    required: true
  },
  color: {
    type: String,
    default: 'blue'
  }
})

const formattedValue = computed(() => {
  if (typeof props.value === 'number') {
    if (props.value >= 1000000) {
      return `$${(props.value / 1000000).toFixed(1)}M`
    } else if (props.value >= 1000) {
      return `$${(props.value / 1000).toFixed(0)}K`
    }
    return `$${props.value.toLocaleString()}`
  }
  return props.value
})

const borderColor = computed(() => {
  const colors = {
    blue: 'border-blue-500',
    green: 'border-green-500',
    purple: 'border-purple-500',
    orange: 'border-orange-500'
  }
  return colors[props.color] || colors.blue
})

const iconBgColor = computed(() => {
  const colors = {
    blue: 'bg-blue-100',
    green: 'bg-green-100',
    purple: 'bg-purple-100',
    orange: 'bg-orange-100'
  }
  return colors[props.color] || colors.blue
})

const iconColor = computed(() => {
  const colors = {
    blue: 'text-blue-600',
    green: 'text-green-600',
    purple: 'text-purple-600',
    orange: 'text-orange-600'
  }
  return colors[props.color] || colors.blue
})

const changeColor = computed(() => {
  return props.change >= 0 ? 'text-green-600' : 'text-red-600'
})
</script>

<style scoped>
.metric-card {
  transition: transform 0.2s ease-in-out;
}

.metric-card:hover {
  transform: translateY(-2px);
}
</style>
