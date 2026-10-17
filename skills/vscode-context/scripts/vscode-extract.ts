// Print the files currently open in VSCode for the workspace containing $PWD.
// Port of vscode_extract.py. Reads VSCode's per-window state.vscdb via sqlite3.
import { spawnSync } from "node:child_process";
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import { homedir } from "node:os";
import { join, relative } from "node:path";

const STORAGE_BASE = join(homedir(), "Library/Application Support/Code/User/workspaceStorage");

interface GridNode {
  type?: string;
  data?: unknown;
}

function gitRoot(): string {
  const r = spawnSync("git", ["rev-parse", "--show-toplevel"], { encoding: "utf8" });
  if (r.status === 0) {
    return r.stdout.trim();
  }
  return process.cwd();
}

function matchingStorageDirs(workspaceUri: string): string[] {
  const isRepoWorkspace = (d: { folder?: string; workspace?: string }): boolean => {
    const folder = d.folder ?? "";
    const workspace = d.workspace ?? "";
    if (folder === workspaceUri || folder.startsWith(`${workspaceUri}/`)) {
      return true;
    }
    if (workspace.startsWith(`${workspaceUri}/`)) {
      return true;
    }
    return false;
  };

  const dirs: string[] = [];
  let entries: string[];
  try {
    entries = readdirSync(STORAGE_BASE);
  } catch {
    return dirs;
  }
  for (const entry of entries) {
    const path = join(STORAGE_BASE, entry);
    const wf = join(path, "workspace.json");
    if (existsSync(wf) && statSync(wf).isFile()) {
      try {
        if (isRepoWorkspace(JSON.parse(readFileSync(wf, "utf8")))) {
          dirs.push(path);
        }
      } catch {
        // ignore malformed workspace.json
      }
    }
  }
  return dirs;
}

function extract(node: GridNode): string[] {
  const paths: string[] = [];
  if (node.type === "leaf") {
    const data = (node.data ?? {}) as { editors?: { value?: string }[] };
    for (const ed of data.editors ?? []) {
      try {
        const v = JSON.parse(ed.value ?? "{}") as { resourceJSON?: { fsPath?: string } };
        const p = v.resourceJSON?.fsPath;
        if (p) {
          paths.push(p);
        }
      } catch {
        // ignore unparseable editor value
      }
    }
  } else if (node.type === "branch") {
    for (const child of (node.data ?? []) as GridNode[]) {
      paths.push(...extract(child));
    }
  }
  return paths;
}

function main(): number {
  const root = gitRoot();
  const workspaceUri = `file://${root}`;
  const storageDirs = matchingStorageDirs(workspaceUri);
  if (storageDirs.length === 0) {
    console.log(`ERROR: No VSCode workspace storage found matching ${workspaceUri}`);
    return 1;
  }

  const seen = new Set<string>();
  const allPaths: string[] = [];
  for (const storageDir of storageDirs) {
    const db = join(storageDir, "state.vscdb");
    if (!existsSync(db) || !statSync(db).isFile()) {
      continue;
    }
    const r = spawnSync(
      "sqlite3",
      [db, "SELECT value FROM ItemTable WHERE key='memento/workbench.parts.editor';"],
      { encoding: "utf8" },
    );
    if (r.status !== 0) {
      continue;
    }
    const result = r.stdout.trim();
    if (!result) {
      continue;
    }
    const data = JSON.parse(result) as {
      "editorpart.state"?: { serializedGrid?: { root?: GridNode } };
    };
    const grid = data["editorpart.state"]?.serializedGrid ?? {};
    for (const p of extract(grid.root ?? {})) {
      if (!seen.has(p)) {
        seen.add(p);
        allPaths.push(p);
      }
    }
  }

  if (allPaths.length === 0) {
    console.log("No file paths found in open editor state.");
    return 0;
  }

  for (const p of allPaths) {
    const rel = relative(root, p);
    console.log(rel.startsWith("..") ? p : rel);
  }
  return 0;
}

process.exit(main());
