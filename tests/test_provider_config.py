import importlib
import os
import sys
import types
import unittest


def install_dependency_stubs():
    openai = types.ModuleType("openai")

    class AuthenticationError(Exception):
        pass

    class DummyOpenAI:
        def __init__(self, *args, **kwargs):
            self.models = types.SimpleNamespace(list=lambda: [])
            self.chat = types.SimpleNamespace(
                completions=types.SimpleNamespace(create=lambda **kwargs: [])
            )

    openai.AuthenticationError = AuthenticationError
    openai.OpenAI = DummyOpenAI
    sys.modules["openai"] = openai

    colorama = types.ModuleType("colorama")
    colorama.Fore = types.SimpleNamespace(CYAN="")
    colorama.Style = types.SimpleNamespace(RESET_ALL="")
    colorama.init = lambda autoreset=True: None
    sys.modules["colorama"] = colorama

    pwinput_module = types.ModuleType("pwinput")
    pwinput_module.pwinput = lambda prompt="", mask="*": ""
    sys.modules["pwinput"] = pwinput_module

    dotenv = types.ModuleType("dotenv")
    dotenv.load_dotenv = lambda dotenv_path=None, override=False: None
    dotenv.set_key = lambda path, key, value: None
    sys.modules["dotenv"] = dotenv

    rich = types.ModuleType("rich")
    sys.modules["rich"] = rich

    console_module = types.ModuleType("rich.console")

    class DummyStatus:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    class DummyConsole:
        def print(self, *args, **kwargs):
            return None

        def input(self, *args, **kwargs):
            return ""

        def status(self, *args, **kwargs):
            return DummyStatus()

    console_module.Console = DummyConsole
    sys.modules["rich.console"] = console_module

    panel_module = types.ModuleType("rich.panel")
    panel_module.Panel = type("Panel", (), {})
    sys.modules["rich.panel"] = panel_module

    markdown_module = types.ModuleType("rich.markdown")
    markdown_module.Markdown = type("Markdown", (), {})
    sys.modules["rich.markdown"] = markdown_module

    text_module = types.ModuleType("rich.text")
    text_module.Text = type("Text", (), {})
    sys.modules["rich.text"] = text_module

    live_module = types.ModuleType("rich.live")

    class DummyLive:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def update(self, *args, **kwargs):
            return None

    live_module.Live = DummyLive
    sys.modules["rich.live"] = live_module

    table_module = types.ModuleType("rich.table")
    table_module.Table = type("Table", (), {})
    sys.modules["rich.table"] = table_module

    spinner_module = types.ModuleType("rich.spinner")
    spinner_module.Spinner = type("Spinner", (), {})
    sys.modules["rich.spinner"] = spinner_module

    align_module = types.ModuleType("rich.align")
    align_module.Align = type("Align", (), {"center": staticmethod(lambda value: value)})
    sys.modules["rich.align"] = align_module


def load_hexsec_module():
    install_dependency_stubs()
    sys.modules.pop("HexSecGPT", None)
    return importlib.import_module("HexSecGPT")


class ProviderConfigTests(unittest.TestCase):
    def setUp(self):
        self.original_env = os.environ.copy()
        for key in list(os.environ):
            if key.startswith("HEXSECGPT_") or key == "HexSecGPT-API":
                os.environ.pop(key, None)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_defaults_to_openrouter_config(self):
        module = load_hexsec_module()

        self.assertEqual(module.Config.get_provider_name(), "openrouter")

        config = module.Config.get_provider_config()
        self.assertEqual(config["BASE_URL"], "https://openrouter.ai/api/v1")
        self.assertEqual(config["MODEL_NAME"], "deepseek/deepseek-r1-0528:free")
        self.assertEqual(config["API_KEY_NAME"], "HEXSECGPT_OPENROUTER_API_KEY")
        self.assertIn("HTTP-Referer", config["DEFAULT_HEADERS"])
        self.assertIn("X-Title", config["DEFAULT_HEADERS"])

    def test_custom_openai_provider_reads_runtime_settings(self):
        module = load_hexsec_module()
        os.environ["HEXSECGPT_PROVIDER"] = "custom_openai"
        os.environ["HEXSECGPT_CUSTOM_OPENAI_API_KEY"] = "sk-custom"
        os.environ["HEXSECGPT_CUSTOM_OPENAI_BASE_URL"] = "https://example.test/v1"
        os.environ["HEXSECGPT_CUSTOM_OPENAI_MODEL"] = "custom-model"

        config = module.Config.get_provider_config()

        self.assertEqual(config["BASE_URL"], "https://example.test/v1")
        self.assertEqual(config["MODEL_NAME"], "custom-model")
        self.assertEqual(config["API_KEY_NAME"], "HEXSECGPT_CUSTOM_OPENAI_API_KEY")
        self.assertEqual(config["DEFAULT_HEADERS"], {})

    def test_custom_openai_provider_uses_zai_defaults(self):
        module = load_hexsec_module()
        os.environ["HEXSECGPT_PROVIDER"] = "custom_openai"

        config = module.Config.get_provider_config()

        self.assertEqual(config["BASE_URL"], "https://api.z.ai/api/paas/v4")
        self.assertEqual(config["MODEL_NAME"], "glm-5")

    def test_custom_openai_legacy_pass_url_is_normalized(self):
        module = load_hexsec_module()
        os.environ["HEXSECGPT_PROVIDER"] = "custom_openai"
        os.environ["HEXSECGPT_CUSTOM_OPENAI_BASE_URL"] = "https://api.z.ai/api/pass/v4"

        config = module.Config.get_provider_config()

        self.assertEqual(config["BASE_URL"], "https://api.z.ai/api/paas/v4")

    def test_legacy_api_key_fallback_is_preserved(self):
        module = load_hexsec_module()
        os.environ["HEXSECGPT_PROVIDER"] = "deepseek"
        os.environ["HexSecGPT-API"] = "legacy-key"

        self.assertEqual(module.Config.get_api_key_name(), "HEXSECGPT_DEEPSEEK_API_KEY")
        self.assertEqual(module.Config.get_api_key(), "legacy-key")

    def test_custom_provider_reports_missing_required_settings(self):
        module = load_hexsec_module()
        os.environ["HEXSECGPT_PROVIDER"] = "custom_openai"
        os.environ["HEXSECGPT_CUSTOM_OPENAI_API_KEY"] = "sk-custom"

        self.assertEqual(
            module.Config.get_missing_provider_settings(),
            [],
        )

    def test_custom_openai_key_prompt_does_not_require_sk_prefix(self):
        module = load_hexsec_module()
        app = module.App()

        prompt = app.get_api_key_prompt_text(
            module.Config.get_provider_config("custom_openai")
        )

        self.assertEqual(prompt, "[bold yellow]Enter your API Key:[/]")

    def test_openrouter_key_prompt_keeps_provider_specific_hint(self):
        module = load_hexsec_module()
        app = module.App()

        prompt = app.get_api_key_prompt_text(
            module.Config.get_provider_config("openrouter")
        )

        self.assertIn("sk-or-", prompt)


if __name__ == "__main__":
    unittest.main()
