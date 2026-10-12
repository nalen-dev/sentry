/** Kontrak sumber data. UI hanya bergantung pada ini, bukan pada Tauri / HTTP. */
export type InvokeArgs = Record<string, unknown>;
export type DataSource = <T = any>(command: string, args?: InvokeArgs) => Promise<T>;
