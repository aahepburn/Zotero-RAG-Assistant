import { request } from "./client";

export type MetadataVersionInfo = {
  version: number;
  migration_needed: boolean;
  message?: string;
  can_use_filtering: boolean;
};

export type MigrationSummary = {
  total_chunks: number;
  updated_chunks: number;
  failed_chunks: number;
  unique_items: number;
  elapsed_seconds: number;
  success: boolean;
};

export type MigrationResponse = {
  status: "started" | "completed" | "not_needed" | "error";
  message: string;
  summary?: MigrationSummary;
  version?: number;
  error?: string;
};

/**
 * Check the current metadata version and whether migration is needed.
 */
export async function checkMetadataVersion(): Promise<MetadataVersionInfo> {
  return request("/api/metadata/version");
}

/**
 * Trigger metadata migration to update to the current format.
 * This updates metadata in-place without re-embedding.
 */
export async function migrateMetadata(): Promise<MigrationResponse> {
  return request("/api/metadata/migrate", { method: "POST" });
}
