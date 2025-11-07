# ResuMatch AI - Testing Guide

## Quick Test Checklist

### Backend API Tests

#### 1. Health Check
```bash
curl http://localhost:8001/api/health
# Expected: {"status":"healthy","database":"connected"}
```

#### 2. Register New User
```bash
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test User",
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

#### 3. Login
```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
# Save the access_token from response
```

#### 4. Get Current User (requires token)
```bash
curl http://localhost:8001/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 5. Create Profile
```bash
curl -X POST http://localhost:8001/api/profiles/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test User",
    "email": "test@example.com",
    "phone": "+1234567890",
    "location": "San Francisco, CA",
    "title": "Software Engineer"
  }'
```

#### 6. Add Job Description
```bash
curl -X POST http://localhost:8001/api/jobs/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Senior Software Engineer",
    "company": "Tech Corp",
    "location": "San Francisco, CA",
    "job_type": "Full-time",
    "description": "We are looking for a senior software engineer with Python and React experience..."
  }'
```

#### 7. Generate Resume
```bash
curl -X POST http://localhost:8001/api/resumes/generate \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": "template_1"
  }'
```

#### 8. Generate Interview Questions
```bash
# First get a job_id from step 6, then:
curl -X POST http://localhost:8001/api/interviews/generate-questions \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description_id": "YOUR_JOB_ID",
    "count": 10
  }'
```

### Frontend Tests

#### 1. Landing Page
- Navigate to http://localhost:3000
- Should see landing page with "Get Started Free" button
- Click "Get Started" should navigate to /register

#### 2. Registration
- Fill in the registration form
  - Full Name: Test User
  - Email: test@example.com
  - Password: testpass123
  - Confirm Password: testpass123
- Click "Create Account"
- Should automatically log in and navigate to dashboard

#### 3. Dashboard
- Check if welcome message appears with user name
- Verify all stat cards show correct data
- Click on "Complete Profile" quick action

#### 4. Profile Page
- Fill in personal information
  - Full Name
  - Email
  - Phone
  - Location
  - Professional Title
  - LinkedIn URL
- Add work experience (click "Add Experience")
- Add education (click "Add Education")
- Add skills
- Click "Save Profile"
- Should see success message

#### 5. Job Descriptions Page
- Click "Add Job" button
- Fill in job details:
  - Title: Senior Software Engineer
  - Company: Tech Corp
  - Location: San Francisco, CA
  - Description: (paste a real job description)
- Click "Save Job"
- Job card should appear with parsed keywords

#### 6. Resumes Page
- Click "Generate Resume"
- Select a job description (or leave empty for general)
- Select a template
- Click "Generate Resume"
- Resume card should appear with ATS score
- Try Preview and Download buttons

#### 7. Interview Prep Page
- Click "Generate Questions"
- Select a job description
- Set number of questions (default 25)
- Click "Generate Questions"
- Questions should appear categorized
- Click on a question to expand and see AI-generated answer

### Integration Tests

#### End-to-End Flow
1. Register new user
2. Complete profile with full details
3. Add 2-3 job descriptions
4. Generate resumes for each job
5. Generate interview questions for each job
6. Practice with questions
7. Verify all data persists after logout/login

### Performance Tests

#### Backend
```bash
# Test API response time
time curl http://localhost:8001/api/health

# Test multiple concurrent requests
for i in {1..10}; do
  curl http://localhost:8001/ &
done
wait
```

#### Frontend
- Check loading times for each page
- Verify no console errors in browser DevTools
- Test responsiveness on mobile viewport

### Database Tests

#### MongoDB Queries
```bash
# Connect to MongoDB
mongo mongodb://localhost:27017/resumatch

# List collections
show collections

# Count users
db.users.count()

# Find a user
db.users.findOne({email: "test@example.com"})

# Count profiles
db.profiles.count()

# Count job descriptions
db.job_descriptions.count()

# Count resumes
db.resumes.count()

# Count interview questions
db.interview_questions.count()
```

## Common Issues and Solutions

### Issue: Backend not starting
**Solution:** Check logs with `tail -f /var/log/supervisor/backend.err.log`

### Issue: Frontend not loading
**Solution:** 
1. Check if backend is running: `sudo supervisorctl status`
2. Check backend URL in frontend/.env

### Issue: CORS errors
**Solution:** Verify CORS_ORIGINS in backend/.env includes frontend URL

### Issue: Database connection failed
**Solution:** 
1. Check MongoDB is running: `sudo supervisorctl status mongodb`
2. Verify MONGO_URL in backend/.env

### Issue: 401 Unauthorized errors
**Solution:** 
1. Verify JWT token is being sent in Authorization header
2. Check if token has expired (default: 30 minutes)
3. Try logging in again

### Issue: Profile not saving
**Solution:**
1. Check if user is authenticated
2. Verify all required fields are filled
3. Check backend logs for validation errors

## Testing with Real Data

### Sample Job Descriptions
You can use real job postings from:
- LinkedIn Jobs
- Indeed
- AngelList
- Company career pages

### Sample Profile Data
Create realistic profiles with:
- 2-3 work experiences
- 1-2 education entries
- 5-10 technical skills
- 3-5 soft skills
- 1-2 certifications
- 1-2 projects

## Automated Testing (Future)

### Backend Tests (pytest)
```bash
cd /app/backend
pytest tests/
```

### Frontend Tests (Jest)
```bash
cd /app/frontend
npm test
```

### E2E Tests (Playwright)
```bash
cd /app/tests
npx playwright test
```

## Performance Benchmarks

### Expected Response Times
- Health check: < 50ms
- User registration: < 200ms
- Login: < 200ms
- Profile operations: < 300ms
- Job parsing: < 500ms
- Resume generation: < 2s (basic) / < 5s (with AI)
- Interview questions: < 3s (basic) / < 10s (with AI)

### Load Testing
- Concurrent users: Support 100+ concurrent users
- Database: Handle 10,000+ documents per collection
- API throughput: 1000+ requests/minute

## Next Steps for Testing

1. **Add Unit Tests** - Write pytest tests for backend logic
2. **Add Component Tests** - Write Jest tests for React components
3. **Add E2E Tests** - Write Playwright tests for user flows
4. **Set up CI/CD** - Automate testing in deployment pipeline
5. **Load Testing** - Use tools like Apache JMeter or Locust
6. **Security Testing** - Run security audits and penetration tests

## Test Coverage Goals

- Backend: > 80% code coverage
- Frontend: > 70% code coverage
- Critical paths: 100% coverage
- API endpoints: 100% coverage

---

**Last Updated:** November 7, 2025
**Version:** 1.0.0
