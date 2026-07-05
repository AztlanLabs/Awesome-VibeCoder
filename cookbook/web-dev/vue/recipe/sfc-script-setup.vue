<script setup lang="ts">
import {
  computed,
  inject,
  onMounted,
  provide,
  ref,
  useTemplateRef,
  watchEffect,
  type InjectionKey,
  type Ref,
} from 'vue';

type Theme = 'light' | 'dark';

const themeKey: InjectionKey<Ref<Theme>> = Symbol('theme');

provide(themeKey, ref<Theme>('dark'));

const props = defineProps<{ initial?: number; label: string }>();
const emit = defineEmits<{ 'update:count': [value: number]; submit: [] }>();
const count = defineModel<number>('count', { default: props.initial ?? 0 });
const theme = inject(themeKey, ref<Theme>('light'));

const inputEl = useTemplateRef<HTMLInputElement>('inputEl');
onMounted(() => inputEl.value?.focus());

const parity = computed(() => (count.value % 2 === 0 ? 'even' : 'odd'));

watchEffect(() => {
  if (count.value > 0) emit('update:count', count.value);
});

function increment(): void {
  count.value += 1;
}

function reset(): void {
  count.value = 0;
  emit('submit');
}

defineExpose({ reset, increment });
</script>

<template>
  <fieldset :data-theme="theme">
    <legend>{{ label }}</legend>
    <input ref="inputEl" v-model.number="count" type="number" />
    <p>Value: {{ count }} ({{ parity }})</p>
    <button type="button" @click="increment">+</button>
    <button type="button" @click="reset">Reset</button>
  </fieldset>
</template>