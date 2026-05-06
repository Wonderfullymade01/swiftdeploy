# swiftdeploy

A declarative deployment CLI tool that generates Nginx and Docker Compose configurations from a single `manifest.yaml` file.

## Prerequisites

- Docker Desktop
- Python 3.x
- pip packages: `pip install pyyaml jinja2`

## Project Structure
swiftdeploy/
├── manifest.yaml          # Single source of truth
├── swiftdeploy            # CLI tool
├── Dockerfile             # API service image
├── app/
│   ├── main.py            # Flask API service
│   └── requirements.txt
├── templates/
│   ├── nginx.conf.j2      # Nginx template
│   └── docker-compose.yml.j2  # Compose template
└── README.md

## Setup

1. Clone the repo:
```bash
git clone https://github.com/Wonderfullymade01/swiftdeploy
cd swiftdeploy
```

2. Build the Docker image:
```bash
docker build -t wonderfullymade-api:latest .
```

3. Install Python dependencies:
```bash
pip install pyyaml jinja2
```

## Subcommand Walkthrough

### init
Parses `manifest.yaml` and generates `nginx.conf` and `docker-compose.yml`:
```bash
python swiftdeploy init
```

### validate
Runs 5 pre-flight checks before deployment:
```bash
python swiftdeploy validate
```
Checks:
- manifest.yaml exists and is valid YAML
- All required fields are present
- Docker image exists locally
- Nginx port is free
- nginx.conf is syntactically valid

### deploy
Runs init, starts the stack, and waits for health checks:
```bash
python swiftdeploy deploy
```

### promote
Switches between canary and stable modes with a rolling restart:
```bash
python swiftdeploy promote canary
python swiftdeploy promote stable
```

### teardown
Stops and removes all containers, networks, and volumes:
```bash
python swiftdeploy teardown
```
Add `--clean` to also delete generated config files:
```bash
python swiftdeploy teardown --clean
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Welcome message with mode, version, timestamp |
| `/healthz` | GET | Health check with uptime |
| `/chaos` | POST | Simulate degraded behaviour (canary mode only) |

## Chaos Modes (canary only)

```bash
# Slow responses
curl -X POST http://localhost:8080/chaos \
  -H "Content-Type: application/json" \
  -d '{"mode":"slow","duration":3}'

# Error rate
curl -X POST http://localhost:8080/chaos \
  -H "Content-Type: application/json" \
  -d '{"mode":"error","rate":0.5}'

# Recover
curl -X POST http://localhost:8080/chaos \
  -H "Content-Type: application/json" \
  -d '{"mode":"recover"}'
```

## Screenshots

All required screenshots (validate, deploy, promote, generated configs, nginx logs) are available here:
[Google Drive Screenshots](https://drive.google.com/drive/folders/14XGwV2dSIvRr3fh93Z0U6mDU9djSGsEA?usp=sharing) 

## Blog Post

Full technical deep dive:
[SwiftDeploy: How I Built a Tool That Writes Its Own Infrastructure Files](https://dev.to/wonderfullymade01/swiftdeploy-how-i-built-a-tool-that-writes-its-own-infrastructure-files-4cmp)