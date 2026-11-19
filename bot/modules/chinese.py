"""Rule-based Chinese conversation within the normal module pipeline."""

import re
import unicodedata

PRIORITY = 8000


# Unicode names also cover Han extensions outside the Basic Multilingual Plane.
def _has_han(text):
    return any(unicodedata.name(char, "").startswith(
        ("CJK UNIFIED IDEOGRAPH-", "CJK COMPATIBILITY IDEOGRAPH-")
    ) for char in text)


_NAME = re.compile(r"(?:我叫|我的名字[是叫])\s*([^\W\d_]{1,16})(?=$|[，,。.!！?？])")
_FALLBACK = "这句话我还不太懂。你可以换个说法，或者问我能做什么。"
_RULES = (
    (("你好", "您好", "嗨", "哈喽"), "你好！今天想聊些什么？"),
    (("谢谢", "多谢", "謝謝", "多謝"), "不客气！"),
    (("再见", "拜拜", "再見"), "再见！下次聊。"),
    (("你是谁", "你是誰", "你叫什么", "你叫什麼"), "我是 PyBot，一个基于规则的聊天机器人。"),
    (("你能做什么", "你會做什麼", "帮助", "幫助"),
     "我能用中文打招呼、介绍自己，也能记住你在本次对话中告诉我的名字。"),
)


def respond(text, memory):
    """Propose a Chinese reply when the input contains Han characters."""
    normalized = unicodedata.normalize("NFKC", text).strip()
    if not _has_han(normalized):
        return None

    state = memory.setdefault("chinese", {})
    phrase = normalized.rstrip("。.!！?？ ")
    if phrase in ("我叫什么", "我叫什么名字", "我的名字是什么", "你还记得我吗",
                  "我叫什麼", "我叫什麼名字", "我的名字是什麼", "你還記得我嗎"):
        name = state.get("name")
        return f"你之前告诉我，你叫{name}。" if name else "你还没告诉我你的名字。"
    match = _NAME.match(phrase)
    if match:
        name = state["name"] = match[1]
        return f"你好，{name}！很高兴认识你。"
    for phrases, answer in _RULES:
        if phrase in phrases:
            return answer
    return _FALLBACK
