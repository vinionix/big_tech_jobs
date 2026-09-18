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
