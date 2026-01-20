# 💰 AWS Serverless: Costs, Scaling, and Common Mistakes

This guide covers everything you need to know about AWS costs, how scaling works, common mistakes, and how to deploy your MVP for free or cheaply.

---

## 💵 Part 1: AWS Pricing (2024/2025)

### Lambda (Backend)
**Always Free (Never expires!):**
- ✅ 1 million requests/month
- ✅ 400,000 GB-seconds of compute time
- ✅ 100 GiB of HTTP response streaming

**After Free Tier:**
- $0.20 per 1 million requests
- $0.0000166667 per GB-second (x86)
- $0.0000133334 per GB-second (ARM/Graviton2 - 34% cheaper!)

**Example for your app:**
- If 1 request takes 2 seconds with 512MB RAM:
  - Free tier: ~200,000 requests/month
  - After that: $0.20 per million + compute costs

---

### S3 (Frontend Storage)
**First 12 Months Free:**
- ✅ 5 GB storage
- ✅ 20,000 GET requests
- ✅ 2,000 PUT requests

**After Free Tier:**
- $0.023 per GB/month (first 50 TB)
- $0.0004 per 1,000 GET requests
- $0.005 per 1,000 PUT requests

**Example for your app:**
- Your Next.js build is probably ~50MB
- Cost: **$0.001/month** (basically free!)

---

### CloudFront (CDN)
**Always Free:**
- ✅ 1 TB data transfer out/month
- ✅ 10 million HTTP/HTTPS requests
- ✅ 2 million CloudFront Function invocations

**After Free Tier:**
- $0.085 per GB (first 10 TB)

**Example for your app:**
- 1 TB = ~1 million page loads
- Most MVPs stay in free tier!

---

### API Gateway
**First 12 Months Free:**
- ✅ 1 million HTTP API calls
- ✅ 1 million REST API calls

**After Free Tier:**
- HTTP API: $1.00 per million requests
- REST API: $3.50 per million requests

**💡 Pro Tip:** Use HTTP API (not REST) - it's 70% cheaper!

---

## 📊 Part 2: Total Cost for Your MVP

### Scenario: 1,000 users/month, each analyzing 5 code snippets

| Service | Usage | Cost |
|---------|-------|------|
| **Lambda** | 5,000 requests × 2s × 512MB | **FREE** (within 1M requests) |
| **S3** | 50MB storage + 5,000 GET requests | **FREE** (within 5GB + 20K requests) |
| **CloudFront** | 5,000 page loads (~500MB transfer) | **FREE** (within 1TB) |
| **API Gateway** | 5,000 API calls | **FREE** (within 1M calls) |
| **Total** | | **$0.00/month** ✅ |

### Scenario: 100,000 users/month (500K requests)

| Service | Usage | Cost |
|---------|-------|------|
| **Lambda** | 500K requests × 2s × 512MB | **~$0.10** |
| **S3** | 50MB storage + 500K GET requests | **~$0.20** |
| **CloudFront** | 500K page loads (~50GB transfer) | **FREE** (within 1TB) |
| **API Gateway** | 500K API calls | **$0.50** |
| **Total** | | **~$0.80/month** 🎉 |

---

## ⚠️ Part 3: Common Mistakes (and How to Avoid Them)

### 1. **Over-Provisioning Lambda Memory**
❌ **Mistake:** Setting Lambda to 3GB when it only needs 512MB.
✅ **Fix:** Start with 512MB. Use **AWS Lambda Power Tuning** to find the sweet spot.

### 2. **Excessive Logging**
❌ **Mistake:** Logging every single request at DEBUG level in production.
✅ **Fix:** 
```python
# In production, use INFO or ERROR only
logging.basicConfig(level=logging.INFO)
```
- Set CloudWatch log retention to 30 days (not forever!).

### 3. **No Billing Alarms**
❌ **Mistake:** Not knowing you're being charged until the bill arrives.
✅ **Fix:** 
1. Go to AWS Console > **CloudWatch** > **Alarms**.
2. Create a billing alarm for $5, $10, $50.

### 4. **Not Using Caching**
❌ **Mistake:** Every request hits Lambda, even for the same data.
✅ **Fix:** Use CloudFront caching for static content (your React app is already cached!).

