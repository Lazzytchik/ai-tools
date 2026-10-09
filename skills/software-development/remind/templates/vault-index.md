# _index.md Template

Use this template when creating a new `_index.md` for a vault directory.

```markdown
# <relative-path>/ — <Short Scope Title>

<One or two sentences describing the current scope.>

## Подкаталоги

- `<subdir-name>/` — <brief description>. Смотреть только <restrictive condition>.

Если подкаталогов нет: "Нет подкаталогов на этом уровне."

## Файлы

- `<filename>.md` — <brief description>. Читать только <restrictive condition>.

Если content-файлов нет: "Нет содержимых файлов на этом уровне."
```

Rules:

1. List every immediate subdirectory and content file.
2. Give each entry a restrictive routing condition.
3. Update the index in the same operation as add, remove, rename, or purpose change.
4. Describe only the current snapshot; do not include decision IDs, chronology, or history links.
