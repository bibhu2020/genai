# 🔐 Security Policy

We take security seriously at [YourOrgName] and appreciate your efforts to responsibly disclose vulnerabilities.

## 📆 Supported Versions

We actively maintain the following versions:

| Version | Supported          |
|---------|--------------------|
| 1.x     | ✅ Yes              |
| < 1.0   | ❌ No (upgrade required) |

If you're using an unsupported version, we strongly encourage upgrading to a supported release.

## 🚨 Reporting a Vulnerability

If you discover a security vulnerability, **please DO NOT open an issue or pull request** on GitHub.

Instead, follow these steps:

1. **Email us at**: [security@example.com](mailto:security@example.com)
2. Provide:
   - A detailed description of the vulnerability
   - Steps to reproduce (proof of concept)
   - Potential impact
3. You’ll receive an acknowledgment within **2 business days**, and we’ll provide a status update within **7 business days**.

We follow [Coordinated Disclosure](https://en.wikipedia.org/wiki/Coordinated_disclosure).

## 🛡️ Security Measures

We apply the following security practices:

- ✅ Dependency scanning via [Dependabot](https://github.com/dependabot)
- ✅ Code scanning using GitHub Advanced Security / CodeQL
- ✅ Secrets detection using [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- ✅ SAST and DAST tools in CI/CD (e.g., SonarQube, Snyk, OWASP ZAP)

## 👩‍💻 Security Best Practices (For Contributors)

Please follow these guidelines when contributing:

- Never commit secrets or credentials
- Validate all input data
- Use secure defaults
- Keep dependencies updated
- Follow the [OWASP Top 10](https://owasp.org/www-project-top-ten/)

## 🧾 Additional Resources

- [Node.js Security Best Practices](https://github.com/lirantal/nodejs-security-best-practices)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [NPM Audit](https://docs.npmjs.com/cli/v8/commands/npm-audit)

---

Thank you for helping us keep our project secure!
