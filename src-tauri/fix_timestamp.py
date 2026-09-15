import re

with open('src/lib.rs', 'r') as f:
    content = f.read()

# Replace NaiveDateTime with DateTime<chrono::Utc> for MySQL structs
content = content.replace("Option<chrono::NaiveDateTime>", "Option<chrono::DateTime<chrono::Utc>>")

with open('src/lib.rs', 'w') as f:
    f.write(content)

