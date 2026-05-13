#!/usr/bin/env node
/**
 * Migration runner — hanya butuh Node.js + pg package.
 * Usage:
 *   node scripts/migrate.js up
 *   node scripts/migrate.js down
 *   node scripts/migrate.js seed
 *   node scripts/migrate.js reset
 */

const fs = require("fs");
const path = require("path");
const { Client } = require("pg");

function loadEnv() {
  const envPath = path.join(__dirname, "..", ".env");
  if (!fs.existsSync(envPath)) return;
  for (const line of fs.readFileSync(envPath, "utf-8").split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const eq = trimmed.indexOf("=");
    if (eq === -1) continue;
    const key = trimmed.slice(0, eq).trim();
    const val = trimmed.slice(eq + 1).trim();
    if (!process.env[key]) process.env[key] = val;
  }
}

async function runSqlFile(client, filePath) {
  const sql = fs.readFileSync(filePath, "utf-8");
  await client.query(sql);
  console.log(`  OK: ${path.basename(filePath)}`);
}

async function migrateUp(client) {
  const dir = path.join(__dirname, "..", "migrations");
  const files = fs.readdirSync(dir).filter((f) => f.endsWith(".up.sql")).sort();
  console.log("Running migrations UP...");
  for (const file of files) await runSqlFile(client, path.join(dir, file));
}

async function migrateDown(client) {
  const dir = path.join(__dirname, "..", "migrations");
  const files = fs.readdirSync(dir).filter((f) => f.endsWith(".down.sql")).sort().reverse();
  console.log("Running migrations DOWN...");
  for (const file of files) await runSqlFile(client, path.join(dir, file));
}

async function seed(client) {
  const dir = path.join(__dirname, "..", "seeds");
  const files = fs.readdirSync(dir).filter((f) => f.endsWith(".sql")).sort();
  console.log("Running seeds...");
  for (const file of files) await runSqlFile(client, path.join(dir, file));
}

async function main() {
  loadEnv();
  const cmd = process.argv[2];
  if (!["up", "down", "reset", "seed"].includes(cmd)) {
    console.error("Usage: node scripts/migrate.js [up|down|reset|seed]");
    process.exit(1);
  }

  const url = process.env.DATABASE_URL;
  if (!url) {
    console.error("ERROR: DATABASE_URL tidak diset di .env");
    process.exit(1);
  }

  const client = new Client({ connectionString: url });
  await client.connect();
  try {
    if (cmd === "up") await migrateUp(client);
    else if (cmd === "down") await migrateDown(client);
    else if (cmd === "seed") await seed(client);
    else if (cmd === "reset") { await migrateDown(client); await migrateUp(client); }
    console.log("Done.");
  } finally {
    await client.end();
  }
}

main().catch((err) => {
  console.error("Error:", err.message);
  process.exit(1);
});
