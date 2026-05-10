import { mkdir, readFile, readdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { createHash, randomUUID } from "node:crypto";

export type GeneratedPageInput = {
  title?: string;
  html: string;
  source?: string;
  userId?: string;
};

export type GeneratedPageRecord = {
  id: string;
  title: string;
  source: string;
  userId?: string;
  createdAt: string;
  html: string;
};

export type GeneratedPageSummary = Omit<GeneratedPageRecord, "html"> & {
  storageFile: string;
  htmlBytes: number;
};

export function generatedRoot(): string {
  return process.env.SITELET_GENERATED_DIR || path.join(process.cwd(), ".sitelet", "generated");
}

export async function saveGeneratedPage(input: GeneratedPageInput): Promise<GeneratedPageRecord> {
  const html = input.html.trim();
  if (!html) {
    throw new Error("Generated page HTML is required.");
  }

  const id = makeGeneratedId(html);
  const record: GeneratedPageRecord = {
    id,
    title: sanitizeTitle(input.title || "Generated Page"),
    source: sanitizeTitle(input.source || "sitelet"),
    userId: input.userId,
    createdAt: new Date().toISOString(),
    html: ensureDocument(html, input.title || "Generated Page"),
  };

  const root = generatedRoot();
  await mkdir(root, { recursive: true });
  await writeFile(path.join(root, `${id}.json`), JSON.stringify(record, null, 2), "utf8");
  return record;
}

export async function readGeneratedPage(id: string): Promise<GeneratedPageRecord> {
  const safeId = sanitizeId(id);
  if (!safeId) {
    throw new Error("Invalid generated page id.");
  }

  const raw = await readFile(path.join(generatedRoot(), `${safeId}.json`), "utf8");
  return JSON.parse(raw) as GeneratedPageRecord;
}

export async function listGeneratedPages(userId?: string): Promise<GeneratedPageSummary[]> {
  const root = generatedRoot();
  let names: string[];
  try {
    names = await readdir(root);
  } catch (error) {
    if (isNotFound(error)) {
      return [];
    }
    throw error;
  }

  const records = await Promise.all(
    names
      .filter((name) => name.endsWith(".json"))
      .map(async (name): Promise<GeneratedPageSummary | null> => {
        try {
          const storageFile = path.join(root, name);
          const raw = await readFile(storageFile, "utf8");
          const record = JSON.parse(raw) as GeneratedPageRecord;
          if (userId && record.userId && record.userId !== userId) {
            return null;
          }
          const { html, ...summary } = record;
          return {
            ...summary,
            storageFile,
            htmlBytes: Buffer.byteLength(html || "", "utf8"),
          };
        } catch {
          return null;
        }
      }),
  );

  return records
    .filter((record): record is GeneratedPageSummary => Boolean(record))
    .sort((a, b) => b.createdAt.localeCompare(a.createdAt));
}

function makeGeneratedId(html: string): string {
  const hash = createHash("sha256").update(html).digest("hex").slice(0, 10);
  return `${Date.now().toString(36)}-${hash}-${randomUUID().slice(0, 8)}`;
}

function sanitizeId(id: string): string {
  return id.replace(/[^a-zA-Z0-9._-]/g, "");
}

function isNotFound(error: unknown): boolean {
  return Boolean(error && typeof error === "object" && "code" in error && error.code === "ENOENT");
}

function sanitizeTitle(value: string): string {
  return value.replace(/\s+/g, " ").trim().slice(0, 120);
}

function ensureDocument(html: string, title: string): string {
  if (/<!doctype html/i.test(html) || /<html[\s>]/i.test(html)) {
    return html;
  }

  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${escapeHtml(title)}</title>
</head>
<body>
${html}
</body>
</html>`;
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
