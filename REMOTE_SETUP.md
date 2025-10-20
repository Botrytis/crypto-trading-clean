# Remote Setup Guide

Run the Web UI on your desktop while connecting to the API server on a remote machine.

## Setup

### Option 1: Environment Variable (Recommended)

**On your desktop**, before starting the Web UI:

```bash
# Linux/macOS
export API_URL=http://165.22.71.91:8001
./scripts/start_web.sh

# Windows
set API_URL=http://165.22.71.91:8001
scripts\start_web.bat
```

### Option 2: .env File

Create a `.env` file in the project root on your desktop:

```bash
# Copy the example
cp .env.example .env

# Edit .env and set:
API_URL=http://165.22.71.91:8001
```

Then start the Web UI normally:
```bash
./scripts/start_web.sh
```

## Full Remote Setup Steps

**1. On the Server (165.22.71.91):**
```bash
cd crypto-trading-clean
source venv/bin/activate
./scripts/start_api.sh
```

The API will run on `http://0.0.0.0:8001` (accessible from any IP)

**2. On Your Desktop:**
```bash
# Pull latest code
git pull

# Setup if not done yet
./setup.sh   # or setup.bat on Windows

# Set API URL to point to server
export API_URL=http://165.22.71.91:8001

# Start Web UI
source venv/bin/activate
./scripts/start_web.sh
```

**3. Open Browser:**
```
http://localhost:8501
```

The web interface will connect to the API on the server.

## Firewall Requirements

Make sure port **8001** is open on the server:

```bash
# Check if port is accessible
curl http://165.22.71.91:8001/health

# Should return: {"status":"healthy"}
```

If not accessible, open the port:

```bash
# Ubuntu/Debian with ufw
sudo ufw allow 8001/tcp

# Or check firewall rules
sudo ufw status
```

## Troubleshooting

### Web UI says "API Offline"

1. **Check API is running on server:**
   ```bash
   ssh user@165.22.71.91
   curl http://localhost:8001/health
   ```

2. **Test from your desktop:**
   ```bash
   curl http://165.22.71.91:8001/health
   ```

3. **Check firewall:**
   - Port 8001 must be open
   - Server must bind to 0.0.0.0 (not just localhost)

### Connection timeout

- Check if server is reachable: `ping 165.22.71.91`
- Verify API is running: `ssh` to server and check processes
- Check cloud provider firewall/security groups

### CORS errors in browser console

The API already has CORS enabled for all origins. If you see CORS errors:
1. Clear browser cache
2. Try incognito mode
3. Check API logs for errors

## Local Development (Both on Same Machine)

If running both API and Web UI on the same machine:

```bash
# No need to set API_URL, it defaults to localhost:8001

# Terminal 1 - API
./scripts/start_api.sh

# Terminal 2 - Web UI
./scripts/start_web.sh
```

## Production Deployment

For production with HTTPS:

```bash
export API_URL=https://api.yourdomain.com
./scripts/start_web.sh
```

---

**Quick Reference:**

| Scenario | API URL |
|----------|---------|
| Local development | `http://localhost:8001` (default) |
| Remote development | `http://165.22.71.91:8001` |
| Production | `https://api.yourdomain.com` |

