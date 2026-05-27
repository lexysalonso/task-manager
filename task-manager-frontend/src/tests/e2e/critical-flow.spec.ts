import { test, expect } from "@playwright/test";
import { randomBytes } from "crypto";

/** Generate a unique user for each test run so auth never collides. */
function uniqueUser() {
  const suffix = randomBytes(4).toString("hex");
  return {
    email: `e2e-${suffix}@test-${suffix}.com`,
    fullName: `E2E User ${suffix}`,
    password: "TestPass123!",
  };
}

const PROJ_NAME = "Proyecto E2E";
const PROJ_DESC = "Descripción del proyecto E2E";
const TASK_NAME = "Tarea de prueba E2E";

test.describe("Critical user flow", () => {
  let projectId: number;

  test("full flow: register → login → create project → tasks → archive → logout", async ({ page }) => {
    const user = uniqueUser();

    // ── 1. Register ──────────────────────────────────────────────
    await page.goto("/register");
    await page.getByLabel("Nombre completo").fill(user.fullName);
    await page.getByLabel("Correo electrónico").fill(user.email);
    await page.getByLabel("Contraseña", { exact: true }).fill(user.password);
    await page.getByLabel("Confirmar contraseña").fill(user.password);
    await page.getByRole("button", { name: "Crear cuenta" }).click();
    await page.waitForURL("/projects");
    await expect(page.getByRole("heading", { name: "Mis Proyectos" })).toBeVisible();

    // ── 2. Create a project ──────────────────────────────────────
    await page.getByRole("link", { name: /nuevo proyecto/i }).first().click();
    await page.waitForURL("/projects/new");

    await page.getByLabel("Nombre del proyecto").fill(PROJ_NAME);
    await page.getByLabel("Descripción").fill(PROJ_DESC);
    await page.getByRole("button", { name: "Crear Proyecto" }).click();
    await page.waitForURL(/\/projects\/\d+$/);

    const match = page.url().match(/\/projects\/(\d+)/);
    projectId = Number(match![1]);
    expect(projectId).toBeGreaterThan(0);

    // Verify we are on the project detail page
    await expect(page.getByRole("heading", { name: PROJ_NAME })).toBeVisible();

    // ── 3. Create task ──────────────────────────────────────────
    await page.getByRole("button", { name: /agregar tarea/i }).click();
    await page.getByLabel("Nombre de la tarea").fill(TASK_NAME);
    await page.getByRole("button", { name: "Crear Tarea" }).click();
    await expect(page.getByText(TASK_NAME)).toBeVisible();

    // ── 4. Change task status ───────────────────────────────────
    // Radix SelectTrigger renders as a button. Find it by its text content.
    await page.locator("button", { hasText: "Pendiente" }).first().click();
    await page.getByRole("option", { name: /en progreso/i }).click();
    await expect(page.getByText("En Progreso").first()).toBeVisible();

    // ── 5. Delete task ──────────────────────────────────────────
    await page.getByRole("button", { name: "Eliminar tarea" }).click();
    await page.getByRole("button", { name: /^Eliminar$/ }).click();
    await expect(page.getByText(TASK_NAME)).not.toBeVisible();

    // ── 6. Archive project ──────────────────────────────────────
    await page.getByRole("link", { name: /editar/i }).click();
    await page.waitForURL(`/projects/${projectId}/edit`);

    await page.locator("#is_archived").click();
    await page.getByRole("option", { name: "Archivado" }).click();
    await page.getByRole("button", { name: "Guardar Cambios" }).click();
    await page.waitForURL(`/projects/${projectId}`);

    await expect(page.getByRole("button", { name: /agregar tarea/i })).not.toBeVisible();
    await expect(page.getByText(/proyecto está archivado/i)).toBeVisible();

    // ── 7. Logout ───────────────────────────────────────────────
    await page.getByRole("button", { name: "Menú de usuario" }).click();
    await page.getByRole("menuitem", { name: /cerrar sesión/i }).click();
    await page.waitForURL("/login");
    await expect(page.getByText("Bienvenido de nuevo")).toBeVisible();
  });
});
