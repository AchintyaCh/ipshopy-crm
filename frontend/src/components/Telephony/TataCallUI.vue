<template>
  <div>
    <!-- Small popup for minimized call -->
    <div
      v-show="showSmallCallPopup"
      class="ml-2 flex cursor-pointer select-none items-center justify-between gap-1 rounded-full bg-surface-gray-7 px-2 py-[7px] text-base text-ink-gray-2"
      @click="toggleCallPopup"
    >
      <div
        class="flex justify-center items-center size-5 rounded-full bg-surface-gray-6 shrink-0 mr-1"
      >
        <Avatar
          v-if="contact?.image"
          :image="contact.image"
          :label="contact.full_name"
          class="!size-5"
        />
        <AvatarIcon v-else class="size-3" />
      </div>
      <span>{{ contact?.full_name ?? contact?.mobile_no }}</span>
      <span>·</span>
      <div v-if="callStatus == 'In progress'">
        {{ counterUp?.updatedTime }}
      </div>
      <div
        v-else-if="callStatus == 'Call ended' || callStatus == 'No answer'"
        class="text-ink-gray-5"
      >
        {{ callStatus }}
      </div>
      <div v-else>
        {{ callStatus }}
      </div>
      <FeatherIcon
        name="x"
        class="size-3 ml-1 cursor-pointer text-ink-gray-5"
        @click.stop="endCall"
      />
    </div>

    <!-- Full call popup -->
    <div
      v-show="showCallPopup"
      ref="callPopupHeader"
      class="fixed bottom-5 right-5 z-50 w-80 rounded-lg bg-surface-modal shadow-lg border border-outline-gray-modals flex flex-col"
      :style="style"
    >
      <div class="header flex justify-between items-center p-4 border-b border-outline-gray-modals">
        <div class="flex items-center gap-3 flex-1">
          <Avatar
            v-if="contact?.image"
            :image="contact.image"
            :label="contact.full_name"
            class="!size-10"
          />
          <div v-else class="flex justify-center items-center size-10 rounded-full bg-surface-gray-6">
            <AvatarIcon class="size-4" />
          </div>
          <div class="flex flex-col gap-1">
            <div class="font-medium text-ink-gray-9">
              {{ contact?.full_name ?? contact?.mobile_no }}
            </div>
            <div class="text-sm text-ink-gray-5">{{ contact?.mobile_no }}</div>
          </div>
        </div>
        <Button
          variant="ghost"
          icon="minimize-2"
          class="text-ink-gray-5"
          @click="toggleCallPopup"
        />
      </div>

      <div class="body flex-1 flex flex-col items-center justify-center gap-4 p-6">
        <div v-if="callStatus" class="text-center">
          <div class="text-2xl font-semibold text-ink-gray-9">
            {{ contact?.full_name ?? __('Call') }}
          </div>
          <div class="text-base text-ink-gray-5 mt-2">
            {{ callStatus }}
          </div>
        </div>

        <CountUpTimer v-if="callStatus == 'In progress'" ref="counterUp">
          <div class="text-3xl font-semibold text-ink-gray-9">
            {{ counterUp?.updatedTime }}
          </div>
        </CountUpTimer>

        <div class="flex gap-2 mt-4">
          <Button
            v-if="callStatus != 'Call ended' && callStatus != 'No answer'"
            variant="solid"
            theme="red"
            class="rounded-full !h-12 !w-12"
            :icon="PhoneIcon"
            @click="endCall"
          />
        </div>
      </div>

      <div class="footer flex justify-between gap-2 p-4 border-t border-outline-gray-modals">
        <Button
          class="flex-1"
          variant="ghost"
          :label="__('Add note')"
          :icon="NoteIcon"
          @click="showNoteWindow"
        />
        <Button
          class="flex-1"
          variant="ghost"
          :label="__('Add task')"
          :icon="TaskIcon"
          @click="showTaskWindow"
        />
      </div>
    </div>

    <!-- Note Modal -->
    <NoteModal
      v-model="showNoteModal"
      :note="note"
      doctype="CRM Call Log"
      @after="updateNote"
    />

    <!-- Task Modal -->
    <TaskModal
      v-model="showTaskModal"
      :task="task"
      doctype="CRM Call Log"
      @after="updateTask"
    />
  </div>
