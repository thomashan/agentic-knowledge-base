# Prompt Templates

We can use `prompts/template/*` file(s) and use that as the CLI prompt template or as additional context for the CLI prompt.

## Gemini CLI

The `GEMINI_SYSTEM_MD` environment variable is the key to achieving advanced customisation. It instructs the Gemini CLI to source its core behavioural instructions from an external file rather than its hardcoded
defaults.

The feature is enabled by setting the `GEMINI_SYSTEM_MD` environment variable within the shell.
When the variable is set to true or 1, the CLI searches for a file named `system.md` within a `.gemini` directory at the project's
root. This approach is recommended for project-specific configurations.

We can use the files in `prompts/template/**` and can be used as a template for the `.gemini/system.md` file.
