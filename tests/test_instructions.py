# Copyright (c) 2026 Google LLC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Tests for the MCP server instructions sent in the initialize result."""

import re
import unittest

from gateway import forward

# Tool names in the instructions: snake_case identifiers with an underscore.
_TOOL_NAME = re.compile(r"\b[a-z]+(?:_[a-z0-9]+)+\b")
# list_*/get_* are families, not tool names.
_FAMILY = re.compile(r"\b(?:list|get)_\*")


class InstructionsTest(unittest.TestCase):

  def test_initialize_sends_instructions(self):
    self.assertEqual(
        forward.mcp_server.instructions, forward.MCP_SERVER_INSTRUCTIONS
    )

  def test_short(self):
    # Sent on every session; about 4 bytes per token.
    self.assertLess(len(forward.MCP_SERVER_INSTRUCTIONS), 800)

  def test_named_tools_exist(self):
    text = _FAMILY.sub("", forward.MCP_SERVER_INSTRUCTIONS)
    names = set(_TOOL_NAME.findall(text)) - {"database_id"}
    self.assertTrue(names)
    registered = set(forward.__dict__) | _proxy_tool_names()
    self.assertEqual(sorted(names - registered), [])


def _proxy_tool_names() -> set[str]:
  """Tool functions defined by the generated proxy and optional modules."""
  from gateway import proxy  # pylint: disable=g-import-not-at-top

  names = set(vars(proxy))
  for mod in ("gateway.patcher", "gateway.query"):
    try:
      module = __import__(mod, fromlist=["_"])
    except ImportError:
      continue
    names |= set(vars(module))
  return names


if __name__ == "__main__":
  unittest.main()
