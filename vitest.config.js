import { defineConfig } from "vitest/config";
import path from "path";

export default defineConfig({
  test: {
    include: ["src/**/*.{test,spec}.{js,ts}"],
    environment: "jsdom",
    setupFiles: ["./src/lib/tests/setup.js"],
    globals: true,
  },
  resolve: {
    alias: {
      $lib: path.resolve(__dirname, "./src/lib"),
      $app: path.resolve(__dirname, "./src"),
      "$app/environment": path.resolve(
        __dirname,
        "./src/lib/tests/mocks/$app/environment.js",
      ),
    },
  },
});
