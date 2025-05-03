# Bug: OpenAI API v1.0.0+ Compatibility Issue

**Date Encountered:** May 3, 2025

**Component:** `src/app/services/text_analysis.py` (or specify where the error originated)

**Severity:** High (Blocks core functionality)

**Status:** Open / Resolved (Update as needed)

## Description

The application failed when attempting to call the OpenAI API for chat completion or embeddings. This is because the code uses the syntax for `openai` library versions prior to 1.0.0, while a newer version (>=1.0.0) is installed. The newer versions have breaking changes in how API calls are made.

## Error Message

```json
{
  "detail": "\n\nYou tried to access openai.ChatCompletion, but this is no longer supported in openai>=1.0.0 - see the README at https://github.com/openai/openai-python for the API.\n\nYou can run `openai migrate` to automatically upgrade your codebase to use the 1.0.0 interface. \n\nAlternatively, you can pin your installation to the old version, e.g. `pip install openai==0.28`\n\nA detailed migration guide is available here: https://github.com/openai/openai-python/discussions/742\n"
}
```
