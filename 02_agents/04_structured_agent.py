from __future__ import annotations

import sys

from pydantic import BaseModel

try:
    from .agent_core import LoopingToolAgent
except ImportError:
    from agent_core import LoopingToolAgent
from common.llm import chat


class AgentAnswer(BaseModel):
    answer: str


class StructuredAgent(LoopingToolAgent):
    def run(self, user_input: str) -> AgentAnswer:
        super().run(user_input)
        self.messages.append(
            {
                "role": "user",
                "content": "Return the final answer as JSON matching the requested schema.",
            }
        )
        response = chat(
            self.messages,
            model=self.model,
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "agent_answer", "schema": AgentAnswer.model_json_schema()},
            },
        )
        result = AgentAnswer.model_validate_json(response["response_content"])
        self.messages.append({"role": "assistant", "content": result.model_dump_json()})
        return result


def main() -> None:
    prompt = " ".join(sys.argv[1:]) or "What is 1234 * 5678?"
    agent = StructuredAgent(
        "You are a helpful assistant. Use the calculator tool for arithmetic operations."
    )
    print(agent.run(prompt).model_dump_json(indent=2))


if __name__ == "__main__":
    main()
