import assert from "node:assert/strict";
import { writeFile } from "node:fs/promises";
import { chromium } from "playwright-core";

const BASE = "http://127.0.0.1:7718";
const ID = "01KYEBZTV77TPMP5Q5E1DPQ9SG";
const OUT = ".omo/evidence";
const result = { verdict: "needs-fix", responsive: {}, interactions: {}, consoleErrors: [] };
async function api(path, init) {
  const response = await fetch(BASE + path, init);
  const body = await response.json();
  assert.equal(response.ok, true, path + ": " + JSON.stringify(body));
  return body;
}
async function count() { return (await api("/api/canvas/" + ID)).document.objects.length; }
const pixel = Buffer.from("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4z8DwHwAFgAI/ScLvaQAAAABJRU5ErkJggg==", "base64");
const browser = await chromium.launch({ executablePath: "/usr/bin/google-chrome", headless: true });
try {
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 }, colorScheme: "light" });
  await context.addInitScript(() => {
    localStorage.setItem("creative-hub-recent-colors", JSON.stringify(["#ffffff", "junk", 4, "#11223380"]));
    localStorage.setItem("creative-hub-theme", "light");
  });
  const page = await context.newPage();
  page.on("console", (m) => { if (m.type() === "error") result.consoleErrors.push(m.text()); });
  page.on("pageerror", (e) => result.consoleErrors.push(e.message));
  await page.goto(BASE + "/canvas/" + ID, { waitUntil: "networkidle" });
  await page.getByLabel("편집 캔버스").waitFor();
  assert.equal(await page.locator("html").getAttribute("data-theme"), "light");
  result.interactions.routedEditor = page.url().endsWith("/canvas/" + ID);

  const beforeShapes = await count();
  await page.getByRole("button", { name: "도형 패널" }).click();
  await page.getByRole("button", { name: "사각형", exact: true }).click();
  await page.getByRole("button", { name: "채우기", exact: true }).last().click();
  const hex = page.getByRole("dialog").getByRole("textbox");
  await hex.fill("#11223380"); await hex.blur();
  await page.getByRole("button", { name: "채우기", exact: true }).last().click();
  const recent = await page.evaluate(() => localStorage.getItem("creative-hub-recent-colors"));
  assert.match(recent ?? "", /#11223380/i);
  result.interactions.recentColorsAlphaAndStaleStorage = { recent, noJunk: !/junk/.test(recent ?? "") };
  for (const name of ["원", "삼각형", "다각형", "5각 별", "6각 별", "선", "화살표"]) await page.getByRole("button", { name, exact: true }).click();
  assert.ok((await count()) >= beforeShapes + 8);
  await page.getByRole("button", { name: "왼쪽 정렬" }).click();
  result.interactions.allShapesAndAlignment = true;

  await page.getByRole("button", { name: "그리기 패널" }).click();
  for (const name of ["펜", "형광펜", "지우개"]) {
    await page.getByRole("button", { name, exact: true }).click();
    assert.equal(await page.getByRole("button", { name, exact: true }).getAttribute("aria-pressed"), "true");
  }
  await page.getByRole("button", { name: "펜", exact: true }).click();
  const upper = page.locator("canvas.upper-canvas");
  const box = await upper.boundingBox(); assert.ok(box);
  await page.mouse.move(box.x + 200, box.y + 200); await page.mouse.down();
  await page.mouse.move(box.x + 250, box.y + 240, { steps: 4 }); await page.mouse.up();
  result.interactions.drawingControls = true;

  await page.getByRole("button", { name: "에셋 패널" }).click();
  await page.locator('input[type="file"]').setInputFiles({ name: "task6-verify.png", mimeType: "image/png", buffer: pixel });
  await page.waitForTimeout(500); result.interactions.uploadControl = true;

  await page.getByRole("button", { name: "텍스트 패널" }).click();
  await page.getByRole("button", { name: /제목 추가/ }).click(); await page.waitForTimeout(150);
  const beforeTextShortcut = await count();
  await page.mouse.dblclick(box.x + 125, box.y + 105); await page.keyboard.press("Control+d"); await page.waitForTimeout(100);
  assert.equal(await count(), beforeTextShortcut, "Fabric text editing must suppress Ctrl+D");
  await page.keyboard.press("Escape"); result.interactions.fabricTextShortcutSuppressed = true;

  await page.getByRole("button", { name: "도형 패널" }).click();
  await page.getByRole("button", { name: "사각형", exact: true }).click();
  const beforeInputShortcut = await count();
  await page.getByLabel("X 위치").first().focus(); await page.keyboard.press("Control+d"); await page.waitForTimeout(100);
  assert.equal(await count(), beforeInputShortcut, "input must suppress Ctrl+D");
  result.interactions.inputShortcutSuppressed = true;

  await upper.click({ position: { x: 150, y: 150 } });
  const beforeD = await count(); await page.keyboard.press("Control+d"); await page.waitForTimeout(150);
  const afterD = await count(); assert.equal(afterD, beforeD + 1, "canvas Ctrl+D must duplicate exactly once");
  await page.locator("[aria-label='캔버스 작업 영역']").evaluate((n) => n.dispatchEvent(new KeyboardEvent("keydown", { key: "d", ctrlKey: true, repeat: true, bubbles: true, cancelable: true })));
  await page.waitForTimeout(100); assert.equal(await count(), afterD, "repeat must not duplicate");
  await page.keyboard.press("Control+a"); await page.keyboard.press("Control+g"); await page.waitForTimeout(100);
  assert.ok(await page.getByRole("button", { name: "그룹 해제" }).isVisible());
  await page.keyboard.press("Control+Shift+g"); await page.waitForTimeout(100);
  assert.ok(await page.getByRole("button", { name: "그룹화" }).isVisible());
  await page.keyboard.press("Control+c"); const beforePaste = await count(); await page.keyboard.press("Control+v"); await page.waitForTimeout(150);
  assert.ok((await count()) > beforePaste);
  result.interactions.canvasShortcutRepeatGroupUngroupCopyPaste = true;

  await page.getByLabel("선택 도구").click();
  await page.getByRole("button", { name: "캔버스 배경", exact: true }).click();
  const bgHex = page.getByRole("dialog").getByRole("textbox"); await bgHex.fill("#22334480"); await bgHex.blur();
  await page.getByRole("button", { name: "캔버스 배경", exact: true }).click();
  result.interactions.backgroundControl = true;

  const zoom = page.locator("output").filter({ hasText: /%/ }).last();
  const beforeWheel = await zoom.textContent(); await upper.dispatchEvent("wheel", { deltaY: -120, bubbles: true, cancelable: true }); await page.waitForTimeout(100);
  assert.notEqual(await zoom.textContent(), beforeWheel, "wheel should change zoom");
  const beforePan = await page.screenshot();
  await upper.click({ position: { x: 250, y: 250 } }); await page.keyboard.down("Space");
  await page.mouse.move(box.x + 250, box.y + 250); await page.mouse.down(); await page.mouse.move(box.x + 330, box.y + 290, { steps: 4 }); await page.mouse.up(); await page.keyboard.up("Space");
  await page.waitForTimeout(100); assert.notDeepEqual(await page.screenshot(), beforePan, "Space-drag should visibly pan");
  await page.getByRole("button", { name: "화면에 맞춤" }).click();
  result.interactions.wheelZoomSpacePanFit = true;

  await page.getByRole("button", { name: "전체 화면" }).click(); await page.waitForFunction(() => document.fullscreenElement !== null);
  await page.keyboard.press("Escape"); await page.waitForFunction(() => document.fullscreenElement === null);
  result.interactions.fullscreenEscape = true;

  const theme = page.getByRole("button", { name: /테마:/ });
  assert.match(await theme.getAttribute("aria-label") ?? "", /라이트/);
  await theme.click(); assert.equal(await page.locator("html").getAttribute("data-theme"), "dark");
  await theme.click(); assert.equal(await page.locator("html").getAttribute("data-theme"), null);
  await theme.click(); assert.equal(await page.locator("html").getAttribute("data-theme"), "light");
  await theme.click(); assert.equal(await page.locator("html").getAttribute("data-theme"), "dark");
  await page.reload({ waitUntil: "networkidle" }); await page.getByLabel("편집 캔버스").waitFor();
  assert.equal(await page.locator("html").getAttribute("data-theme"), "dark");
  result.interactions.threeStateThemePersisted = true;

  await page.getByRole("button", { name: "저장" }).click(); await page.getByText("저장됨").waitFor();
  const saved = await api("/api/canvas/" + ID);
  assert.ok(saved.document.objects.some((o) => String(o.fill ?? "").toLowerCase() === "#11223380"));
  assert.equal(String(saved.document.background ?? "").toLowerCase(), "#22334480");
  result.interactions.serializedAlphaAndBackground = true;
  await page.screenshot({ path: OUT + "/task-6-adversarial-1280.png", fullPage: true }); await context.close();

  for (const width of [375, 768]) {
    const c = await browser.newContext({ viewport: { width, height: 844 }, colorScheme: "light" });
    await c.addInitScript(() => localStorage.setItem("creative-hub-theme", "dark"));
    const p = await c.newPage(); await p.goto(BASE + "/canvas/" + ID, { waitUntil: "networkidle" }); await p.getByLabel("편집 캔버스").waitFor();
    const m = await p.evaluate(() => ({ docScrollWidth: document.documentElement.scrollWidth, innerWidth: innerWidth, theme: document.documentElement.getAttribute("data-theme") }));
    assert.ok(m.docScrollWidth <= m.innerWidth, width + "px must not horizontal-overflow");
    if (width === 375) {
      await p.getByRole("button", { name: "도형 패널" }).click(); await p.getByRole("button", { name: "사각형", exact: true }).waitFor();
      m.mobileToolPanel = true; m.mobileTarget = await p.getByRole("button", { name: "사각형", exact: true }).evaluate((n) => { const r = n.getBoundingClientRect(); return { width: r.width, height: r.height }; });
      assert.ok(m.mobileTarget.height >= 44);
    }
    result.responsive[width] = m; await p.screenshot({ path: OUT + "/task-6-adversarial-" + width + ".png", fullPage: true }); await c.close();
  }
  assert.equal(result.consoleErrors.length, 0, result.consoleErrors.join(" | "));
  result.verdict = "confirmed";
} catch (error) { result.error = error instanceof Error ? error.stack : String(error); }
finally { await browser.close(); }
await writeFile(OUT + "/task-6-adversarial-result.json", JSON.stringify(result, null, 2));
console.log(JSON.stringify(result, null, 2));
if (result.verdict !== "confirmed") process.exitCode = 1;
