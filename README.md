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