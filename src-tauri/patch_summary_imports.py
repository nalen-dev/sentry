import re

with open('src/lib.rs', 'r') as f:
    content = f.read()

content = content.replace("crate::db::get_settings(&*state)", "get_settings(state.clone())")
content = content.replace("crate::domain::app_models::get_segment_mappings(&*state)", "get_segment_mappings(state.clone())")

with open('src/lib.rs', 'w') as f:
    f.write(content)

