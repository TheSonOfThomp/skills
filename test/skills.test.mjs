import { test } from "node:test";
import assert from "node:assert/strict";
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";

const root = new URL("../skills/", import.meta.url).pathname;
const skills = readdirSync(root).filter((name) => statSync(join(root, name)).isDirectory());

function frontmatter(name) {
  const text = readFileSync(join(root, name, "SKILL.md"), "utf8");
  const match = text.match(/^---\n([\s\S]*?)\n---\n/);
  assert.ok(match, `${name}: SKILL.md has no frontmatter`);
  const field = (key) => match[1].match(new RegExp(`^${key}:\\s*(.+)$`, "m"))?.[1].trim().replace(/^"|"$/g, "");
  return { name: field("name"), description: field("description") };
}

function files(dir) {
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) =>
    entry.isDirectory() ? files(join(dir, entry.name)) : [join(dir, entry.name)],
  );
}

test("every skill has a valid name and description", () => {
  assert.ok(skills.length > 0);
  for (const dir of skills) {
    const { name, description } = frontmatter(dir);
    assert.equal(name, dir, `${dir}: name must match its directory`);
    assert.match(name, /^[a-z0-9]+(-[a-z0-9]+)*$/, `${dir}: invalid name`);
    assert.ok(name.length <= 64, `${dir}: name is longer than 64 characters`);
    assert.ok(description, `${dir}: missing description`);
    assert.ok(description.length <= 1024, `${dir}: description is longer than 1024 characters`);
  }
});

test("no skill contains machine-specific paths", () => {
  for (const file of files(root)) {
    const text = readFileSync(file, "utf8");
    assert.doesNotMatch(text, /(^|[\s"'`(])\/(Users|home)\/[a-z]/m, `${file}: contains a home directory path`);
    assert.doesNotMatch(text, /Mobile Documents|iCloud~/, `${file}: contains an iCloud path`);
  }
});
