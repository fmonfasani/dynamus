# Needed for path adjustments during tests
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from dynamus_core.framework import (
    TemplateBasedGenerator,
    EntityDefinition,
    FieldDefinition,
    GenerationContext,
)


def create_template(base: Path, framework: str, content: str, architecture: str = None):
    dir_path = base / framework
    if architecture:
        dir_path = dir_path / architecture
    dir_path.mkdir(parents=True, exist_ok=True)
    (dir_path / "template.j2").write_text(content)


def test_generate_with_primary_key(tmp_path):
    template_content = "{{ framework }} {{ primary_key_field.name if primary_key_field else 'no_pk' }}"
    create_template(tmp_path, "fastapi", template_content)
    generator = TemplateBasedGenerator(str(tmp_path))

    entity = EntityDefinition(
        name="User",
        fields=[FieldDefinition(name="id", type="integer", primary_key=True)],
    )
    context = GenerationContext(entity=entity, framework="fastapi")

    files = generator.generate(context)
    assert list(files.values())[0].strip() == "fastapi id"


def test_generate_without_primary_key(tmp_path):
    template_content = "{{ framework }} {{ primary_key_field.name if primary_key_field else 'no_pk' }}"
    create_template(tmp_path, "fastapi", template_content)
    generator = TemplateBasedGenerator(str(tmp_path))

    entity = EntityDefinition(
        name="Item",
        fields=[FieldDefinition(name="name", type="string")],
    )
    context = GenerationContext(entity=entity, framework="fastapi")

    files = generator.generate(context)
    assert list(files.values())[0].strip() == "fastapi no_pk"


def test_generate_multiple_frameworks(tmp_path):
    content = "{{ framework }}"
    create_template(tmp_path, "fastapi", content)
    create_template(tmp_path, "flask", content)
    generator = TemplateBasedGenerator(str(tmp_path))

    entity = EntityDefinition(
        name="Book",
        fields=[FieldDefinition(name="id", type="integer", primary_key=True)],
    )

    fastapi_context = GenerationContext(entity=entity, framework="fastapi")
    flask_context = GenerationContext(entity=entity, framework="flask")

    fastapi_files = generator.generate(fastapi_context)
    flask_files = generator.generate(flask_context)

    assert list(fastapi_files.values())[0].strip() == "fastapi"
    assert list(flask_files.values())[0].strip() == "flask"
    assert len(fastapi_files) == 1
    assert len(flask_files) == 1
