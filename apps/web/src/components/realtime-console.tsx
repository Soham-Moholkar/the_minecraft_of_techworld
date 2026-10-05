"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Activity, RefreshCw, ShieldCheck } from "lucide-react";
import { z } from "zod";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

type ConnectionState = "connecting" | "live" | "retrying";

const ticketSchema = z.object({
  url: z.string().url(),
  expires_in_seconds: z.number().int().positive(),
});
const pongSchema = z.object({
  type: z.literal("presence.pong"),
  request_id: z.string().uuid(),
  organization_slug: z.string().min(1),
  subject: z.string().min(1),
  server_time: z.string().datetime(),
});

export function RealtimeConsole() {
  const [connection, setConnection] = useState<ConnectionState>("connecting");
  const [latencyMs, setLatencyMs] = useState<number | null>(null);
  const [identity, setIdentity] = useState("Waiting for authenticated presence…");
  const [lastError, setLastError] = useState<string | null>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const pendingRef = useRef(new Map<string, number>());

  const sendPing = useCallback(() => {
    const socket = socketRef.current;
    if (!socket || socket.readyState !== WebSocket.OPEN) return;
    const requestId = crypto.randomUUID();
    pendingRef.current.set(requestId, performance.now());
    socket.send(JSON.stringify({ type: "presence.ping", request_id: requestId }));
  }, []);

  useEffect(() => {
    let disposed = false;
    let reconnectTimer: ReturnType<typeof setTimeout> | undefined;
    const pendingRequests = pendingRef.current;

    const scheduleReconnect = () => {
      if (disposed || reconnectTimer) return;
      setConnection("retrying");
      reconnectTimer = setTimeout(() => {
        reconnectTimer = undefined;
        void connect();
      }, 2000);
    };

    const connect = async () => {
      setConnection((current) => (current === "retrying" ? "retrying" : "connecting"));
      try {
        // Every reconnect obtains a fresh one-use grant. The durable bearer token
        // remains inside the BFF and is never serialized into browser state.
        const response = await fetch("/api/realtime/ticket", {
          method: "POST",
          cache: "no-store",
        });
        const payload: unknown = await response.json();
        if (!response.ok) throw new Error("Ticket request was rejected");
        const ticket = ticketSchema.parse(payload);
        if (disposed) return;

        const socket = new WebSocket(ticket.url);
        socketRef.current = socket;
        socket.onopen = () => {
          setConnection("live");
          setLastError(null);
          sendPing();
        };
        socket.onmessage = (message) => {
          let decoded: unknown;
          try {
            decoded = JSON.parse(String(message.data));
          } catch {
            setLastError("The server returned malformed realtime data.");
            return;
          }
          const parsed = pongSchema.safeParse(decoded);
          if (!parsed.success) {
            setLastError("The server returned an invalid realtime envelope.");
            return;
          }
          const startedAt = pendingRef.current.get(parsed.data.request_id);
          if (startedAt !== undefined) {
            setLatencyMs(Math.max(0, Math.round(performance.now() - startedAt)));
            pendingRef.current.delete(parsed.data.request_id);
          }
          setIdentity(`${parsed.data.organization_slug} · ${parsed.data.subject}`);
        };
        socket.onerror = () => {
          setLastError("Realtime transport interrupted; requesting a fresh ticket.");
          socket.close();
        };
        socket.onclose = (event) => {
          if (socketRef.current === socket) socketRef.current = null;
          pendingRequests.clear();
          if (!disposed && event.code !== 1000) scheduleReconnect();
        };
      } catch {
        setLastError("Realtime service unavailable; retrying shortly.");
        scheduleReconnect();
      }
    };

    void connect();
    return () => {
      disposed = true;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      socketRef.current?.close(1000, "component unmounted");
      socketRef.current = null;
      pendingRequests.clear();
    };
  }, [sendPing]);

  const tone = connection === "live" ? "success" : connection === "retrying" ? "warning" : "neutral";

  return (
    <Card className="overflow-hidden">
      <div className="flex items-center justify-between border-b border-white/[.07] px-5 py-4">
        <div>
          <h2 className="text-sm font-semibold">Bidirectional presence check</h2>
          <p className="mt-1 text-[10px] text-slate-500">One-use ticket · origin checked · rate limited</p>
        </div>
        <Badge tone={tone}><Activity size={11} />{connection}</Badge>
      </div>
      <div className="grid gap-4 p-5 sm:grid-cols-[1fr_auto] sm:items-end">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-200">
            <ShieldCheck size={14} className="text-cyan-300" />
            {identity}
          </div>
          <p className="mt-3 text-[10px] uppercase tracking-[.16em] text-slate-500">Latest round trip</p>
          <p className="mt-1 text-2xl font-semibold text-white">
            {latencyMs === null ? "—" : latencyMs}<span className="ml-1 text-xs text-slate-500">ms</span>
          </p>
          {lastError ? <p role="status" className="mt-3 text-[10px] text-amber-300">{lastError}</p> : null}
        </div>
        <Button type="button" variant="secondary" disabled={connection !== "live"} onClick={sendPing}>
          <RefreshCw size={13} />Measure round trip
        </Button>
      </div>
    </Card>
  );
}
