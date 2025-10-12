<template>
  <div class="pipeline-board">
    <div class="flex space-x-4 overflow-x-auto pb-4">
      <div 
        v-for="stage in stages" 
        :key="stage.id"
        class="pipeline-column flex-shrink-0 w-64 bg-gray-50 rounded-lg p-4"
      >
        <!-- Header del Stage -->
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center">
            <div class="w-3 h-3 rounded-full mr-2" :class="stage.color"></div>
            <h4 class="font-semibold text-gray-900">{{ stage.name }}</h4>
          </div>
          <span class="bg-white px-2 py-1 rounded-full text-sm font-medium text-gray-600">
            {{ getLeadsForStage(stage.id).length }}
          </span>
        </div>

        <!-- Leads en este Stage -->
        <div class="space-y-3">
          <div 
            v-for="lead in getLeadsForStage(stage.id)" 
            :key="lead.id"
            class="pipeline-lead bg-white rounded-lg p-3 shadow-sm border border-gray-200 cursor-pointer hover:shadow-md transition-shadow"
            @click="selectLead(lead)"
          >
            <div class="flex justify-between items-start mb-2">
              <h5 class="font-medium text-gray-900 text-sm">{{ lead.name }}</h5>
              <span class="text-xs text-gray-500">{{ formatDate(lead.lastActivity) }}</span>
            </div>
            <div class="text-sm text-gray-600">
              <p class="font-medium text-green-600">${{ formatCurrency(lead.value) }}</p>
            </div>
            <div class="mt-2 flex items-center justify-between">
              <span class="text-xs text-gray-500">Última actividad</span>
              <div class="flex space-x-1">
                <button 
                  v-if="stage.id !== 'new'"
                  @click.stop="moveLead(lead, getPreviousStage(stage.id))"
                  class="text-xs text-blue-600 hover:text-blue-800"
                >
                  ←
                </button>
                <button 
                  v-if="stage.id !== 'closed'"
                  @click.stop="moveLead(lead, getNextStage(stage.id))"
                  class="text-xs text-blue-600 hover:text-blue-800"
                >
                  →
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Botón para agregar nuevo lead -->
        <button 
          class="w-full mt-3 p-2 border-2 border-dashed border-gray-300 rounded-lg text-gray-500 hover:border-gray-400 hover:text-gray-600 transition-colors"
          @click="addNewLead(stage.id)"
        >
          + Agregar Lead
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineEmits } from 'vue'

const props = defineProps({
  stages: {
    type: Array,
    required: true
  },
  leads: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['lead-selected', 'lead-moved', 'add-lead'])

const getLeadsForStage = (stageId) => {
  return props.leads.filter(lead => lead.stage === stageId)
}

const selectLead = (lead) => {
  emit('lead-selected', lead)
}

const moveLead = (lead, newStage) => {
  emit('lead-moved', { lead, newStage })
}

const addNewLead = (stageId) => {
  emit('add-lead', stageId)
}

const getPreviousStage = (currentStageId) => {
  const stageIndex = props.stages.findIndex(stage => stage.id === currentStageId)
  return stageIndex > 0 ? props.stages[stageIndex - 1].id : currentStageId
}

const getNextStage = (currentStageId) => {
  const stageIndex = props.stages.findIndex(stage => stage.id === currentStageId)
  return stageIndex < props.stages.length - 1 ? props.stages[stageIndex + 1].id : currentStageId
}

const formatCurrency = (value) => {
  return new Intl.NumberFormat('es-AR', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0
  }).format(value)
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('es-AR', {
    day: '2-digit',
    month: '2-digit'
  })
}
</script>

<style scoped>
.pipeline-board {
  min-height: 400px;
}

.pipeline-column {
  min-height: 350px;
}

.pipeline-lead {
  transition: all 0.2s ease-in-out;
}

.pipeline-lead:hover {
  transform: translateY(-1px);
}
</style>
