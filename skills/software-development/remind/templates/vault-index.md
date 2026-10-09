# _index.md Template

Only a designated writer child creates/updates this index under `references/vault-writer.md`; parent/reviewer never mutate it.

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

List every immediate subdirectory/content file (except the index itself and hidden application metadata); give restrictive gates. Reread the target and affected ancestors before patching; serialize with all writers on this vault, preserve concurrent additions, deduplicate, replace obsolete rules. Verify inventory and affected ancestor routing after create/update/rename/delete. Current snapshot only, no chronology, decision IDs or history links.
