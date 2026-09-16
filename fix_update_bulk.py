import re

with open('src/components/MappingGrid.tsx', 'r') as f:
    grid = f.read()

old_call = """      await onUpdateBulk(
        Array.from(selectedIds), 
        selectedIds.size === 1 ? (formCustomName || null) : null,
        formMainGroup, 
        formStartM === '' ? null : Number(formStartM), formEndM === '' ? null : Number(formEndM)
      );"""

new_call = """      await onUpdateBulk(
        Array.from(selectedIds), 
        selectedIds.size === 1 ? (formCustomName || null) : null,
        formMainGroup, 
        formSubGroup === '' ? null : formSubGroup,
        formStartM === '' ? null : Number(formStartM),
        formEndM === '' ? null : Number(formEndM)
      );"""

grid = grid.replace(old_call, new_call)

with open('src/components/MappingGrid.tsx', 'w') as f:
    f.write(grid)

