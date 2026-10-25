<template>
  <form
    class="registration-form"
    @submit="onSubmit"
  >
    <h2 class="registration-form__title">Регистрация</h2>

    <PhotoSelect
      v-model="photo"
      class="registration-form__photo"
    />

    <div class="registration-form__fields">
      <BaseInput
        id="registration-last-name"
        v-model="lastName"
        name="last_name"
        placeholder="Фамилия"
        required
      />
      <BaseInput
        id="registration-first-name"
        v-model="firstName"
        name="first_name"
        placeholder="Имя"
        required
      />
      <BaseInput
        id="registration-middle-name"
        v-model="middleName"
        name="middle_name"
        placeholder="Отчество"
        optional
      />
      <BaseInput
        id="registration-group"
        v-model="group"
        name="group"
        placeholder="Номер группы"
        description="(формат 261-321)"
        required
      />
      <hr class="registration-form__divider" />
      <BaseInput
        id="registration-email"
        v-model="email"
        name="email"
        type="email"
        placeholder="Адрес электронной почты"
        required
      />
      <BaseInput
        id="registration-password"
        v-model="password"
        name="password"
        type="password"
        placeholder="Придумайте пароль"
        required
      />
    </div>

    <p class="registration-form__note">* - необязательное поле</p>

    <BaseBtn
      :type="BtnType.SUBMIT"
      :disabled="!meta.valid || isSubmitting"
    >
      Зарегистрироваться
    </BaseBtn>
  </form>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useForm } from 'vee-validate';
import { toTypedSchema } from '@vee-validate/zod';
import { toast } from 'vue3-toastify';

import { registerSchema, userApi, type User } from '@/modules/user';

import { getErrorMessage } from '@/shared/api/client';
import { BaseBtn, BaseInput, BtnType, PhotoSelect } from '@/shared/ui';

const emit = defineEmits<{
  registered: [user: User];
}>();

const { defineField, handleSubmit, meta, isSubmitting } = useForm({
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

const photo = ref<File | null>(null);

const onSubmit = handleSubmit(async (values) => {
  try {
    emit('registered', await userApi.register({ ...values, photo: photo.value }));
  } catch (error) {
    toast.error(getErrorMessage(error, 'Не удалось зарегистрироваться'));
  }
});
</script>

<style lang="scss" scoped>
.registration-form {
  display: flex;
  flex-direction: column;
  gap: 10px;

  width: 100%;

  &__title {
    margin-bottom: 13px;

    font-family: 'Montserrat', sans-serif;
    font-size: var(--font-size-xl);
    line-height: 1.2;
    font-weight: 300;
    text-align: center;
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
    margin-bottom: 9px;

    border: none;
    border-top: 1px solid var(--color-pink-600);
  }

  &__note {
    margin-top: 10px;

    font-size: 1rem;
    line-height: 1.2;
    color: var(--color-pink-600);
  }
}
</style>
