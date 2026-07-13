import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from translate_cv import collect_strings, apply_translations


SAMPLE_CV = {
    "quote": "Hello world",
    "basic": {"position": "Developer", "firstName": "John"},
    "experience": [
        {
            "position": "Engineer",
            "company": "Acme",
            "tasks": [
                {
                    "project": "Alpha",
                    "entries": ["did A", "did B"],
                }
            ],
        }
    ],
    "skill": [{"category": "AWS", "subskill": ["CDK", "Lambda"]}],
    "education": [{"faculty": "Master: CS", "thesis": "My thesis", "school": "MIT"}],
    "cert": [{"title": "AWS SAA", "code": "SAA-C03"}],
    "presentation": [{"title": "My talk", "detail": ["point 1", "point 2"]}],
    "article": [{"title": "My article"}],
    "oss": [{"name": "mylib", "description": "A library"}],
    "rodo": "GDPR text",
    "contact": {"email": "x@y.com"},
}


def test_collect_strings_count():
    strings = collect_strings(SAMPLE_CV)
    # quote, position, exp.position, project, 2 entries, 2 subskills,
    # faculty, thesis, cert title, pres title, 2 detail, article title, oss description = 16
    assert len(strings) == 16


def test_collect_strings_excludes_non_translatable():
    strings = collect_strings(SAMPLE_CV)
    assert "GDPR text" not in strings
    assert "x@y.com" not in strings
    assert "John" not in strings
    assert "Acme" not in strings
    assert "MIT" not in strings


def test_collect_strings_includes_translatable():
    strings = collect_strings(SAMPLE_CV)
    assert "Hello world" in strings
    assert "Developer" in strings
    assert "Engineer" in strings
    assert "Alpha" in strings
    assert "did A" in strings
    assert "CDK" in strings
    assert "Master: CS" in strings
    assert "My thesis" in strings
    assert "AWS SAA" in strings
    assert "My talk" in strings
    assert "point 1" in strings
    assert "My article" in strings
    assert "A library" in strings


def test_apply_translations_roundtrip():
    strings = collect_strings(SAMPLE_CV)
    # fake translations: uppercase each string
    translated = [s.upper() for s in strings]
    result = apply_translations(SAMPLE_CV, translated)

    assert result["quote"] == "HELLO WORLD"
    assert result["basic"]["position"] == "DEVELOPER"
    assert result["basic"]["firstName"] == "John"  # unchanged
    assert result["experience"][0]["position"] == "ENGINEER"
    assert result["experience"][0]["company"] == "Acme"  # unchanged
    assert result["experience"][0]["tasks"][0]["project"] == "ALPHA"
    assert result["experience"][0]["tasks"][0]["entries"] == ["DID A", "DID B"]
    assert result["skill"][0]["subskill"] == ["CDK", "LAMBDA"]
    assert result["education"][0]["faculty"] == "MASTER: CS"
    assert result["education"][0]["thesis"] == "MY THESIS"
    assert result["education"][0]["school"] == "MIT"  # unchanged
    assert result["cert"][0]["title"] == "AWS SAA"
    assert result["presentation"][0]["title"] == "MY TALK"
    assert result["presentation"][0]["detail"] == ["POINT 1", "POINT 2"]
    assert result["article"][0]["title"] == "MY ARTICLE"
    assert result["oss"][0]["description"] == "A LIBRARY"


def test_apply_translations_preserves_structure():
    strings = collect_strings(SAMPLE_CV)
    translated = [s.upper() for s in strings]
    result = apply_translations(SAMPLE_CV, translated)
    # rodo and contact must be untouched
    assert result["rodo"] == "GDPR text"
    assert result["contact"] == {"email": "x@y.com"}
