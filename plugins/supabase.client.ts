import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://ugqqlnlmubedxpsepvgz.supabase.co'
const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVncXFsbmxtdWJlZHhwc2Vwdmd6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEzNDIwNDYsImV4cCI6MjA2NjkxODA0Nn0.M615vk5VD3irW7yH4TRU5wY29HQRPIvtufARuzXDl8s'
const supabase = createClient(supabaseUrl, supabaseKey)

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.provide('supabase', supabase)
})