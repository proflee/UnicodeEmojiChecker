from tkinter import ttk
import unicodedata

class UnicodeChecker:
    def __init__(self, root):
        self.root = root

    def test_unicode_support(self):
        """增强的Unicode测试（兼容旧系统）"""
        from config import UNICODE_TEST_CHARS
        results = []
        max_supported = "0.0"

        versions = sorted(UNICODE_TEST_CHARS.keys(), key=float, reverse=True)

        for version in versions:
            char_info = UNICODE_TEST_CHARS[version]
            char = char_info["char"]
            name = char_info["name"]

            try:
                test_label = ttk.Label(self.root, text=char, font=("Arial", 12))
                test_label.update()

                actual_text = test_label.cget("text")

                if actual_text != char or len(actual_text) != len(char):
                    status = f"✗ 不支持"
                    char_name = "N/A"
                else:
                    status = "✓ 支持"
                    try:
                        char_name = unicodedata.name(char, "Unknown")
                    except:
                        char_name = "名称未知"

                    if float(version) > float(max_supported):
                        max_supported = version

                test_label.destroy()
            except Exception:
                status = f"✗ 不支持"
                char_name = "N/A"

            results.append({
                "version": version,
                "char": char,
                "name": name,
                "status": status,
                "char_name": char_name,
                "release_date": UNICODE_TEST_CHARS[version]["version"]
            })

        return results, max_supported