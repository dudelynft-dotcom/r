import { neon, type NeonQueryFunction } from "@neondatabase/serverless";

/**
 * Neon Postgres (serverless, HTTP). Returns null when DATABASE_URL is unset
 * (e.g. local dev without a DB) so callers can degrade gracefully.
 */
let sql: NeonQueryFunction<false, false> | null | undefined;

export function getSql() {
  if (sql !== undefined) return sql;
  const url = process.env.DATABASE_URL;
  sql = url ? neon(url) : null;
  return sql;
}
