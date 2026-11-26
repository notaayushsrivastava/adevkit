# Security Policy

## Supported Versions

| Version | Supported |
| --- | --- |
| `0.1.x` (Latest) | Yes |
| `< 0.1.0` | No |

---

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability in **adevkit** (for example, in the Windows DPAPI / POSIX vault encryption, CLI subprocess handling, skill/template path traversal, or the local PyWebView server), please report it privately via one of the following channels:

1. **GitHub Private Vulnerability Reporting** (preferred):
   Open a private advisory at [Security Advisories](https://github.com/notaayushsrivastava/adevkit/security/advisories/new).
2. **Email**:
   Send details to **aayush@aayushsrivastava.com** with `[SECURITY] adevkit` in the subject line.

### What to Include
- Description of the vulnerability and potential impact.
- Step-by-step reproduction instructions or a minimal proof of concept.
- Your `adevkit info` output (OS, Python version, installation channel).

### Response Timeline
- **Acknowledgement**: Within 48 hours of receipt.
- **Triage & Assessment**: Within 5 business days.
- **Fix & Disclosure**: We will coordinate a patch release and public advisory once a fix is verified.
