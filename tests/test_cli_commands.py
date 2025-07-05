import unittest
from click.testing import CliRunner
from src.main import cli
from unittest.mock import patch, MagicMock

class TestCliCommands(unittest.TestCase):
    def test_cli_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Usage: cli [OPTIONS] COMMAND [ARGS]', result.output)

    def test_status_command(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['status'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Application Status:', result.output)

    @patch('subprocess.Popen')
    def test_code_command_starts_ui_and_api(self, mock_popen):
        # Configure the mock to return a mock process object
        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        runner = CliRunner()
        result = runner.invoke(cli, ['code', '.'])

        # Assert that the command exited successfully
        self.assertEqual(result.exit_code, 0)

        # Assert that subprocess.Popen was called twice
        self.assertEqual(mock_popen.call_count, 2)

        # Check the calls to Popen
        # The order might vary depending on implementation, so check both calls
        calls = mock_popen.call_args_list

        # Expected API command
        api_command_found = False
        # Expected UI command (simplified for now, will refine with actual path)
        ui_command_found = False

        for call_args, call_kwargs in calls:
            command_list = call_args[0]
            if 'python' in command_list[0] and '-m' in command_list and 'src.api' in command_list:
                api_command_found = True
            elif 'npm' in command_list[0] and 'start' in command_list[1] and call_kwargs.get('cwd', '').endswith('electron-llm-ui'):
                ui_command_found = True
        
        self.assertTrue(api_command_found, "API command was not called")
        self.assertTrue(ui_command_found, "UI command was not called")

if __name__ == '__main__':
    unittest.main()