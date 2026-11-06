export default {
  chats: {
    enterRequest: 'Введите запрос...',
    createChat: 'Новый чат',
    addToFavorite: 'Добавить чат в избранное',
    deleteFromFavorite: 'Удалить чат из избранного',
    deleteChat: 'Удалить чат',
    chatGroups: {
      favorite: '♡ Избранное',
      today: 'Сегодня',
      yesterday: 'Вчера',
      lastWeek: 'За последнюю неделю',
      lastMonth: 'За последний месяц',
      lastYear: 'За последний год',
      other: 'Ранее',
    },
  },
  auth: {
    title: 'Авторизация',
    login: 'Войти',
    register: 'Зарегистрироваться',
    logout: 'Выйти из аккаунта',
    notRequiredField: 'Необязательное поле',
    authForm: {
      title: 'Войти или зарегистрироваться',
      euz: 'Продолжить с помощью ЕУЗ',
      or: 'Или',
      fields: {
        email: {
          placeholder: 'Введите почту',
          error: 'Некорректный адрес почты',
        },
        password: {
          placeholder: 'Введите пароль',
          error: 'Введите пароль',
        },
      },
    },
    registrationForm: {
      title: 'Регистрация',
      fields: {
        lastName: {
          placeholder: 'Фамилия',
          error: 'Укажите фамилию',
        },
        firstName: {
          placeholder: 'Имя',
          error: 'Укажите имя',
        },
        middleName: {
          placeholder: 'Отчество',
        },
        group: {
          placeholder: 'Имя',
          error: 'Номер группы в неверном формате',
          description: '(формат 261-321)',
        },
        email: {
          placeholder: 'Введите почту',
          error: 'Некорректный адрес почты',
        },
        password: {
          placeholder: 'Введите пароль',
          error: 'Не короче 8 символов',
        },
      },
    },
  },
  profile: {
    language: 'Язык',
    theme: 'Тема',
    notifications: 'Уведомления',
    languages: {
      ru: 'Русский',
      en: 'Английский',
      zh: 'Китайский',
    },
  },
};
