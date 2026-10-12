import type { DataSource, InvokeArgs } from "./types";

const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? "/api/v1";

/**
 * Pemetaan panggilan `invoke(command, args)` di desktop ke endpoint HTTP REST di Cloud.
 * Menggunakan query string atau path yang sesuai.
 */
interface RequestConfig {
  path: string;
  method?: string;
  body?: any;
}

const mapCommandToRequest = (command: string, args?: InvokeArgs): RequestConfig | null => {
  switch (command) {
    case "get_live_segments":
      return { path: "/web/live_segments" };

    case "get_segment_mappings":
      return { path: "/segments" };

    case "get_alarms": {
      const date = args?.date ? `?date=${encodeURIComponent(String(args.date))}` : "";
      return { path: `/alarms${date}` };
    }

    case "get_groups_history": {
      const q = new URLSearchParams();
      if (args?.startDt) q.set("start_dt", String(args.startDt));
      if (args?.endDt) q.set("end_dt", String(args.endDt));
      return { path: `/history/groups?${q.toString()}` };
    }

    case "get_history_summary": {
      const q = new URLSearchParams();
      if (args?.startDt) q.set("start_dt", String(args.startDt));
      if (args?.endDt) q.set("end_dt", String(args.endDt));
      return { path: `/history/summary?${q.toString()}` };
    }

    case "get_segment_history": {
      const q = new URLSearchParams();
      if (args?.dtsCh !== undefined) q.set("dts_ch", String(args.dtsCh));
      if (args?.dtsCode !== undefined) q.set("dts_code", String(args.dtsCode));
      if (args?.minutes !== undefined) q.set("minutes", String(args.minutes));
      return { path: `/history/segment?${q.toString()}` };
    }

    case "get_spatial_profile": {
      const group = args?.mainGroup ? `?main_group=${encodeURIComponent(String(args.mainGroup))}` : "";
      return { path: `/spatial/profile${group}` };
    }

    case "get_system_logs":
      return { path: "/logs/system" };

    case "write_system_log":
      return {
        path: "/logs/system",
        method: "POST",
        body: {
          event_type: args?.eventType || "INFO",
          message: args?.message || "",
        },
      };

    case "get_all_settings":
      return { path: "/settings/all" };

    case "get_map_calibration":
      return { path: "" }; // Calibrations are baked in frontend or empty in web

    default:
      return null;
  }
};

export const httpSource: DataSource = async (command, args) => {
  // Mock/no-op fallback untuk command khusus desktop yang dipanggil di web
  if (command === "ack_all_alarms") {
    console.warn("ack_all_alarms hanya dapat dilakukan secara fisik di unit lokal DTS.");
    return;
  }
  if (command === "toggle_fullscreen") {
    return false;
  }
  if (command === "get_map_calibration") {
    return [];
  }
  if (command === "get_users") {
    return [];
  }

  const req = mapCommandToRequest(command, args);
  if (!req) {
    throw new Error(`Command "${command}" belum tersedia di REST API cloud.`);
  }

  const token = localStorage.getItem("jwt_token");
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${req.path}`, {
    method: req.method || "GET",
    headers,
    body: req.body ? JSON.stringify(req.body) : undefined,
  });

  if (res.status === 401) {
    localStorage.removeItem("jwt_token");
    localStorage.removeItem("userRole");
    localStorage.removeItem("userId");
    localStorage.removeItem("userPlan");
    if (window.location.pathname !== "/login") {
      window.location.href = "/login";
    }
    throw new Error("Sesi login berakhir. Silakan login kembali.");
  }

  if (!res.ok) {
    throw new Error(`HTTP Error ${res.status}: ${res.statusText}`);
  }

  const json = await res.json();
  return json.data !== undefined ? json.data : json;
};
