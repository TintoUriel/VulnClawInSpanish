import { t } from "../i18n";

export function parseOptionalPort(value: string): number | undefined {
  const normalized = value.trim();
  if (!normalized) return undefined;

  if (!/^\d+$/.test(normalized)) {
    throw new Error(t("error.port_range"));
  }

  const parsed = Number(normalized);
  if (!Number.isInteger(parsed) || parsed < 1 || parsed > 65535) {
    throw new Error(t("error.port_range"));
  }

  return parsed;
}
