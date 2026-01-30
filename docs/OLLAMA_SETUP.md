# Ollama Setup Guide

Ollama allows you to run open-source large language models (LLMs) locally on your own machine. This is a great alternative to paid APIs like Gemini or OpenAI, providing privacy and cost savings.

## 1. Install Ollama

- **Windows**: Download the installer from [ollama.com/download/windows](https://ollama.com/download/windows)
- **macOS**: Download from [ollama.com/download/mac](https://ollama.com/download/mac)
- **Linux**: Run `curl -fsSL https://ollama.com/install.sh | sh`

## 2. Pull a Model

Before you can use a model in InvoiceIQ, you need to "pull" (download) it using the command line:

```bash
# Recommended for balanced speed and quality
ollama pull llama3.2

# Highly recommended for quality (larger download)
ollama pull gemma2

# Lightweight and fast
ollama pull phi3
```

## 3. Verify Ollama is Running

Ensure the Ollama service is running. You should see the Ollama icon in your system tray (macOS/Windows) or verify via terminal:

```bash
ollama list
```

## 4. Using with Docker

If you are running InvoiceIQ inside a Docker container, `localhost:11434` will not work because it refers to the container itself.

1. **Host Configuration**: By default, Ollama only listens on `127.0.0.1`. To allow access from Docker, you may need to set the `OLLAMA_HOST` environment variable to `0.0.0.0` on your host machine.
   - **Windows**: Right-click "This PC" > Properties > Advanced System Settings > Environment Variables > New > `OLLAMA_HOST` = `0.0.0.0`. Restart Ollama.
2. **Internal URL**: Use `http://host.docker.internal:11434` as the base URL.
3. **Docker Compose**: The provided `docker-compose.yml` is already configured to map `host.docker.internal` to your machine's IP.

## 5. Using in InvoiceIQ

1. Start the InvoiceIQ application.
2. In the sidebar, select **Ollama (Local)** as the Provider.
3. If Ollama is running, you will see a green checkmark: `✓ Connected to Ollama`.
4. Select your pulled model (e.g., `llama3.2:latest`) from the dropdown.
5. Upload an invoice and start extracting!

## Troubleshooting

- **Connection Error**: If you see `❌ Could not connect to Ollama`, ensure the Ollama application is open and running.
- **No Models Found**: Run `ollama list` in your terminal to ensure you have successfully pulled at least one model.
- **Performance**: Local models run on your CPU/GPU. If extraction is slow, try a smaller model like `phi3` or `llama3.2:1b`.
