# Coding standards and repository structure

[Documentation index](README.md)

## Formatting ownership

Each file type has one formatter. Biome checks code quality; it does not format files.

| Files                                                      | Formatter                       | Rules                                                                                                          |
| ---------------------------------------------------------- | ------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| JavaScript, TypeScript, CSS, HTML and hand-maintained JSON | Prettier                        | Four spaces, 100-column target, LF; JavaScript uses single quotes, optional semicolons and ES5 trailing commas |
| Svelte components, including scripts, markup and styles    | Prettier with the Svelte plugin | The same rules; keep the existing script/markup/style order and do not indent script/style contents            |
| Markdown                                                   | Prettier                        | Preserve prose wrapping and fenced code examples; retain meaningful hard-break spaces                          |
| YAML, including GitHub workflows                           | Prettier                        | Two spaces; preserve embedded shell scripts                                                                    |
| Bash and the Git commit hook                               | Prettier with the shell plugin  | Four spaces and LF; format without simplifying shell syntax                                                    |
| Python under `scripts/`                                    | Ruff                            | Python 3.10 syntax, four spaces, 100-column target, double quotes and LF                                       |

Line width is a formatting target, not a promise that URLs, strings and comments always fit. Do not wrap strings or alter behavior just to satisfy the target.

`package.json` uses two spaces to match npm's manifest and lockfile output.

The executable settings are [.prettierrc.json](../.prettierrc.json), [ruff.toml](../ruff.toml) and [biome.json](../biome.json). [.editorconfig](../.editorconfig) supplies editor defaults and [.gitattributes](../.gitattributes) defines LF checkout conventions for text files. Binary assets remain binary.

[.prettierignore](../.prettierignore) excludes generated snapshots, lockfiles, build output, dependencies, local tool state and bundled assets/licenses. Producers own generated data formatting. Small declarative files such as TOML, EditorConfig and Git attributes are maintained directly using the text conventions above; they are not passed through an unrelated formatter.

Do not add overlapping formatter configurations or broad suppressions to make a check pass. Fix the source or explain a narrow exception in the relevant configuration. Python lint currently selects error and Pyflakes rules; formatting does not imply that every optional style rule is enabled.

## Commands and enforcement

Run from the repository root with Linux Node/npm and the project Python environment.

| Task                                                      | Command                       |
| --------------------------------------------------------- | ----------------------------- |
| Format all maintained code and documentation              | `npm run format`              |
| Check formatting without writing files                    | `npm run format:check`        |
| Format web code, documentation and shell files            | `npm run format:code`         |
| Check those files without writing                         | `npm run format:code:check`   |
| Format Python                                             | `npm run format:python`       |
| Check Python formatting without writing                   | `npm run format:python:check` |
| Run formatting, lint, documentation, type and unit checks | `npm run validate`            |

The [pre-commit hook](../.husky/pre-commit) runs the staged-file tasks in [package.json](../package.json). Prettier formats staged web/docs/shell files; Ruff formats and lints staged Python. Biome lints matching source files. Install dependencies before committing; bypassing the hook does not bypass CI.

The [Verify workflow](../.github/workflows/verify.yml) checks Prettier formatting in the frontend job and Ruff formatting in the Python job, alongside the existing validation gates. These checks fail on formatting drift rather than changing files in CI.

## File placement and naming

| Location                   | Responsibility                                                                                                     |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `src/routes/`              | SvelteKit routes, page loads and endpoint adapters; keep reusable logic in the library                             |
| `src/lib/components/`      | UI components grouped by domain, with shared controls under `ui/`; use PascalCase component names                  |
| `src/lib/stores/`          | Shared reactive state and refresh coordination                                                                     |
| `src/lib/services/`        | Data-source access and snapshot loading                                                                            |
| `src/lib/server/`          | Server/build-only code; never import it into browser components                                                    |
| `src/lib/utils/`           | Focused reusable helpers without UI state                                                                          |
| `src/lib/tests/`           | Vitest tests named `*.test.js` or `*.test.ts`, including matching domain subdirectories                            |
| `scripts/data_collection/` | Python collectors, validators and shared collection utilities; use snake_case Python modules and `test_*.py` tests |
| `scripts/prebuild/`        | Node build-time enrichment; retain `.cjs` for CommonJS entry points                                                |
| `scripts/`                 | Cross-pipeline commands, validation and development tools; use descriptive kebab-case JavaScript filenames         |
| `docs/`                    | Maintained engineering guides linked from the documentation index                                                  |
| `static/data/`             | Published snapshots, written by their documented collectors                                                        |
| Repository root            | Shared tool configuration and project manifests                                                                    |

Match the existing naming convention within a module. These rules guide new files; formatting work is not a reason to rename existing files or move modules. Do not create another snapshot tree under a script directory or promote experiments into the production pipeline without wiring and documenting the entry point.

Keep formatting-only changes separate from behavior changes. Use [Architecture](ARCHITECTURE.md) for module boundaries, [Data pipeline](DATA_PIPELINE.md) for output ownership and [Testing](TESTING.md) for validation scope. Add new tests to the configured test locations and verify that Git actually tracks them; ignored local diagnostics are not CI coverage.

## Tool references

- [Prettier configuration](https://prettier.io/docs/configuration) and [ignore rules](https://prettier.io/docs/ignore)
- [Svelte formatter options](https://github.com/sveltejs/prettier-plugin-svelte)
- [Shell formatter options](https://github.com/un-ts/prettier/tree/master/packages/sh)
- [Ruff formatting](https://docs.astral.sh/ruff/formatter/)
