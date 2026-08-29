from pathlib import Path
import sys

from pydantic import BaseModel

sys.path.append(str(Path(__file__).resolve().parents[1]))

from common.llm import chat


class Person(BaseModel):
    name: str
    age: int
    occupation: str


def main() -> None:
    schema = Person.model_json_schema()
    prompt = "Return a fictional person as JSON with name, age, occupation."
    resp = chat(
        [{"role": "user", "content": prompt}],
        response_format={"type": "json_schema", "json_schema": {"name": "person", "schema": schema}},
        max_tokens=2000,
    )
    person = Person.model_validate_json(resp["response_content"] or "{}")
    print(person.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
