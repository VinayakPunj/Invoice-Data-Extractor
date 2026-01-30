# LLM Model Configuration

## Quick Start

The Invoice Data Extractor supports multiple AI models. The default model is `gemini-2.0-flash-exp`, which provides the best balance of speed and accuracy.

## Supported Models

### Gemini Models (Recommended)
- `gemini-2.0-flash-exp` - Latest, fastest (default)
- `gemini-1.5-pro` - Highest quality
- `gemini-1.5-flash` - Fast and balanced

### Gemma Models (Open-Source)
- `models/gemma-2-27b-it` - 27B params, highest quality
- `models/gemma-2-9b-it` - 9B params, balanced
- `models/gemma-2-2b-it` - 2B params, lightweight

## Configuration

Edit your `.env` file:

```bash
# Choose a model
LLM_MODEL=gemini-2.0-flash-exp

# Or use Gemma (open-source)
LLM_MODEL=models/gemma-2-9b-it
```

## Troubleshooting

### 404 Error: Model Not Found

If you get a 404 error:

1. Update to the latest model:
   ```bash
   LLM_MODEL=gemini-2.0-flash-exp
   ```

2. For Gemma models, ensure you use `models/` prefix:
   ```bash
   LLM_MODEL=models/gemma-2-9b-it
   ```

3. Verify your API key has access to the model

### Performance Tuning

**For faster processing:**
```bash
LLM_MODEL=gemini-2.0-flash-exp
LLM_MAX_OUTPUT_TOKENS=4096
```

**For better accuracy:**
```bash
LLM_MODEL=gemini-1.5-pro
LLM_TEMPERATURE=0
```

## Model Comparison

| Model | Speed | Quality | Cost | Type |
|-------|-------|---------|------|------|
| gemini-2.0-flash-exp | ⚡⚡⚡ | ⭐⭐⭐ | $ | Closed |
| gemini-1.5-pro | ⚡ | ⭐⭐⭐⭐⭐ | $$$ | Closed |
| gemini-1.5-flash | ⚡⚡⚡ | ⭐⭐⭐ | $ | Closed |
| models/gemma-2-27b-it | ⚡ | ⭐⭐⭐⭐ | $ | Open |
| models/gemma-2-9b-it | ⚡⚡ | ⭐⭐⭐ | $ | Open |
| models/gemma-2-2b-it | ⚡⚡⚡ | ⭐⭐ | $ | Open |

## Need More Details?

See the complete [LLM Models Guide](file:///C:/Users/Vinay/.gemini/antigravity/brain/5b3c5639-c6ed-4896-9209-e5cd75d3c2ba/llm_models_guide.md) for comprehensive documentation.
