<template>
  <div class="auth-form">
    <h2 class="auth-form__title">Войти или зарегистрироваться</h2>
    <BaseBtn
      class="auth-form__euz"
      :as="'a'"
      :variant="BtnVariant.OUTLINE"
    >
      Продолжить с помощью ЕУЗ
    </BaseBtn>
    <p class="auth-form__divider">или</p>
    <form
      class="auth-form__fields"
      @submit="onSubmit"
    >
      <BaseInput
        id="email"
        v-model="email"
        name="email"
        type="email"
        placeholder="Введите почту"
        :error-text="errors.email"
        :size="InputSize.LG"
      />
      <BaseInput
        id="password"
        v-model="password"
        name="password"
        type="password"
        placeholder="Введите пароль"
        :error-text="errors.password"
        :size="InputSize.LG"
      />
      <div class="auth-form__buttons">
        <BaseBtn
          class="auth-form__login"
          :type="BtnType.SUBMIT"
          :disabled="!meta.valid || isSubmitting"
        >
          Войти
        </BaseBtn>
        <BaseBtn
          class="auth-form__register"
          :variant="BtnVariant.OUTLINE"
          @click="$emit('openRegistration')"
        >
          Зарегистрироваться
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
import { loginSchema, useAuthStore } from '@/modules/user';
import { getErrorMessage } from '@/shared/api/client';

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

const authStore = useAuthStore();

const onSubmit = handleSubmit(async (values) => {
  try {
    await authStore.login(values);
  } catch (error) {
    toast.error(getErrorMessage(error, 'Не удалось зарегистрироваться'));
    return;
  }
});
</script>

<style lang="scss" scoped>
.auth-form {
  &__title {
    font-family: 'Montserrat';
    font-size: var(--font-size-xl);
    text-align: center;
    font-weight: 300;
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
