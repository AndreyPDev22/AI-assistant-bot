<template>
  <form
    class="registration-form"
    @submit="onSubmit"
  >
    <h2 class="registration-form__title">{{ $t('auth.registrationForm.title') }}</h2>

    <PhotoSelect
      v-model="photo"
      class="registration-form__photo"
    />

    <div class="registration-form__fields">
      <BaseInput
        id="registration-last-name"
        v-model="lastName"
        name="last_name"
        required
        :placeholder="$t('auth.registrationForm.fields.lastName.placeholder')"
        :error-text="errors.lastName"
      />
      <BaseInput
        id="registration-first-name"
        v-model="firstName"
        name="first_name"
        required
        :placeholder="$t('auth.registrationForm.fields.firstName.placeholder')"
        :error-text="errors.firstName"
      />
      <BaseInput
        id="registration-middle-name"
        v-model="middleName"
        name="middle_name"
        optional
        :placeholder="$t('auth.registrationForm.fields.middleName.placeholder')"
        :error-text="errors.middleName"
      />
      <BaseInput
        id="registration-group"
        v-model="group"
        name="group"
        required
        :placeholder="$t('auth.registrationForm.fields.group.placeholder')"
        :description="$t('auth.registrationForm.fields.group.description')"
        :error-text="errors.group"
      />
      <hr class="registration-form__divider" />
      <BaseInput
        id="registration-email"
        v-model="email"
        name="email"
        type="email"
        required
        :placeholder="$t('auth.registrationForm.fields.email.placeholder')"
        :error-text="errors.email"
      />
      <BaseInput
        id="registration-password"
        v-model="password"
        name="password"
        type="password"
        required
        :placeholder="$t('auth.registrationForm.fields.password.placeholder')"
        :error-text="errors.password"
      />
    </div>

    <p class="registration-form__note">* - {{ $t('auth.notRequiredField') }}</p>

    <BaseBtn
      :type="BtnType.SUBMIT"
      :disabled="!meta.valid || isSubmitting"
    >
      {{ $t('auth.register') }}
    </BaseBtn>
    <BaseBtn @click="$emit('openAuth')"> {{ $t('auth.login') }} </BaseBtn>
  </form>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useForm } from 'vee-validate';
import { toast } from 'vue3-toastify';
import { toTypedSchema } from '@vee-validate/zod';

import { getErrorMessage } from '@/shared/api/client';
import { BaseBtn, BaseInput, BtnType, PhotoSelect } from '@/shared/ui';

import { registerSchema } from '../model/registerSchema';
import { useUserStore } from '../model/userStore';

defineEmits<{
  openAuth: [];
}>();

const { defineField, handleSubmit, meta, isSubmitting, errors } = useForm({
  validationSchema: toTypedSchema(registerSchema),
  initialValues: {
    lastName: '',
    firstName: '',
    middleName: '',
    group: '',
    email: '',
    password: '',
  },
});

const [lastName] = defineField('lastName');
const [firstName] = defineField('firstName');
const [middleName] = defineField('middleName');
const [group] = defineField('group');
const [email] = defineField('email');
const [password] = defineField('password');

const userStore = useUserStore();

const photo = ref<File | null>(null);

const onSubmit = handleSubmit(async (values) => {
  try {
    await userStore.register({ ...values, photo: photo.value });
  } catch (error) {
    toast.error(getErrorMessage(error, 'Не удалось зарегистрироваться'));
  }
});
</script>

<style lang="scss" scoped>
@use '@/styles/breakpoints' as *;

.registration-form {
  display: flex;
  flex-direction: column;
  gap: 10px;

  width: 100%;

  &__title {
    margin-bottom: 10px;

    font-family: 'Montserrat', sans-serif;
    font-size: var(--font-size-xl);
    line-height: 1.2;
    font-weight: 300;
    text-align: center;

    @include tablet {
      font-size: var(--font-size-lg);
    }
  }

  &__photo {
    align-self: center;
    margin-bottom: 10px;
  }

  &__fields {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  &__divider {
    margin-bottom: 4px;

    border: none;
    border-top: 1px solid var(--color-pink-600);
  }

  &__note {
    margin-top: 2px;

    font-size: 1rem;
    line-height: 1.2;
    color: var(--color-pink-600);
  }
}
</style>
