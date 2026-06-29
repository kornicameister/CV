// @ts-check
import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
  output: 'static',
  outDir: './dist',
  site: 'https://kornicameister.github.io',
  base: '/CV',
});
