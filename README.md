## File Tree
```
📦backend
 ┣ 📂.git
 ┣ 📂.github
 ┃ ┗ 📂workflows
 ┃ ┃ ┗ 📜ci-cd.yml
 ┣ 📂helm
 ┃ ┣ 📂apps
 ┃ ┃ ┣ 📂templates
 ┃ ┃ ┃ ┗ 📜backend-application.yaml
 ┃ ┃ ┣ 📜Chart.yaml
 ┃ ┃ ┗ 📜values.yaml
 ┃ ┗ 📂backend
 ┃ ┃ ┣ 📂templates
 ┃ ┃ ┃ ┣ 📜deployment.yaml
 ┃ ┃ ┃ ┗ 📜service.yaml
 ┃ ┃ ┣ 📜.helmignore
 ┃ ┃ ┣ 📜Chart.yaml
 ┃ ┃ ┗ 📜values.yaml
 ┣ 📂routers
 ┃ ┣ 📜cognito.py
 ┃ ┣ 📜diary.py
 ┃ ┣ 📜s3.py
 ┃ ┣ 📜todo.py
 ┃ ┗ 📜user.py
 ┣ 📜.env
 ┣ 📜.gitignore
 ┣ 📜app.py
 ┣ 📜database.py
 ┣ 📜Dockerfile
 ┣ 📜functions.py
 ┣ 📜models.py
 ┣ 📜package-lock.json
 ┣ 📜README.md
 ┗ 📜requirements.txt
 ```

 ## CI/CD 파이프라인
1. GitHub에 코드를 Push
2. `.github/workflows/ci-cd.yaml` 이 실행 되면서 GitHub Actions 실행
3. GitHub Actions에서 AWS ECR로 이미지 푸시
4. AWS ECR에 이미지가 푸시된 것을 ArgoCD에서 감지 후 푸시된 이미지로 EKS에 배포


## 사용된 AWS 서비스
* AWS IAM
* AWS Cognito
* AWS RDS
* AWS S3
* AWS ECR
* AWS EKS
* AWS EC2
* AWS VPC
* AWS Route 53
* AWS WAF
* AWS CloudWatch