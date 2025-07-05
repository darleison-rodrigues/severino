import unittest
from click.testing import CliRunner
from src.main import cli
import os

class TestModelPath(unittest.TestCase):
    def test_gemma_command_invalid_model_path(self):
        runner = CliRunner()
        # Use a path that definitely does not exist
        invalid_path = "/non/existent/path/to/model.gguf"
        result = runner.invoke(cli, ["gemma", "test prompt", "--model-path", invalid_path])
        self.assertIn("Invalid value for '--model-path'", result.output)
        self.assertNotEqual(result.exit_code, 0)

if __name__ == '__main__':
    unittest.main()