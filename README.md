# cms-monolith

## Purpose

The CMS Monolith is an internal application used by a content team to manage platform data and workflows.

It is intentionally deployed outside of Kubernetes as a standalone service running on EC2.

It is responsible for:
- managing internal content and operational data
- serving internal users (non-public system)
- running as a containerized application on EC2
- supporting simple deployment and operational workflows

It is not responsible for:
- handling public API traffic
- participating in the GitOps deployment model
- running within the EKS cluster
- managing infrastructure or deployment state

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

## Deployment Model

This service follows a traditional CI/CD model and does NOT use GitOps.

Instead:

- Jenkins builds the Docker image
- The image is deployed directly to an EC2 instance
- Deployment scripts manage container lifecycle (start, stop, restart, rollback)

This creates a hybrid architecture where:

- Microservices (API + AI) -> deployed via GitOps on EKS
- CMS Monolith -> deployed directly to EC2 via Jenkins

This decision prioritizes simplicity for an internal, low-concurrency system.

---

## CI/CD Model

- Built and deployed via Jenkins
- Containerized using Docker
- Deployed directly to EC2 (non-Kubernetes workload)
- Uses deployment scripts for lifecycle management

This service intentionally uses a different delivery model than the EKS-based microservices.

It reflects a real-world hybrid system where not all workloads require Kubernetes orchestration.

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

## Key Architectural Decisions

- Deployed outside Kubernetes to reduce operational complexity
- Uses EC2 + Docker instead of EKS for a simpler internal workload
- Separate CI/CD pipeline (Jenkins) from microservices (GitHub Actions)
- Hybrid architecture allows selecting the right tool for each workload

This demonstrates that not all services need Kubernetes, especially for internal systems with lower scaling requirements.

---

## Future Enhancements

- Push Docker images to ECR for centralized registry management
- Improve deployment automation and rollback safety
- Add runtime monitoring and observability
- Strengthen CI/CD pipeline validation and reliability