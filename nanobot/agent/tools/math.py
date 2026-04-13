from typing import Any

from nanobot.agent.tools.base import Tool


class MultiplyTool(Tool):
    @property
    def name(self) -> str:
        return "multiply"

    @property
    def description(self) -> str:
        return "用于简单的乘法运算（a * b）。"

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "第一个乘数"},
                "b": {"type": "number", "description": "第二个乘数"},
            },
            "required": ["a", "b"],
        }

    async def execute(self, a: float, b: float, **kwargs: Any) -> str:
        result = float(a) * float(b)
        if result.is_integer():
            return str(int(result))
        return str(result)
