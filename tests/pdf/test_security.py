import subprocess
import sys
from pathlib import Path

import fitz
import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "pdf" / "scripts"
SEC_SCRIPT = SCRIPTS_DIR / "pdf_security.py"


def _run(args: list[str]):
    return subprocess.run(
        [sys.executable, str(SEC_SCRIPT)] + args,
        capture_output=True, text=True, encoding="utf-8",
    )


class TestSecurity:

    def test_encrypt(self, simple_pdf, output_dir):
        out = output_dir / "encrypted.pdf"
        result = _run(["encrypt", "--pdf", str(simple_pdf),
                       "--user-pw", "secret", "--output", str(out)])
        assert result.returncode == 0
        doc = fitz.open(str(out))
        assert doc.is_encrypted
        doc.close()

    def test_encrypt_then_decrypt(self, simple_pdf, output_dir):
        enc = output_dir / "encrypted.pdf"
        dec = output_dir / "decrypted.pdf"

        r1 = _run(["encrypt", "--pdf", str(simple_pdf),
                    "--user-pw", "secret", "--output", str(enc)])
        assert r1.returncode == 0

        r2 = _run(["decrypt", "--pdf", str(enc),
                    "--password", "secret", "--output", str(dec)])
        assert r2.returncode == 0

        doc = fitz.open(str(dec))
        text = doc[0].get_text()
        doc.close()
        assert "Hello World" in text

    def test_encrypt_with_permissions(self, simple_pdf, output_dir):
        out = output_dir / "restricted.pdf"
        result = _run(["encrypt", "--pdf", str(simple_pdf),
                       "--user-pw", "user", "--owner-pw", "admin",
                       "--permit", "print", "copy",
                       "--output", str(out)])
        assert result.returncode == 0

    def test_decrypt_encrypted(self, secure_pdf, output_dir):
        out = output_dir / "decrypted.pdf"
        result = _run(["decrypt", "--pdf", str(secure_pdf),
                       "--password", "owner123", "--output", str(out)])
        assert result.returncode == 0
        doc = fitz.open(str(out))
        text = doc[0].get_text()
        doc.close()
        assert "Hello World" in text
