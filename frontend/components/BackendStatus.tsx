"use client";

import { useEffect, useState } from "react";

import { getHealth, type HealthResponse } from "@/lib/api";

type StatusState =
  | { kind: "loading" }
  | { kind: "ready"; data: HealthResponse }
  | { kind: "error"; message: string };

export function BackendStatus() {
  const [state, setState] = useState<StatusState>({ kind: "loading" });

  useEffect(() => {
    let active = true;

    getHealth()
      .then((data) => {
        if (active) setState({ kind: "ready", data });
      })
      .catch((error: unknown) => {
        if (active) {
          setState({
            kind: "error",
            message:
              error instanceof Error ? error.message : "Backend is unavailable.",
          });
        }
      });

    return () => {
      active = false;
    };
  }, []);

  if (state.kind === "loading") {
    return <StatusPill tone="loading" label="Checking local API" />;
  }

  if (state.kind === "error") {
    return <StatusPill tone="error" label={state.message} />;
  }

  return <StatusPill tone="ready" label={`${state.data.service} online`} />;
}

function StatusPill({
  label,
  tone,
}: {
  label: string;
  tone: "loading" | "ready" | "error";
}) {
  return (
    <div className={`status-pill status-pill--${tone}`} role="status">
      <span className="status-dot" aria-hidden="true" />
      <span>{label}</span>
    </div>
  );
}