</template>

<script setup>
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import NoteIcon from '@/components/Icons/NoteIcon.vue'
import TaskIcon from '@/components/Icons/TaskIcon.vue'
import AvatarIcon from '@/components/Icons/AvatarIcon.vue'
import CountUpTimer from '@/components/CountUpTimer.vue'
import NoteModal from '@/components/Modals/NoteModal.vue'
import TaskModal from '@/components/Modals/TaskModal.vue'
import { useDraggable, useWindowSize } from '@vueuse/core'
import { Avatar, Button, FeatherIcon, call, createResource, toast } from 'frappe-ui'
import { ref, watch } from 'vue'

const showCallPopup = ref(false)
const showSmallCallPopup = ref(false)
const showNoteModal = ref(false)
const showTaskModal = ref(false)
const loading = ref(false)

const callStatus = ref('')
const phoneNumber = ref('')
const callData = ref(null)
const counterUp = ref(null)
const currentCallId = ref('')

const contact = ref({
  full_name: '',
  image: '',
  mobile_no: '',
})

const note = ref({
  name: '',
  title: '',
  content: '',
})

const task = ref({
  name: '',
  title: '',
  description: '',
  assigned_to: '',
  due_date: '',
  status: 'Open',
  priority: 'Medium',
})

const callPopupHeader = ref(null)

const { width, height } = useWindowSize()

let { style } = useDraggable(callPopupHeader, {
  initialValue: { x: width.value - 350, y: height.value - 250 },
  preventDefault: true,
})

const getContact = createResource({
  url: 'crm.integrations.api.get_contact_by_phone_number',
  makeParams() {
    return {
      phone_number: phoneNumber.value,
    }
  },
  onSuccess(data) {
    contact.value = data
  },
})

watch(phoneNumber, (value) => {
  if (!value) return
  getContact.fetch()
})

function makeOutgoingCall(number) {
  console.log("=" .repeat(80))
  console.log("[TATA TELE FRONTEND] Make Call Started")
  console.log("[TATA TELE FRONTEND] Input Number:", number)
  
  loading.value = true
  phoneNumber.value = number
  callStatus.value = 'Initiating...'
  showCallPopup.value = true
  showSmallCallPopup.value = false
  
  console.log("[TATA TELE FRONTEND] Phone Number Set:", phoneNumber.value)

  console.log("[TATA TELE FRONTEND] Creating API request...")
  
  // Use call() method directly instead of createResource with auto:true
  call('crm.integrations.tata_tele.handler.make_a_call', {
    to_number: phoneNumber.value
  })
    .then((response) => {
      loading.value = false
      console.log("[TATA TELE FRONTEND] API Success Response Received:")
      console.log(response)
      
      if (response && response.ok) {
        console.log("[TATA TELE FRONTEND] Call Initiated Successfully!")
        console.log("[TATA TELE FRONTEND] Call Details:")
        console.log("  - Call ID:", response.call_id)
        console.log("  - Agent Number:", response.agent_number)
        console.log("  - Caller ID:", response.caller_id)
        console.log("  - Response Data:", response.data)
        
        currentCallId.value = response.call_id
        callData.value = response.data
        callStatus.value = 'Calling...'
        
        console.log("[TATA TELE FRONTEND] UI State Updated:")
        console.log("  - Current Call ID:", currentCallId.value)
        console.log("  - Call Status:", callStatus.value)
        console.log("  - Show Call Popup:", showCallPopup.value)
        
        console.log("[TATA TELE FRONTEND] Showing success toast...")
        toast.success(__('Call initiated successfully to {0}', [phoneNumber.value]))
        console.log("[TATA TELE FRONTEND] Success toast shown")
      } else {
        console.warn("[TATA TELE FRONTEND] Call Failed - Invalid Response")
        console.warn("[TATA TELE FRONTEND] Response:", response)
        
        const errorMessage = response?.message || __('Failed to initiate call')
        
        console.log("[TATA TELE FRONTEND] Showing error toast...")
        toast.error(errorMessage)
        console.log("[TATA TELE FRONTEND] Error toast shown")
      }
      console.log("=" .repeat(80))
    })
    .catch((err) => {
      loading.value = false
      console.error("[TATA TELE FRONTEND] API Error Response Received:")
      console.error(err)
      console.error("[TATA TELE FRONTEND] Error Details:")
      console.error("  - Messages:", err.messages)
      console.error("  - Message:", err.message)
      console.error("  - Exception:", err.exception)
      
      let errorMessage = __('Failed to initiate call')
      
      if (err.messages && err.messages.length > 0) {
        errorMessage = err.messages.join(', ')
      } else if (err.message) {
        errorMessage = err.message
      } else if (err.exception) {
        errorMessage = err.exception
      }
      
      console.log("[TATA TELE FRONTEND] Showing error toast...")
      toast.error(errorMessage)
      console.log("[TATA TELE FRONTEND] Error toast shown")
      console.log("=" .repeat(80))
    })
}

