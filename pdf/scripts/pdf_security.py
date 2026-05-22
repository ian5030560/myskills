import argparse
import sys
from pathlib import Path

import fitz
# pylint: disable=no-member


def cmd_encrypt(args):
    src = fitz.open(args.pdf)
    out = Path(args.output) if args.output else Path(args.pdf)
    out.parent.mkdir(exist_ok=True, parents=True)
    src.save(
        str(out),
        encryption=fitz.PDF_ENCRYPT_AES_256,
        user_pw=args.user_pw,
        owner_pw=args.owner_pw,
        permissions=args.permissions,
    )
    src.close()
    print(f"Encrypted to {out}", flush=True)


def cmd_decrypt(args):
    src = fitz.open(args.pdf)
    if args.password:
        if not src.authenticate(args.password):
            print("Incorrect password.", file=sys.stderr)
            sys.exit(1)
    out = Path(args.output) if args.output else Path(args.pdf)
    out.parent.mkdir(exist_ok=True, parents=True)
    src.save(str(out))
    src.close()
    print(f"Decrypted to {out}", flush=True)


def build_permissions(flags: list[str]) -> int:
    perm_map = {
        "print": fitz.PDF_PERM_PRINT,
        "modify": fitz.PDF_PERM_MODIFY,
        "copy": fitz.PDF_PERM_COPY,
        "annotate": fitz.PDF_PERM_ANNOTATE,
        "forms": fitz.PDF_PERM_FORM,
        "extract": fitz.PDF_PERM_ACCESSIBILITY,
        "assemble": fitz.PDF_PERM_ASSEMBLE,
        "print-hq": fitz.PDF_PERM_PRINT_HQ,
    }
    perms = 0
    for f in flags or []:
        if f in perm_map:
            perms |= perm_map[f]
    return perms


def main():
    parser = argparse.ArgumentParser(description="PDF security (encrypt / decrypt)")
    sub = parser.add_subparsers(dest="command", required=True)

    # encrypt
    e = sub.add_parser("encrypt", help="Encrypt PDF with password")
    e.add_argument("--pdf", required=True, help="Input PDF file")
    e.add_argument("--user-pw", help="User password (open password)")
    e.add_argument("--owner-pw", help="Owner password (permissions password)")
    e.add_argument("--output", "-o", help="Output file (default: overwrite input)")
    e.add_argument("--permit", nargs="*", dest="permissions",
                   choices=["print", "modify", "copy", "annotate", "forms",
                            "extract", "assemble", "print-hq"],
                   help="Grant specific permissions to the user")
    e.set_defaults(func=cmd_encrypt, permissions=0)

    # decrypt
    d = sub.add_parser("decrypt", help="Decrypt PDF (remove password)")
    d.add_argument("--pdf", required=True, help="Input PDF file")
    d.add_argument("--password", help="Owner password (omit if no password)")
    d.add_argument("--output", "-o", help="Output file (default: overwrite input)")
    d.set_defaults(func=cmd_decrypt)

    args = parser.parse_args()
    if hasattr(args, "permissions") and args.permissions is not None:
        args.permissions = build_permissions(args.permissions)
    args.func(args)


if __name__ == "__main__":
    main()
