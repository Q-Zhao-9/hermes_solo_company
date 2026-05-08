"use client";

import { FormEvent, useState } from "react";

type AuthMode = "login" | "register";

export function AuthForm({ mode }: { mode: AuthMode }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [status, setStatus] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setStatus(mode === "login" ? "Signing in..." : "Creating account...");

    const response = await fetch(`/api/auth/${mode}`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const payload = await response.json();
    if (!response.ok || !payload.ok) {
      setStatus(payload.error || "Authentication failed.");
      return;
    }
    window.location.href = "/dashboard";
  }

  return (
    <form className="auth-form" onSubmit={submit}>
      <label htmlFor="email">Email</label>
      <input
        id="email"
        type="email"
        autoComplete="email"
        value={email}
        onChange={(event) => setEmail(event.target.value)}
        required
      />
      <label htmlFor="password">Password</label>
      <input
        id="password"
        type="password"
        autoComplete={mode === "login" ? "current-password" : "new-password"}
        minLength={10}
        value={password}
        onChange={(event) => setPassword(event.target.value)}
        required
      />
      <button type="submit">{mode === "login" ? "Sign In" : "Create Account"}</button>
      {status ? <p className="form-status">{status}</p> : null}
    </form>
  );
}
