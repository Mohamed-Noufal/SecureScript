# Contributing to SecureScript

Thank you for your interest in contributing! 🎉

## 🌳 Development Workflow

We use **GitHub Flow**. Here's how to contribute:

### 1. Fork & Clone
```bash
git clone https://github.com/YOUR_USERNAME/SecureScript.git
cd SecureScript
git remote add upstream https://github.com/Mohamed-Noufal/SecureScript.git
```

### 2. Create a Feature Branch
```bash
git checkout develop
git pull upstream develop
git checkout -b feature/your-feature-name
```

### 3. Make Changes
- Write clean, documented code
- Follow existing code style
- Test locally before pushing

### 4. Commit & Push
```bash
git add .
git commit -m "feat: add amazing feature"
git push origin feature/your-feature-name
```

### 5. Open a Pull Request
- Go to GitHub and click "Compare & Pull Request"
- Target the `develop` branch (NOT `main`)
- Describe your changes clearly
- Wait for review!

---

## 📝 Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new security check for SQL injection
fix: resolve CORS issue with Vercel deployment
docs: update README with deployment steps
style: format code with black
refactor: simplify authentication logic
test: add unit tests for analysis endpoint
chore: update dependencies
```

---

## 🧪 Testing

Before submitting a PR:

### Frontend
```bash
cd frontend
npm run lint
npm run build  # Ensure no build errors
```

### Backend
```bash
cd backend
python -m pytest  # If tests exist
python -m black .  # Format code
```

---

## 🐛 Reporting Bugs

Found a bug? Please open an issue with:
- Clear title
- Steps to reproduce
- Expected vs actual behavior
- Screenshots (if applicable)

---

## 💡 Feature Requests

Have an idea? Open an issue with:
- Problem description
- Proposed solution
- Why it's valuable

---

## 📜 Code of Conduct

- Be respectful and constructive
- No spam or self-promotion
- Help others learn and grow

---

## 🙏 Thank You!

Every contribution, big or small, is appreciated. Let's build something amazing together! 🚀
