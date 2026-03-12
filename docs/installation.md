# Installation

## Recommended

Use the skill's GitHub URL directly in your agent prompt.

Example:

```text
install https://github.com/Nightnzh/my_skills/tree/main/skills/android-strings-localized-translate skill
```

Traditional Chinese example:

```text
請安裝這個 skill：
https://github.com/Nightnzh/my_skills/tree/main/skills/android-strings-localized-translate
```

## Template

Replace `<slug>` with the skill folder name:

```text
install https://github.com/Nightnzh/my_skills/tree/main/skills/<slug> skill
```

Or:

```text
請安裝這個 skill：
https://github.com/Nightnzh/my_skills/tree/main/skills/<slug>
```

## Advanced / Maintainer Notes

This repository still includes local tooling such as `./tools/install_skill`, but it is a maintainer-oriented path rather than the primary end-user instruction.