### 5. **Synchronous Lambda-to-Lambda Calls**
❌ **Mistake:**
```python
# Lambda A calls Lambda B and waits
response = lambda_client.invoke(FunctionName='B')
```
You pay for **both** functions' execution time!

✅ **Fix:** Use **SQS** (queue) or **SNS** (pub/sub) for async communication.

### 6. **Ignoring Cold Starts**
❌ **Mistake:** Not understanding why the first request is slow.
✅ **Fix:** 
- Keep dependencies small.
- Use Python or Node.js (faster cold starts than Java).
- For critical APIs, use **Provisioned Concurrency** (costs extra, but eliminates cold starts).

### 7. **Using REST API Instead of HTTP API**
❌ **Mistake:** Choosing REST API Gateway by default.
✅ **Fix:** Use **HTTP API** - it's 70% cheaper and faster!

---

## 🚀 Part 4: How Scaling Works

### Does it happen automatically?
**YES!** 100% automatic. You don't deploy "another version."

### How Lambda Scales:
1. **User 1** sends a request → Lambda creates **Instance 1**.
2. **User 2** sends a request at the same time → Lambda creates **Instance 2**.
3. **1,000 users** send requests → Lambda creates **1,000 instances** (up to your concurrency limit).

### Scaling Limits:
- **Default:** 1,000 concurrent executions per region.
- **Burst:** 500-3,000 requests/second initially.
- **After burst:** +500 instances/minute.

### What if you hit the limit?
- Requests are **throttled** (delayed) until an instance becomes available.
- You can request a limit increase from AWS Support (free).

### Do you need to redeploy?
**NO!** Scaling is automatic. You only redeploy when you change your **code**.

---

## 💡 Part 5: Free/Cost-Efficient MVP Deployment

### Strategy 1: Stay in Free Tier (Recommended for MVP)
✅ Use the serverless architecture we built.
✅ Lambda, S3, CloudFront, API Gateway all have generous free tiers.
✅ **Cost:** $0/month for up to 1M requests.

### Strategy 2: Use Amplify for Frontend (Alternative)
Instead of S3 + CloudFront + GitHub Actions, use **AWS Amplify**:
- Connects directly to your GitHub repo.
- Auto-builds and deploys on every push.
- **Free Tier:** 1,000 build minutes/month, 15GB storage, 5GB served/month.
- **Cost:** $0/month for small MVPs.

### Strategy 3: Hybrid (Cheapest for High Traffic)
- **Frontend:** Vercel or Netlify (free tier is very generous).
- **Backend:** AWS Lambda (as we configured).
- **Why?** Vercel/Netlify have better free tiers for static sites.

---

## 🎯 Part 6: Cost Optimization Checklist

Before deploying, make sure you:
- [ ] Set Lambda memory to 512MB (not more).
- [ ] Use HTTP API (not REST API).
- [ ] Set CloudWatch log retention to 30 days.
- [ ] Enable CloudFront caching.
- [ ] Set up billing alarms ($5, $10, $50).
- [ ] Use Graviton2 (ARM) for Lambda if possible.
- [ ] Compress large responses.
- [ ] Use environment variables (not hardcoded secrets).

---

## 📈 Part 7: When to Upgrade

You should consider upgrading from serverless when:
- ❌ You have **consistent** high traffic (millions of requests/day).
- ❌ Your functions run for **more than 15 minutes**.
- ❌ You need **stateful** connections (e.g., WebSockets for hours).

For an MVP security analyzer? **Serverless is perfect!** 🎉

---

## 🆓 Part 8: Your MVP Cost Estimate

**Realistic MVP (first 6 months):**
- 100-500 users
- 5-10 analyses per user per month
- Total: 500-5,000 requests/month

**Expected Cost:** **$0.00/month** (within free tier)

**Even if you go viral (100K users):**
- 500K requests/month
- **Expected Cost:** **~$1-2/month**

---

## 🎓 Key Takeaways

1. **Serverless is CHEAP** for MVPs (often free!).
2. **Scaling is AUTOMATIC** - you don't do anything.
3. **Common mistakes** are about over-provisioning and logging.
4. **Free tier is generous** - Lambda alone gives 1M requests/month forever.
5. **You only pay for what you use** - no idle costs.

Happy deploying! 🚀
