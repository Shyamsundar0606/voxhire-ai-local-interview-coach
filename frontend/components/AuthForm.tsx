"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { useAuth } from "@/components/AuthProvider";

export function AuthForm({ mode }: { mode: "login" | "register" }) {
  const { login, register } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      if (mode === "login") await login(email, password);
      else await register(email, password);
      router.push("/");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Request failed.");
    } finally {
      setIsSubmitting(false);
    }
  }

  const isLogin = mode === "login";
  return (
    <main className="auth-page">
      <section className="auth-card" aria-labelledby="auth-heading">
        <div className="brand-lockup auth-brand">
          <div className="brand-mark" aria-hidden="true">V</div>
          <div>
            <p className="brand-name">VoxHire</p>
            <p className="brand-caption">LOCAL COACH</p>
          </div>
        </div>
        <p className="eyebrow eyebrow--bright">PRIVATE WORKSPACE</p>
        <h1 id="auth-heading">{isLogin ? "Welcome back." : "Create your workspace."}</h1>
        <p className="auth-intro">
          {isLogin ? "Continue your interview practice locally." : "Your practice data stays on this machine."}
        </p>
        <form className="auth-form" onSubmit={handleSubmit}>
          <label htmlFor="email">Email address</label>
          <input id="email" type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
          <label htmlFor="password">Password</label>
          <input id="password" type="password" autoComplete={isLogin ? "current-password" : "new-password"} minLength={isLogin ? 1 : 8} value={password} onChange={(event) => setPassword(event.target.value)} required />
          {error && <p className="form-error" role="alert">{error}</p>}
          <button className="primary-button auth-submit" type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Working..." : isLogin ? "Log in" : "Create account"}
          </button>
        </form>
        <p className="auth-switch">
          {isLogin ? "New to VoxHire?" : "Already have an account?"}{" "}
          <Link href={isLogin ? "/register" : "/login"}>{isLogin ? "Create an account" : "Log in"}</Link>
        </p>
      </section>
    </main>
  );
}