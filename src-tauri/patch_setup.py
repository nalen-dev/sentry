import re

with open('src/lib.rs', 'r') as f:
    content = f.read()

setup_old = """                // Store connection pool in Tauri state
                handle.manage(pool);
                handle.manage(MysqlState(Mutex::new(None)));
            });
            
            Ok(())
        })"""

setup_new = """                // Store connection pool in Tauri state
                let p = pool.clone();
                handle.manage(pool);
                handle.manage(MysqlState(Mutex::new(None)));
                
                // Write startup log
                let _ = sqlx::query("INSERT INTO system_logs (event_type, message) VALUES ('SYSTEM', 'Sistem Sentry SCADA dinyalakan')")
                    .execute(&p).await;
            });
            
            Ok(())
        })
        .on_window_event(|window, event| match event {
            tauri::WindowEvent::CloseRequested { .. } => {
                let state: tauri::State<'_, SqlitePool> = window.state();
                let _ = tauri::async_runtime::block_on(async {
                    let _ = sqlx::query("INSERT INTO system_logs (event_type, message) VALUES ('SYSTEM', 'Sistem Sentry SCADA dimatikan')")
                        .execute(&*state).await;
                });
            }
            _ => {}
        })"""

content = content.replace(setup_old, setup_new)

with open('src/lib.rs', 'w') as f:
    f.write(content)

