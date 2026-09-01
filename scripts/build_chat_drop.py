"""Export one chat-uploadable Markdown file for every installable Skill."""

from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills"
DEST = ROOT / "chat-ready"


def main() -> None:
    DEST.mkdir(exist_ok=True)
    for source in sorted(SOURCE.glob("*/SKILL.md")):
        target = DEST / f"{source.parent.name}.md"
        shutil.copyfile(source, target)
        print(target.relative_to(ROOT))


if __name__ == "__main__":
    main()
