import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { existsSync, lstatSync, mkdirSync, mkdtempSync, readlinkSync, rmSync, symlinkSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const script = new URL("../skills/skills-sync/scripts/sync.mjs", import.meta.url).pathname;

function skill(dir, name) {
  mkdirSync(join(dir, name), { recursive: true });
  writeFileSync(join(dir, name, "SKILL.md"), `---\nname: ${name}\ndescription: test\n---\n`);
}

function setup() {
  const tmp = mkdtempSync(join(tmpdir(), "skills-sync-"));
  const repo = join(tmp, "repo");
  const vault = join(tmp, "vault");
  skill(repo, "alpha");
  skill(repo, "shared");
  skill(vault, "beta");
  skill(vault, "shared");
  mkdirSync(join(vault, "not-a-skill"));
  return { tmp, repo, vault };
}

const run = (...args) => execFileSync("node", [script, ...args], { encoding: "utf8" });

test("links skills from every source, earlier sources winning", (t) => {
  const { tmp, repo, vault } = setup();
  t.after(() => rmSync(tmp, { recursive: true, force: true }));
  const target = join(tmp, "target");

  const out = run("--source", repo, "--source", vault, "--target", target);

  assert.equal(readlinkSync(join(target, "alpha")), join(repo, "alpha"));
  assert.equal(readlinkSync(join(target, "beta")), join(vault, "beta"));
  assert.equal(readlinkSync(join(target, "shared")), join(repo, "shared"));
  assert.ok(!existsSync(join(target, "not-a-skill")));
  assert.match(out, /shadowed: shared/);
});

test("replaces a whole-directory symlink without touching what it pointed at", (t) => {
  const { tmp, repo, vault } = setup();
  t.after(() => rmSync(tmp, { recursive: true, force: true }));
  const target = join(tmp, "target");
  symlinkSync(vault, target);

  run("--source", repo, "--source", vault, "--target", target);

  assert.ok(lstatSync(target).isDirectory() && !lstatSync(target).isSymbolicLink());
  assert.ok(existsSync(join(vault, "beta", "SKILL.md")));
  assert.equal(readlinkSync(join(target, "beta")), join(vault, "beta"));
});

test("removes stale links into sources and leaves other content alone", (t) => {
  const { tmp, repo, vault } = setup();
  t.after(() => rmSync(tmp, { recursive: true, force: true }));
  const target = join(tmp, "target");
  mkdirSync(join(target, ".system"), { recursive: true });
  mkdirSync(join(target, "local-only"));
  symlinkSync(join(repo, "gone"), join(target, "gone"));
  symlinkSync(join(tmp, "elsewhere"), join(target, "alpha"));

  const out = run("--source", repo, "--source", vault, "--target", target);

  assert.ok(!existsSync(join(target, "gone")) && !lstatOrNull(join(target, "gone")));
  assert.ok(existsSync(join(target, ".system")));
  assert.ok(existsSync(join(target, "local-only")));
  // A broken link to somewhere outside the sources is relinked, since it can't be in use
  assert.equal(readlinkSync(join(target, "alpha")), join(repo, "alpha"));
  assert.doesNotMatch(out, /conflict/);
});

test("dry run changes nothing", (t) => {
  const { tmp, repo } = setup();
  t.after(() => rmSync(tmp, { recursive: true, force: true }));
  const target = join(tmp, "target");

  run("--source", repo, "--target", target, "--dry-run");

  assert.ok(!existsSync(target));
});

test("dry run of a whole-directory symlink reports what a real run would do", (t) => {
  const { tmp, repo, vault } = setup();
  t.after(() => rmSync(tmp, { recursive: true, force: true }));
  const target = join(tmp, "target");
  symlinkSync(vault, target);

  const out = run("--source", repo, "--source", vault, "--target", target, "--dry-run");

  assert.match(out, /linked 3, relinked 0, removed 0, unchanged 0/);
  assert.doesNotMatch(out, /conflict/);
  assert.ok(lstatSync(target).isSymbolicLink());
});

function lstatOrNull(path) {
  try {
    return lstatSync(path);
  } catch {
    return null;
  }
}
