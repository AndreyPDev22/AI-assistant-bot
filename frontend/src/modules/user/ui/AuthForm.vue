<template>
  <div class="auth-form">
    <h2 class="auth-form__title">{{ $t('auth.authForm.title') }}</h2>
    <BaseBtn
      class="auth-form__euz"
      :as="'a'"
      :variant="BtnVariant.OUTLINE"
    >
      {{ $t('auth.authForm.euz') }}
    </BaseBtn>
    <p class="auth-form__divider">{{ $t('auth.authForm.or') }}</p>
    <form
      class="auth-form__fields"
      @submit="onSubmit"
    >
      <BaseInput
        id="email"
        v-model="email"
        name="email"
        type="email"
        :placeholder="$t('auth.authForm.fields.email.placeholder')"
        :error-text="errors.email"
        :size="InputSize.LG"
      />
      <BaseInput
        id="password"
        v-model="password"
        name="password"
        type="password"
        :placeholder="$t('auth.authForm.fields.password.placeholder')"
        :error-text="errors.password"
        :size="InputSize.LG"
      />
      <div class="auth-form__buttons">
        <BaseBtn
          class="auth-form__login"
          :type="BtnType.SUBMIT"
          :disabled="!meta.valid || isSubmitting"
        >
          {{ $t('auth.login') }}
        </BaseBtn>
        <BaseBtn
          class="auth-form__register"
          :variant="BtnVariant.OUTLINE"
          @click="$emit('openRegistration')"
        >
          {{ $t('auth.register') }}
        </BaseBtn>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { useForm } from 'vee-validate';
import { toast } from 'vue3-toastify';

import { toTypedSchema } from '@vee-validate/zod';

import { BaseBtn, BaseInput, BtnType, BtnVariant, InputSize } from '@/shared/ui';
import { getErrorMessage } from '@/shared/api/client';

import { loginSchema } from './../model/loginSchema';
import { useUserStore } from './../model/userStore';

defineEmits<{
  openRegistration: [];
}>();

const { defineField, handleSubmit, meta, isSubmitting, errors } = useForm({
  validationSchema: toTypedSchema(loginSchema),
  initialValues: {
    email: '',
    password: '',
  },
});
const [email] = defineField('email');
const [password] = defineField('password');

const userStore = useUserStore();

const onSubmit = handleSubmit(async (values) => {
  try {
    await userStore.login(values);
  } catch (error) {
    toast.error(getErrorMessage(error, 'Не удалось зарегистрироваться'));
    return;
  }
});
</script>

<style lang="scss" scoped>
@use '@/styles/breakpoints' as *;

.auth-form {
  &__title {
    font-family: 'Montserrat';
    font-size: var(--font-size-xl);
    text-align: center;
    font-weight: 300;

    @include tablet {
      font-size: var(--font-size-lg);
    }
  }

  &__divider {
    position: relative;
    margin-block: 10px;

    text-align: center;
    color: var(--color-pink-600);

    &::before,
    &::after {
      position: absolute;
      content: '';
      left: 0;
      right: calc(50% + 3rem);
      top: 6px;

      border: 1px solid var(--color-pink-600);
    }

    &::after {
      left: calc(50% + 3rem);
      right: 0;
    }
  }

  &__euz {
    margin-top: 30px;
  }

  &__fields,
  &__buttons {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
}
</style>
