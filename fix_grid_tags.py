import re

with open('src/components/MappingGrid.tsx', 'r') as f:
    grid = f.read()

# Fix the unclosed <>
grid = grid.replace("""            </div>
          )}

          {selectedIds.size > 1 && (""", """            </div>
            </>
          )}

          {selectedIds.size > 1 && (""")

with open('src/components/MappingGrid.tsx', 'w') as f:
    f.write(grid)
