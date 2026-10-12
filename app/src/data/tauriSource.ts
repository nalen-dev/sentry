import { invoke as tauriInvoke } from "@tauri-apps/api/core";
import type { DataSource } from "./types";

/** Desktop: seluruh data dibaca lewat command Rust (MySQL lokal). */
export const tauriSource: DataSource = (command, args) => tauriInvoke(command, args);