function toggleCallPopup() {
  showCallPopup.value = !showCallPopup.value
  showSmallCallPopup.value = !showSmallCallPopup.value
}

function endCall() {
  showCallPopup.value = false
  showSmallCallPopup.value = false
  callStatus.value = 'Call ended'
  phoneNumber.value = ''
  callData.value = null
  currentCallId.value = ''

  // Save call log if it exists
  if (currentCallId.value) {
    call('frappe.client.set_value', {
      doctype: 'CRM Call Log',
      name: currentCallId.value,
      fieldname: 'status',
      value: 'Completed',
    }).catch(err => {
      console.error('Error updating call log:', err)
    })
  }
}

function showNoteWindow() {
  showNoteModal.value = true
}

function showTaskWindow() {
  showTaskModal.value = true
}

async function updateNote(_note, insert_mode = false) {
  note.value = _note
  if (insert_mode && _note.name && currentCallId.value) {
    try {
      await call('crm.integrations.api.add_note_to_call_log', {
        call_sid: currentCallId.value,
        note: _note,
      })
      toast.success(__('Note added to call log'))
    } catch (err) {
      toast.error(__('Failed to add note'))
      console.error('Error adding note:', err)
    }
  }
}

async function updateTask(_task, insert_mode = false) {
  task.value = _task
  if (insert_mode && _task.name && currentCallId.value) {
    try {
      await call('crm.integrations.api.add_task_to_call_log', {
        call_sid: currentCallId.value,
        task: _task,
      })
      toast.success(__('Task added to call log'))
    } catch (err) {
      toast.error(__('Failed to add task'))
      console.error('Error adding task:', err)
    }
  }
}

function setup() {
  // Listen for real-time call updates from server
  if (window.$socket) {
    window.$socket.on('tata_tele_call', (data) => {
      callData.value = data
      console.log('Tata Tele Call Update:', data)

      const status = data.status || data.call_status
      if (status) {
        const statusMap = {
          initiated: 'Calling...',
          ringing: 'Ringing...',
          connected: 'Connected',
          active: 'In progress',
          completed: 'Call ended',
          ended: 'Call ended',
          failed: 'Call failed',
          no_answer: 'No answer',
          busy: 'Busy',
          cancelled: 'Cancelled',
        }
        callStatus.value = statusMap[status] || status
      }
    })
  }
}

setup()

// Export makeOutgoingCall and setup for external use
defineExpose({
  makeOutgoingCall,
  setup,
  loading,
})
</script>

<style scoped>
/* Add any additional styles if needed */
</style>
