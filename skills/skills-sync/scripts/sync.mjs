#!/usr/bin/env node
// Link every skill from one or more source directories into agent skill directories,
// one symlink per skill. Earlier sources win when two provide the same skill name.
//
// Usage: node sync.mjs [--source DIR]... [--target DIR]... [--dry-run]
//   --source  defaults to the skills/ directory this script lives in
//   --target  defaults to ~/.claude/skills and ~/.codex/skills
import { existsSync, lstatSync, mkdirSync, readdirSync, readlinkSync, realpathSync, statSync, symlinkSync, unlinkSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

const args = process.argv.slice(2);
const sources = [];
const targets = [];
let dryRun = false;
for (let i = 0; i < args.length; i++) {
  const arg = args[i];
  if (arg === "--source" || arg === "--target") {
    const value = args[++i];
    if (!value) fail(`${arg} needs a directory`);
    (arg === "--source" ? sources : targets).push(expand(value));
  } else if (arg === "--dry-run") {
    dryRun = true;
  } else if (arg === "--help" || arg === "-h") {
    console.log("Usage: node sync.mjs [--source DIR]... [--target DIR]... [--dry-run]");
    process.exit(0);
  } else {
    fail(`unknown argument: ${arg}`);
  }
}
if (sources.length === 0) sources.push(resolve(dirname(realpathSync(fileURLToPath(import.meta.url))), "../.."));
if (targets.length === 0) targets.push(join(homedir(), ".claude", "skills"), join(homedir(), ".codex", "skills"));

for (const s of sources) if (!existsSync(s)) fail(`source does not exist: ${s}`);
// Links use each source as given; matching also accepts its real path (e.g. /var vs /private/var on macOS)
const sourceRoots = sources;
const matchRoots = [...new Set(sources.flatMap((s) => [s, realpathSync(s)]))];

// name -> absolute skill directory, first source wins
const skills = new Map();
const shadowed = [];
for (const root of sourceRoots) {
  for (const name of readdirSync(root).sort()) {
    if (name.startsWith(".")) continue;
    const dir = join(root, name);
    if (!isDir(dir) || !existsSync(join(dir, "SKILL.md"))) continue;
    if (skills.has(name)) shadowed.push(`${name} (${dir} is shadowed by ${skills.get(name)})`);
    else skills.set(name, dir);
  }
}

const insideSource = (path) => matchRoots.some((root) => path === root || path.startsWith(root + sep));

for (const target of targets) {
  const report = { linked: 0, relinked: 0, removed: 0, unchanged: 0, conflicts: [] };
  const targetStat = lstatOrNull(target);
  if (targetStat?.isSymbolicLink()) {
    // A whole-directory symlink (the old layout) can only show one source; replace it with a real directory.
    console.log(`${target}: replacing directory symlink -> ${readlinkSync(target)}`);
    if (!dryRun) {
      unlinkSync(target);
      mkdirSync(target, { recursive: true });
    }
  } else if (!targetStat) {
    console.log(`${target}: creating directory`);
    if (!dryRun) mkdirSync(target, { recursive: true });
  } else if (!targetStat.isDirectory()) {
    console.log(`${target}: not a directory, skipping`);
    continue;
  }

  for (const [name, dir] of skills) {
    const link = join(target, name);
    const stat = lstatOrNull(link);
    if (!stat) {
      if (!dryRun) symlinkSync(dir, link);
      report.linked++;
    } else if (stat.isSymbolicLink()) {
      const current = resolve(dirname(link), readlinkSync(link));
      if (current === dir) {
        report.unchanged++;
      } else if (!existsSync(current) || insideSource(current)) {
        if (!dryRun) {
          unlinkSync(link);
          symlinkSync(dir, link);
        }
        report.relinked++;
      } else {
        report.conflicts.push(`${name} links to ${current}`);
      }
    } else {
      report.conflicts.push(`${name} is a real ${stat.isDirectory() ? "directory" : "file"}`);
    }
  }

  // Remove links to skills that no longer exist in any source; leave everything else alone.
  if (existsSync(target)) {
    for (const name of readdirSync(target)) {
      if (name.startsWith(".") || skills.has(name)) continue;
      const link = join(target, name);
      if (!lstatSync(link).isSymbolicLink()) continue;
      const current = resolve(dirname(link), readlinkSync(link));
      if (insideSource(current) || insideSource(resolve(current, ".."))) {
        if (!dryRun) unlinkSync(link);
        report.removed++;
      }
    }
  }

  const summary = `linked ${report.linked}, relinked ${report.relinked}, removed ${report.removed}, unchanged ${report.unchanged}`;
  console.log(`${target}: ${summary}${dryRun ? " (dry run)" : ""}`);
  for (const conflict of report.conflicts) console.log(`  conflict, left alone: ${conflict}`);
}
for (const line of shadowed) console.log(`shadowed: ${line}`);

function expand(path) {
  return resolve(path.startsWith("~/") ? join(homedir(), path.slice(2)) : path);
}

function isDir(path) {
  try {
    return statSync(path).isDirectory();
  } catch {
    return false;
  }
}

function lstatOrNull(path) {
  try {
    return lstatSync(path);
  } catch {
    return null;
  }
}

function fail(message) {
  process.stderr.write(`error: ${message}\n`);
  process.exit(1);
}
