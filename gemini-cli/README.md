# Gemini CLI Setup

This guide provides instructions for setting up and authenticating the Gemini CLI.

## 1. Installation

First, ensure you have Node.js (version 18 or higher) installed.

Then, run the following command to install the Gemini CLI globally:

```bash
npm install -g @google/gemini-cli
```

To verify the installation, check the version:

```bash
gemini --version
```

## 2. Start the CLI

To start the interactive Gemini CLI, simply run:

```bash
gemini
```

## 3. Authentication

Once inside the Gemini CLI, use the `/auth` command to authenticate. You will be prompted to choose a login method (e.g., personal account or API key).

```
/auth
```