<template>
  <div>
    <AuthForm
      v-if="openedForm === FormType.AUTH"
      @open-registration="openedForm = FormType.REGISTRATION"
    />
    <RegistrationForm
      v-else-if="openedForm === FormType.REGISTRATION"
      @open-auth="openedForm = FormType.AUTH"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

import AuthForm from './AuthForm.vue';
import RegistrationForm from './RegistrationForm.vue';

enum FormType {
  AUTH = 'auth',
  REGISTRATION = 'registration',
}

const openedForm = ref<FormType>(FormType.AUTH);
</script>
