import { tauriSource } from "./tauriSource";
import { httpSource } from "./httpSource";

/** Dipilih saat build: VITE_TARGET=web untuk web, selain itu desktop (Tauri). */
export const isWebTarget = import.meta.env.VITE_TARGET === "web";

export const invoke = isWebTarget ? httpSource : tauriSource;
