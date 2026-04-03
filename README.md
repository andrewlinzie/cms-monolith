# cms-monolith

## Purpose
Houses the internal CMS application used by the content team.

---

## Contains
- CMS application code
- Dockerfile
- Jenkinsfile
- EC2 deployment scripts

---

## Does Not Contain
- Kubernetes manifests
- GitOps deployment state
- Terraform infrastructure code
- Microservice Helm charts

---

## Local Development

### Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
````

### Run the application

```bash
uvicorn src.app:app --reload --port 8002
```

### Health check

```bash
curl http://127.0.0.1:8002/health
```

---

## Docker Usage

### Build image

```bash
docker build -t cms-monolith:dev .
```

### Run container

```bash
docker run --rm -p 8002:8002 cms-monolith:dev
```

---

## Operational Commands

### Health check

```bash
./scripts/health_check.sh
```

### Deploy

```bash
IMAGE_REPO=cms-monolith IMAGE_TAG=dev ./scripts/deploy.sh
```

### Restart

```bash
./scripts/restart.sh
```

### Rollback

```bash
ROLLBACK_TAG=previous ./scripts/rollback.sh
```

---

## Runtime Assumptions

* Container name: `cms-monolith`
* Default port: `8002`
* Health endpoint: `/health`
* Image format: `cms-monolith:<tag>`

---

## CI/CD Model

* Built and deployed via Jenkins
* Containerized using Docker
* Deployed to EC2 (non-Kubernetes workload)
* Separate delivery path from EKS microservices

---

## Future Phases

* Jenkins pipeline execution
* ECR image push
* EC2 instance provisioning (Terraform)
* Runtime monitoring and observability