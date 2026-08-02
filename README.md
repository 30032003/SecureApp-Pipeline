# 🔐 SecureApp Pipeline

> End-to-End DevSecOps Pipeline using Flask, Docker, GitHub Actions, Terraform, AWS EC2, Prometheus, Grafana and Security Scanning Tools.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Flask](https://img.shields.io/badge/Flask-Web_App-black)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI/CD-success)
![Terraform](https://img.shields.io/badge/Terraform-IaC-purple)
![AWS](https://img.shields.io/badge/AWS-EC2-orange)
![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-E6522C)
![Grafana](https://img.shields.io/badge/Grafana-Dashboard-F46800)
![Trivy](https://img.shields.io/badge/Trivy-Container_Security-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📖 Project Overview

SecureApp is a vulnerable Flask-based web application developed to demonstrate the implementation of an end-to-end DevSecOps pipeline. The project integrates secure software development practices by automating security testing, containerization, infrastructure provisioning, continuous deployment, and monitoring.

The pipeline uses GitHub Actions to automate security scans, Docker to package the application, Terraform to provision AWS EC2 infrastructure, and Prometheus with Grafana for monitoring. Multiple security tools including Bandit, Semgrep, Gitleaks, pip-audit, Trivy, and OWASP ZAP are integrated to identify vulnerabilities throughout the Software Development Life Cycle (SDLC).

This project demonstrates how security can be incorporated into every stage of application development, making it suitable for learning modern DevSecOps practices.

## 🚀 Features

- 🔐 User Registration and Login Authentication
- 📤 Secure File Upload Functionality
- 🐳 Dockerized Flask Application
- ⚙️ Automated CI/CD Pipeline using GitHub Actions
- ☁️ Infrastructure Provisioning using Terraform
- 🖥️ Automated Deployment on AWS EC2
- 🔍 Static Application Security Testing (Bandit, Semgrep)
- 🔑 Secret Detection using Gitleaks
- 📦 Dependency Vulnerability Scanning using pip-audit
- 🛡️ Container Image Scanning using Trivy
- 🌐 Dynamic Application Security Testing (OWASP ZAP)
- 📊 Monitoring with Prometheus
- 📈 Visualization using Grafana
- 🚨 Demonstration of OWASP Top 10 Vulnerabilities

## 🛠️ Technology Stack

| Category | Technologies |
|----------|--------------|
| Programming Language | Python 3.12 |
| Framework | Flask |
| Database | SQLite |
| Containerization | Docker, Docker Compose |
| Version Control | Git, GitHub |
| CI/CD | GitHub Actions |
| Infrastructure as Code | Terraform |
| Cloud Platform | AWS EC2 |
| Monitoring | Prometheus, Grafana |
| Static Security Testing (SAST) | Bandit, Semgrep |
| Secret Scanning | Gitleaks |
| Dependency Scanning | pip-audit |
| Container Security | Trivy |
| Dynamic Security Testing (DAST) | OWASP ZAP |


## 📂 Project Structure

```text
SecureApp-Pipeline/
│
├── .github/workflows/        # GitHub Actions CI/CD pipeline
├── app/                      # Flask application source code
├── docs/                     # Documentation
├── monitoring/               # Prometheus & Grafana configuration
├── security/                 # Security scan reports
│   ├── bandit/
│   ├── semgrep/
│   ├── gitleaks/
│   ├── trivy/
│   └── zap/
├── templates/                # HTML templates
├── terraform/                # Infrastructure as Code
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 🏗️ Architecture Diagram

The following diagram illustrates the complete SecureApp DevSecOps workflow from code commit to automated deployment and security validation.

<p align="center">
  <img src="docs/architecture-diagram.svg" width="1000">
</p>


### Pipeline Flow

1. Developer pushes source code to GitHub.
2. GitHub Actions automatically starts the CI/CD pipeline.
3. Security scans are executed using:
   - Bandit
   - Semgrep
   - Gitleaks
   - pip-audit
   - Trivy
4. Docker image is built.
5. Terraform provisions AWS EC2 infrastructure.
6. SecureApp is automatically deployed on EC2 using SSH.
7. OWASP ZAP performs Dynamic Application Security Testing (DAST).
8. Prometheus collects application metrics.
9. Grafana visualizes monitoring dashboards.