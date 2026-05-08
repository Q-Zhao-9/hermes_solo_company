import { mkdir, readFile, rename, writeFile } from "node:fs/promises";
import path from "node:path";

export type SiteletUser = {
  id: string;
  email: string;
  passwordHash: string;
  passwordSalt: string;
  createdAt: string;
};

export type SiteletToken = {
  id: string;
  userId: string;
  name: string;
  prefix: string;
  tokenHash: string;
  createdAt: string;
  lastUsedAt?: string;
};

export type SiteletDb = {
  users: SiteletUser[];
  tokens: SiteletToken[];
};

const EMPTY_DB: SiteletDb = {
  users: [],
  tokens: [],
};

let writeQueue: Promise<void> = Promise.resolve();

export function siteletDataRoot(): string {
  return process.env.SITELET_DATA_DIR || path.join(process.cwd(), ".sitelet");
}

export function siteletDbPath(): string {
  return path.join(siteletDataRoot(), "sitelet-db.json");
}

export async function readSiteletDb(): Promise<SiteletDb> {
  try {
    const raw = await readFile(siteletDbPath(), "utf8");
    const parsed = JSON.parse(raw) as Partial<SiteletDb>;
    return {
      users: Array.isArray(parsed.users) ? parsed.users : [],
      tokens: Array.isArray(parsed.tokens) ? parsed.tokens : [],
    };
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") {
      return { ...EMPTY_DB, users: [], tokens: [] };
    }
    throw error;
  }
}

export async function writeSiteletDb(db: SiteletDb): Promise<void> {
  writeQueue = writeQueue.then(async () => {
    const root = siteletDataRoot();
    await mkdir(root, { recursive: true });
    const target = siteletDbPath();
    const tmp = `${target}.${process.pid}.${Date.now()}.tmp`;
    await writeFile(tmp, JSON.stringify(db, null, 2), "utf8");
    await rename(tmp, target);
  });
  return writeQueue;
}
