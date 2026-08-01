import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import {
  cpSync,
  mkdtempSync,
  mkdirSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { basename, join, resolve } from "node:path";
import { pathToFileURL } from "node:url";
import test from "node:test";
import Database from "better-sqlite3";

test("Given a legacy placement schema without its ledger row, When migrations run, Then the placement migration is recorded without a duplicate-column failure", () => {
  // Given
  const directory = mkdtempSync(join(tmpdir(), "creative-hub-db-migration-"));
  const migrationsDirectory = join(directory, "migrations");
  const databasePath = join(directory, "hub.db");
  mkdirSync(migrationsDirectory);
  const migrationName = "0005_generation_placement.sql";
  cpSync(
    join(process.cwd(), "migrations", migrationName),
    join(migrationsDirectory, migrationName),
  );

  const database = new Database(databasePath);
  database.exec(`
    CREATE TABLE generation_result (
      id TEXT PRIMARY KEY,
      position_x REAL,
      position_y REAL
    )
  `);
  database.close();

  try {
    // When
    execFileSync(
      process.execPath,
      [
        "--experimental-strip-types",
        "--input-type=module",
        "--eval",
        `await import(${JSON.stringify(pathToFileURL(resolve("src/lib/db.ts")).href)});`,
      ],
      {
        cwd: process.cwd(),
        env: {
          ...process.env,
          CREATIVE_HUB_ROOT: directory,
          DB_PATH: databasePath,
        },
        stdio: "pipe",
      },
    );

    // Then
    const migratedDatabase = new Database(databasePath, { readonly: true });
    const applied = migratedDatabase
      .prepare("SELECT filename FROM _migration")
      .all()
      .map(({ filename }) => filename);
    migratedDatabase.close();
    assert.deepEqual(applied, [migrationName]);
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});
