import { cookies } from "next/headers";
import {
  createHmac,
  randomBytes,
  randomUUID,
  scryptSync,
  timingSafeEqual,
} from "node:crypto";
import { readSiteletDb, SiteletToken, SiteletUser, writeSiteletDb } from "./sitelet-store";

const SESSION_COOKIE = "sitelet_session";
const TOKEN_PREFIX = "stlt";

export type AuthUser = Pick<SiteletUser, "id" | "email" | "createdAt">;

export function hashPassword(password: string, salt = randomBytes(16).toString("hex")) {
  const hash = scryptSync(password, salt, 64).toString("hex");
  return { salt, hash };
}

export function verifyPassword(password: string, salt: string, expectedHash: string): boolean {
  const actual = Buffer.from(hashPassword(password, salt).hash, "hex");
  const expected = Buffer.from(expectedHash, "hex");
  return actual.length === expected.length && timingSafeEqual(actual, expected);
}

export function makeApiToken(): string {
  return `${TOKEN_PREFIX}_${randomBytes(32).toString("base64url")}`;
}

export function hashApiToken(token: string): string {
  return createHmac("sha256", authSecret()).update(token).digest("hex");
}

export async function createUser(email: string, password: string): Promise<SiteletUser> {
  const cleanEmail = normalizeEmail(email);
  validatePassword(password);

  const db = await readSiteletDb();
  if (db.users.some((user) => user.email === cleanEmail)) {
    throw new Error("An account already exists for this email.");
  }

  const passwordRecord = hashPassword(password);
  const user: SiteletUser = {
    id: randomUUID(),
    email: cleanEmail,
    passwordHash: passwordRecord.hash,
    passwordSalt: passwordRecord.salt,
    createdAt: new Date().toISOString(),
  };
  db.users.push(user);
  await writeSiteletDb(db);
  return user;
}

export async function authenticateUser(email: string, password: string): Promise<SiteletUser> {
  const db = await readSiteletDb();
  const user = db.users.find((candidate) => candidate.email === normalizeEmail(email));
  if (!user || !verifyPassword(password, user.passwordSalt, user.passwordHash)) {
    throw new Error("Invalid email or password.");
  }
  return user;
}

export async function createApiToken(userId: string, name: string) {
  const db = await readSiteletDb();
  const user = db.users.find((candidate) => candidate.id === userId);
  if (!user) {
    throw new Error("User not found.");
  }

  const token = makeApiToken();
  const record: SiteletToken = {
    id: randomUUID(),
    userId,
    name: sanitizeTokenName(name || "Hermes Agent"),
    prefix: token.slice(0, 12),
    tokenHash: hashApiToken(token),
    createdAt: new Date().toISOString(),
  };
  db.tokens.push(record);
  await writeSiteletDb(db);
  return { token, record: publicToken(record) };
}

export async function revokeApiToken(userId: string, tokenId: string): Promise<void> {
  const db = await readSiteletDb();
  db.tokens = db.tokens.filter((token) => !(token.userId === userId && token.id === tokenId));
  await writeSiteletDb(db);
}

export async function listApiTokens(userId: string) {
  const db = await readSiteletDb();
  return db.tokens
    .filter((token) => token.userId === userId)
    .sort((a, b) => b.createdAt.localeCompare(a.createdAt))
    .map(publicToken);
}

export async function requireBearerUser(request: Request): Promise<AuthUser> {
  const header = request.headers.get("authorization") || "";
  const match = header.match(/^Bearer\s+(.+)$/i);
  if (!match) {
    throw new AuthError("Missing bearer token.", 401);
  }

  const tokenValue = match[1].trim();
  const tokenHash = hashApiToken(tokenValue);
  const db = await readSiteletDb();
  const token = db.tokens.find((candidate) => candidate.tokenHash === tokenHash);
  if (!token) {
    throw new AuthError("Invalid bearer token.", 401);
  }

  const user = db.users.find((candidate) => candidate.id === token.userId);
  if (!user) {
    throw new AuthError("Token user no longer exists.", 401);
  }

  token.lastUsedAt = new Date().toISOString();
  await writeSiteletDb(db);
  return publicUser(user);
}

export async function getSessionUser(): Promise<AuthUser | null> {
  const cookieStore = await cookies();
  const raw = cookieStore.get(SESSION_COOKIE)?.value;
  if (!raw) {
    return null;
  }

  const userId = verifySession(raw);
  if (!userId) {
    return null;
  }

  const db = await readSiteletDb();
  const user = db.users.find((candidate) => candidate.id === userId);
  return user ? publicUser(user) : null;
}

export async function requireSessionUser(): Promise<AuthUser> {
  const user = await getSessionUser();
  if (!user) {
    throw new AuthError("Login required.", 401);
  }
  return user;
}

export async function setSessionCookie(userId: string): Promise<void> {
  const cookieStore = await cookies();
  cookieStore.set(SESSION_COOKIE, signSession(userId), {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 60 * 60 * 24 * 30,
  });
}

export async function clearSessionCookie(): Promise<void> {
  const cookieStore = await cookies();
  cookieStore.set(SESSION_COOKIE, "", {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 0,
  });
}

export class AuthError extends Error {
  constructor(message: string, public status = 401) {
    super(message);
  }
}

function signSession(userId: string): string {
  const payload = Buffer.from(JSON.stringify({ userId, issuedAt: Date.now() })).toString("base64url");
  const signature = createHmac("sha256", authSecret()).update(payload).digest("base64url");
  return `${payload}.${signature}`;
}

function verifySession(value: string): string | null {
  const [payload, signature] = value.split(".");
  if (!payload || !signature) {
    return null;
  }
  const expected = createHmac("sha256", authSecret()).update(payload).digest("base64url");
  const actualBuffer = Buffer.from(signature);
  const expectedBuffer = Buffer.from(expected);
  if (actualBuffer.length !== expectedBuffer.length || !timingSafeEqual(actualBuffer, expectedBuffer)) {
    return null;
  }

  try {
    const parsed = JSON.parse(Buffer.from(payload, "base64url").toString("utf8")) as {
      userId?: string;
      issuedAt?: number;
    };
    if (!parsed.userId || !parsed.issuedAt) {
      return null;
    }
    return parsed.userId;
  } catch {
    return null;
  }
}

function authSecret(): string {
  const secret = process.env.SITELET_AUTH_SECRET;
  if (secret && secret.length >= 32) {
    return secret;
  }
  if (process.env.NODE_ENV === "production") {
    throw new Error("SITELET_AUTH_SECRET must be set to at least 32 characters in production.");
  }
  return "dev-sitelet-secret-change-before-deploy";
}

function normalizeEmail(email: string): string {
  const cleanEmail = email.trim().toLowerCase();
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(cleanEmail)) {
    throw new Error("A valid email is required.");
  }
  return cleanEmail;
}

function validatePassword(password: string): void {
  if (password.length < 10) {
    throw new Error("Password must be at least 10 characters.");
  }
}

function sanitizeTokenName(value: string): string {
  return value.replace(/\s+/g, " ").trim().slice(0, 80) || "Hermes Agent";
}

function publicUser(user: SiteletUser): AuthUser {
  return {
    id: user.id,
    email: user.email,
    createdAt: user.createdAt,
  };
}

function publicToken(token: SiteletToken) {
  return {
    id: token.id,
    name: token.name,
    prefix: token.prefix,
    createdAt: token.createdAt,
    lastUsedAt: token.lastUsedAt || null,
  };
}
