# ☁️ Cloud Architecture Comparison

## 1. Container-Based (App Runner)
- **Concept**: A server that stays running 24/7.
- **Pros**: Handles long tasks, standard Docker environment.
- **Cons**: You pay for idle time.

## 2. Serverless (Lambda + S3 + CloudFront)
- **Concept**: Parts wake up only when needed.
- **Pros**: Pay-per-request (Free if not used), scales instantly.
- **Cons**: "Cold starts" (first request is slow), 15-minute time limit.

## 🌉 Why Mangum?
FastAPI expects a persistent connection. Lambda is event-based. Mangum translates between the two.
