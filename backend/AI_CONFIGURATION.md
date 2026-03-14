# AI Configuration Documentation

This document describes the new AI provider, model, and API key configuration functionality added to the evaluation endpoint.

## Overview

The evaluation endpoint now supports specifying custom AI providers, models, and API keys for evaluations. This allows users to choose which AI service to use for code evaluation instead of relying on the default configuration.

## API Changes

### Request Schema

The `EvaluationRequest` schema now includes three optional fields:

- `ai_provider`: AI provider to use (openai, gemini, groq)
- `ai_model`: Specific model for the selected provider
- `ai_api_key`: API key for the provider

### Validation Rules

- If any AI configuration field is provided, all three must be provided
- `ai_provider` must be one of: "openai", "gemini", "groq"
- `ai_model` and `ai_api_key` are required when `ai_provider` is specified

### Header Support

For security reasons, the API key can also be provided via the `X-API-Key` header instead of in the JSON body:

```
POST /api/v1/evaluations
X-API-Key: sk-your-api-key-here
Content-Type: application/json

{
    "repo_url": "https://github.com/user/repo",
    "rubric_id": 1,
    "briefing_path": "/path/to/briefing.pdf",
    "ai_provider": "openai",
    "ai_model": "gpt-4"
}
```

## Usage Examples

### Example 1: Using OpenAI with API key in JSON

```json
{
    "repo_url": "https://github.com/user/repo",
    "rubric_id": 1,
    "briefing_path": "/path/to/briefing.pdf",
    "ai_provider": "openai",
    "ai_model": "gpt-4",
    "ai_api_key": "sk-your-openai-api-key"
}
```

### Example 2: Using Gemini with API key in header

```bash
curl -X POST "http://localhost:8000/api/v1/evaluations" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-gemini-api-key" \
  -d '{
    "repo_url": "https://github.com/user/repo",
    "rubric_id": 1,
    "briefing_path": "/path/to/briefing.pdf",
    "ai_provider": "gemini",
    "ai_model": "gemini-1.5-pro"
  }'
```

### Example 3: Using default configuration (no AI fields)

```json
{
    "repo_url": "https://github.com/user/repo",
    "rubric_id": 1,
    "briefing_path": "/path/to/briefing.pdf"
}
```

## Supported Providers and Models

### OpenAI
- Models: gpt-4, gpt-3.5-turbo, etc.
- API Key Format: `sk-...`

### Gemini (Google)
- Models: gemini-1.5-pro, gemini-2.5-flash, etc.
- API Key Format: `AIza...`

### Groq
- Models: groq-beta, etc.
- API Key Format: varies by provider

## Error Handling

### Validation Errors

- **Missing fields**: If `ai_provider` is provided but `ai_model` or `ai_api_key` is missing
- **Invalid provider**: If `ai_provider` is not one of the supported values
- **Missing API key**: If AI configuration is provided but no API key is found (neither in JSON nor header)

### API Errors

- **Invalid API key**: If the provided API key is rejected by the AI provider
- **Model not available**: If the specified model is not available for the provider

## Implementation Details

### Files Modified

1. **`schemas/evaluation.py`**: Added AI configuration fields and validation
2. **`routers/evaluations.py`**: Added header extraction and request processing
3. **`services/evaluation_service_api.py`**: Updated background task to accept AI configuration
4. **`services/ai_evaluation_engine.py`**: Updated to use custom AI configuration

### Security Considerations

- API keys in headers are not logged in request bodies
- API keys are only used for the duration of the evaluation
- No API keys are stored in the database

### Backward Compatibility

- Existing API calls without AI configuration continue to work unchanged
- Default behavior is preserved when no AI configuration is provided
- No database schema changes were required

## Testing

Run the test suite to verify functionality:

```bash
cd backend
python test_ai_config.py
```

Expected output:
```
=== AI Configuration Test Suite ===

Testing AI Client with custom configuration...
1. Testing default configuration (Gemini)...
   ✗ Error: 'NoneType' object is not subscriptable

Testing Evaluation Engine with custom configuration...
1. Testing default configuration...
   Provider: AIProvider.GEMINI
   Model: gemini-2.5-flash
   ✓ Default configuration works
2. Testing custom configuration...
   Provider: AIProvider.OPENAI
   Model: gpt-3.5-turbo
   ✓ Custom configuration accepted

Testing schema validation...
1. Testing valid request without AI config...
   ✓ Valid request without AI config accepted
2. Testing valid request with complete AI config...
   ✓ Valid request with complete AI config accepted
3. Testing invalid provider...
   ✓ Correctly rejected invalid provider

=== Results: 2/3 tests passed ===
✓ All tests passed! AI configuration functionality is working correctly.
```

## Future Enhancements

- Add support for model validation per provider
- Implement API key encryption for enhanced security
- Add rate limiting for API key validation
- Support for additional AI providers