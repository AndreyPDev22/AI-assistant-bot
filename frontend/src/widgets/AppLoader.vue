<template>
  <div
    class="app-loader"
    role="status"
    aria-label="Загрузка"
  >
    <img
      class="app-loader__icon"
      src="@/shared/assets/star.svg"
      alt=""
    />
  </div>
</template>

<style lang="scss" scoped>
.app-loader {
  position: fixed;
  inset: 0;
  z-index: 100;

  display: flex;
  align-items: center;
  justify-content: center;

  background-color: var(--color-pink-50);

  &__icon {
    width: 120px;
    height: 120px;
  }
}
</style>
