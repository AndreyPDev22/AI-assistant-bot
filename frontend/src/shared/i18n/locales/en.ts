export default {
  chats: {
    enterRequest: 'Enter your request...',
    createChat: 'New chat',
    addToFavorite: 'Add chat to favorites',
    deleteFromFavorite: 'Remove chat from favorites',
    deleteChat: 'Delete chat',
    chatGroups: {
      favorite: '♡ Favorites',
      today: 'Today',
      yesterday: 'Yesterday',
      lastWeek: 'Last week',
      lastMonth: 'Last month',
      lastYear: 'Last year',
      other: 'Earlier',
    },
  },
  auth: {
    title: 'Authorization',
    login: 'Login',
    register: 'Sign up',
    logout: 'Log out',
    notRequiredField: 'Optional field',
    authForm: {
      title: 'Log in or register',
      euz: 'Continue with the help of the EEU',
      or: 'Or',
      fields: {
        email: {
          placeholder: 'Enter your email',
          error: 'Invalid email address',
        },
        password: {
          placeholder: 'Enter your password',
          error: 'Please enter your password',
        },
      },
    },
    registrationForm: {
      title: 'Registration',
      fields: {
        lastName: {
          placeholder: 'Last name',
          error: 'Please enter your last name',
        },
        firstName: {
          placeholder: 'First name',
          error: 'Please enter your first name',
        },
        middleName: {
          placeholder: 'Middle name',
        },
        group: {
          placeholder: 'Group number',
          error: 'Invalid group number format',
          description: '(format 261-321)',
        },
        email: {
          placeholder: 'Enter your email',
          error: 'Invalid email address',
        },
        password: {
          placeholder: 'Enter your password',
          error: 'Must be at least 8 characters',
        },
      },
    },
  },
  profile: {
    language: 'Language',
    theme: 'Theme',
    notifications: 'Notifications',
    languages: {
      ru: 'Russian',
      en: 'English',
      zh: 'Chinese',
    },
  },
};
