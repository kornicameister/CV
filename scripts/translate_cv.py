#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

import boto3


MODEL_ID = "eu.anthropic.claude-haiku-4-5-20251001-v1:0"
REGION = os.environ.get("AWS_DEFAULT_REGION", "eu-central-1")

SYSTEM_PROMPT = (
    "You are a professional CV translator. "
    "Translate the given JSON array of strings from English to Polish. "
    "Return ONLY a valid JSON array with the same number of elements in the same order. "
    "Preserve technical terms, proper nouns, product names, and acronyms as-is. "
    "Do not add explanations or any text outside the JSON array."
)


def collect_strings(cv: dict) -> list[str]:
    strings = []

    def add(s):
        strings.append(s if isinstance(s, str) else str(s))

    if cv.get("quote"):
        add(cv["quote"])
    if cv.get("basic", {}).get("position"):
        add(cv["basic"]["position"])
    for exp in cv.get("experience", []):
        if exp.get("position"):
            add(exp["position"])
        for task in exp.get("tasks", []):
            if task.get("project"):
                add(task["project"])
            for entry in task.get("entries", []):
                add(entry)
    for skill in cv.get("skill", []):
        for item in skill.get("subskill", []):
            add(item)
    for edu in cv.get("education", []):
        if edu.get("faculty"):
            add(edu["faculty"])
        if edu.get("thesis"):
            add(edu["thesis"])
    for cert in cv.get("cert", []):
        if cert.get("title"):
            add(cert["title"])
    for pres in cv.get("presentation", []):
        if pres.get("title"):
            add(pres["title"])
        for detail in pres.get("detail", []):
            add(detail)
    for art in cv.get("article", []):
        if art.get("title"):
            add(art["title"])
    for oss in cv.get("oss", []):
        if oss.get("description"):
            add(oss["description"])

    return strings


def apply_translations(cv: dict, translations: list[str]) -> dict:
    it = iter(translations)

    def nxt() -> str:
        return next(it)

    result = json.loads(json.dumps(cv))

    if result.get("quote"):
        result["quote"] = nxt()
    if result.get("basic", {}).get("position"):
        result["basic"]["position"] = nxt()
    for exp in result.get("experience", []):
        if exp.get("position"):
            exp["position"] = nxt()
        for task in exp.get("tasks", []):
            if task.get("project"):
                task["project"] = nxt()
            task["entries"] = [nxt() for _ in task.get("entries", [])]
    for skill in result.get("skill", []):
        skill["subskill"] = [nxt() for _ in skill.get("subskill", [])]
    for edu in result.get("education", []):
        if edu.get("faculty"):
            edu["faculty"] = nxt()
        if edu.get("thesis"):
            edu["thesis"] = nxt()
    for cert in result.get("cert", []):
        if cert.get("title"):
            cert["title"] = nxt()
    for pres in result.get("presentation", []):
        if pres.get("title"):
            pres["title"] = nxt()
        pres["detail"] = [nxt() for _ in pres.get("detail", [])]
    for art in result.get("article", []):
        if art.get("title"):
            art["title"] = nxt()
    for oss in result.get("oss", []):
        if oss.get("description"):
            oss["description"] = nxt()

    return result


def translate(strings: list[str]) -> list[str]:
    client = boto3.client("bedrock-runtime", region_name=REGION)
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 8192,
        "system": SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": json.dumps(strings, ensure_ascii=False),
            }
        ],
    }
    response = client.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json",
    )
    raw = json.loads(response["body"].read())
    text = raw["content"][0]["text"].strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    translated = json.loads(text)
    if len(translated) != len(strings):
        raise ValueError(
            f"Translation count mismatch: sent {len(strings)}, got {len(translated)}"
        )
    return translated


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: translate_cv.py <input.json> <output.json>", file=sys.stderr)
        sys.exit(1)

    source = json.loads(Path(sys.argv[1]).read_text())
    strings = collect_strings(source)
    print(f"Translating {len(strings)} strings via Bedrock Haiku...", file=sys.stderr)
    translated = translate(strings)
    result = apply_translations(source, translated)
    Path(sys.argv[2]).write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"Written: {sys.argv[2]}", file=sys.stderr)


if __name__ == "__main__":
    main()
