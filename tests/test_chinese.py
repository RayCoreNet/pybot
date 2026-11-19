"""Bilingual routing and conversation regressions."""
import subprocess
import sys
import unittest

from bot.runtime import turn
from bot.modules import arbiter, chinese


class ChineseConversation(unittest.TestCase):
    def test_rules(self):
        for text, expected in [('你好！！', '你好'), ('謝謝！', '不客气'),
                               ('你是谁？', 'PyBot'), ('再见', '下次聊'),
                               ('你能做什么？', '记住'), ('𠮷在下雨', '还不太懂')]:
            with self.subTest(text=text):
                self.assertIn(expected, chinese.respond(text, {}))
        self.assertIsNone(chinese.respond('Hello!', {}))

    def test_language_switch_and_session_memory(self):
        memory = {}
        self.assertEqual(turn('我叫小林。', memory)['module'], 'chinese')
        self.assertNotEqual(turn('Hello!', memory)['module'], 'chinese')
        self.assertIn('小林', turn('我叫什么名字？', memory)['reply'])
        self.assertIn('还没', turn('我叫什么？', {})['reply'])

    def test_does_not_displace_safety_candidate(self):
        candidates = [
            {'module': 'safety', 'priority': arbiter.SAFETY, 'reply': 'Safety reply.'},
            {'module': 'chinese', 'priority': chinese.PRIORITY, 'reply': '你好！'},
        ]
        self.assertEqual(arbiter.choose('你好', {'turns': []}, candidates), 0)

    def test_original_cli_entrypoint(self):
        process = subprocess.run(
            [sys.executable, '-X', 'utf8', '-m', 'pybot', '-p', '谢谢！'],
            capture_output=True, encoding='utf-8', check=True, timeout=60,
        )
        self.assertEqual(process.stdout, '不客气！\n')
