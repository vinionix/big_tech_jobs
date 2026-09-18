export type ServiceState = "healthy" | "unavailable" | "disabled";

export interface ServiceStatus {
  status: ServiceState;
  required: boolean;
  detail: string | null;
}

export interface HealthReport {
  status: "healthy" | "degraded" | "unhealthy";
  ready: boolean;
  checked_at: string;
  services: Record<string, ServiceStatus>;
}

export async function fetchHealth(signal?: AbortSignal): Promise<HealthReport> {
  const response = await fetch("/backend/api/v1/health", {
    cache: "no-store",
    headers: { Accept: "application/json" },
    signal,
  });

  if (!response.ok) {
    throw new Error(`Health endpoint respondeu com HTTP ${response.status}`);
  }

  return (await response.json()) as HealthReport;
}

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
  }
}

export async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`/backend/api/v1${path}`, {
    ...options,
    credentials: "include",
    headers: {
      Accept: "application/json",
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...options.headers,
    },
  });

  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new ApiError(payload?.detail ?? `A API respondeu com HTTP ${response.status}`, response.status);
  }
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}
