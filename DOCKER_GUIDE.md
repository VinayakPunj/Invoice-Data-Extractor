# Docker Deployment Guide

## Prerequisites

1. **Install Docker Desktop** for Windows:
   - Download from: https://www.docker.com/products/docker-desktop/
   - Install and restart your computer if prompted
   - Ensure Docker Desktop is running (check system tray)

## Quick Start with Docker

### 1. Ensure your `.env` file is set up

Make sure you have a `.env` file with your Google API key:

```env
GOOGLE_API_KEY=your_actual_api_key_here
```

### 2. Build and Run with Docker Compose

Open PowerShell in your project directory and run:

```powershell
# Build and start the container
docker-compose up -d

# The app will be available at:
# http://localhost:8501
```

### 3. View Logs

To see what's happening:

```powershell
docker-compose logs -f
```

Press `Ctrl+C` to stop viewing logs (container keeps running).

### 4. Stop the Application

When you're done:

```powershell
docker-compose down
```

## Troubleshooting

### Docker Desktop Not Running
- Make sure Docker Desktop is running (check system tray icon)
- If you just installed it, restart your computer

### Port 8501 Already in Use
If you get a port conflict, stop the local Streamlit:
- Press `Ctrl+C` in the terminal where `streamlit run app.py` is running
- Then run `docker-compose up -d`

### Check Container Status

```powershell
# See running containers
docker ps

# See container logs
docker-compose logs invoice-iq
```

## Benefits of Using Docker

✅ **No manual installation** of Tesseract or Poppler  
✅ **Consistent environment** across different machines  
✅ **Easy deployment** to production  
✅ **Isolated dependencies** - won't affect your system  

## Data Persistence

Your data is automatically persisted in these folders:
- `./data/` - Database files
- `./logs/` - Application logs
- `./Invoices/` - Invoice files

These folders are mapped to the Docker container, so your data persists even if you restart the container.
