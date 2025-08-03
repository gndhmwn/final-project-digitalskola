# Final Project Cloud Engineer - DigitalSkola

## 🐳 Docker Compose Deployment

### 📋 Prerequisites
- **OS**: Ubuntu 20.04 LTS or later
- **Docker**: Version 20.10.12 or higher
- **Docker Compose**: Version 2.5.0 or higher
- **Resources**: Minimum 4GB RAM, 2 vCPUs

### Deployment Steps

1. ✅  Clone Repository:
   ```bash
   git clone https://github.com/gndhmwn/final-project-digitalskola.git

2. ✅ Enter Project Directory:
   ```bash
   cd final-project-digitalskola
   
3.a. ✅ Start Containers:
   ```bash
   docker compose -f docker-compose.staging.yml up -d --> for staging
   docker compose -f docker-compose.prod.yml up -d --> for production
