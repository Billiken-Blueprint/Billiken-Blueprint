This file documents repository-specific conventions and quick actionable guidance so an AI coding assistant can be immediately productive in this Angular + TypeScript project.

Keep this short and concrete — reference the listed files when you need examples.

Key repo facts
- Project root: TypeScript Angular app generated with Angular CLI (see `angular.json`).
- Source: `src/` (components under `src/app/*`); static assets in `public/`.
- Build/test: npm scripts defined in `package.json` (see "scripts").

Useful commands (from `package.json`)
- Start dev server: `npm run start` (runs `ng serve --host 0.0.0.0`).
- Production build: `npm run build` (runs `ng build`).
- Watch (dev build): `npm run watch` (runs `ng build --watch --configuration development`).
- Unit tests: `npm run test` (runs `ng test`, uses Karma).

Serve configurations
- The Angular CLI `serve` target in `angular.json` defines `development`, `production`, and `dev-compose` configurations.
- To use the Docker/compose-friendly proxy, run the dev-compose configuration: `ng run web:serve:dev-compose` or `ng serve --configuration=dev-compose`.
- Proxy files: `proxy.conf.json` and `proxy.compose.conf.json` (used by the serve target).

Component and coding patterns (discoverable in `src/app`)
- Standalone components are used instead of NgModules. Components declare an `imports` array inside `@Component` to import other components/modules. Example: `src/app/app.ts` imports `RouterOutlet` and a `TopBanner` component.
- Use `inject()` rather than constructor injection for services and framework tokens. See `src/app/auth-service/auth-service.ts` and `src/app/register-page/register-page.ts`.
- Forms: prefer reactive forms. Components import `ReactiveFormsModule` inside `imports` (see `register-page.ts`).
- State: signals are used for local component state where present (see `src/app/app.ts`).

Auth & integration points
- Auth service: `src/app/auth-service/auth-service.ts`. Key behaviours:
  - Login/register POST to `/api/identity/token` and `/api/identity/register` with `application/x-www-form-urlencoded` payloads.
  - Access token stored in `localStorage` under the key `access_token`.
  - JWTs are decoded with `jwt-decode` to determine login status and payload.
- Auth interceptor: `src/app/auth-service/auth-interceptor.ts` — it reads `AuthService.getToken()` and, when present, clones requests to set the `Authorization: Bearer <token>` header.

Routing & files to update
- Routes live in `src/app/app.routes.ts` (add feature routes there). Components follow the pattern: `<feature>/{<feature>.ts, <feature>.html, <feature>.css, <feature>.spec.ts}`.

Testing & specs
- Unit tests use Karma/Jasmine and live next to implementation (`*.spec.ts`). Run `npm run test` to execute them.

Conventions and small gotchas
- Do not add `standalone: true` manually — components are standalone by pattern and the codebase expects `imports` arrays inside decorators.
- Use `inject()` in services/components for DI. Patterns exist across the repo (see `auth-service` and pages).
- When adding HTTP calls, prefer the existing `HttpParams` + `HttpHeaders` style for form-encoded requests if matching backend endpoints.
- Token lifecycle: setting/removing `access_token` in localStorage should also update any related BehaviorSubjects used for UI state (see `AuthService` for example).

Files to reference for examples
- `src/app/auth-service/auth-service.ts` — service patterns, BehaviorSubject usage, JWT handling.
- `src/app/auth-service/auth-interceptor.ts` — request interception example.
- `src/app/register-page/register-page.ts` — reactive-form component example and use of `inject()`.
- `src/app/app.ts` — top-level component showing `signal()` usage and `imports` usage.
- `angular.json` and `package.json` — build/serve/test configurations and available npm scripts.

If parts of this guidance are unclear or you want more examples (e.g., how to add a lazy-loaded feature, how to wire new API endpoints, or unit test patterns), tell me which area and I'll expand with exact code edits or examples.
