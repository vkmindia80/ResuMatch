# ResuMatch AI 🚀

An AI-powered platform that transforms user profiles into ATS-optimized resumes tailored to specific job descriptions, while providing comprehensive interview preparation including STAR-format Q&A.

## ✨ Features

### MVP (Phase 1) - Currently Implemented
- ✅ **User Authentication** - Secure registration, login with JWT tokens
- ✅ **Profile Management** - Comprehensive profile builder with completeness tracking
- ✅ **Job Description Parser** - Analyze and extract keywords from job postings
- ✅ **Resume Generator** - Create ATS-optimized resumes with multiple templates
- ✅ **Interview Preparation** - AI-generated questions with STAR-format answers
- ✅ **Responsive Dashboard** - Modern UI with dark mode support

### Coming Soon (Phase 2 & 3)
- 🔄 **AI-Powered Content Generation** - Using OpenAI GPT for personalized content
- 🔄 **Cover Letter Generator** - Tailored cover letters for each application
- 🔄 **LinkedIn Profile Optimizer** - Sync and optimize your LinkedIn presence
- 🔄 **Application Tracking** - Track all your job applications in one place
- 🔄 **Salary Negotiation Assistant** - Get market insights and negotiation tips

## 🏗️ Tech Stack

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **Database:** MongoDB with Motor (async driver)
- **Authentication:** JWT with bcrypt password hashing
- **API Documentation:** Auto-generated Swagger/OpenAPI
- **Validation:** Pydantic models

### Frontend
- **Framework:** React 18 with Hooks
- **Styling:** Tailwind CSS with custom design system
- **Routing:** React Router v6
- **HTTP Client:** Axios with interceptors
- **State Management:** React Context API
- **Icons:** Lucide React

### Infrastructure
- **Process Management:** Supervisor
- **Database:** MongoDB 5.0+
- **Server:** Uvicorn ASGI server
- **Development Server:** React Scripts (Webpack)

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ and Yarn
- MongoDB 5.0+
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/vkmindia80/ResuMatch.git
cd ResuMatch
```

2. **Backend Setup**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # Configure your environment variables
```

3. **Frontend Setup**
```bash
cd frontend
yarn install
cp .env.example .env  # Configure your environment variables
```

4. **Database Setup**
```bash
# Make sure MongoDB is running
sudo systemctl start mongodb
# Or if using supervisor:
sudo supervisorctl start mongodb
```

5. **Start Services**
```bash
# Start all services
sudo supervisorctl restart all

# Or start individually:
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
```

6. **Access the Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001
- API Documentation: http://localhost:8001/docs

## 📖 Documentation

- [Enhanced Roadmap](ROADMAP.md) - Detailed feature roadmap and technical architecture
- [Testing Guide](TESTING_GUIDE.md) - Comprehensive testing instructions
- [API Documentation](http://localhost:8001/docs) - Interactive Swagger UI

## 🔑 Environment Variables

### Backend (.env)
```bash
# MongoDB
MONGO_URL=mongodb://localhost:27017/resumatch

# JWT
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# OpenAI (for AI features)
OPENAI_API_KEY=your-openai-key
```

### Frontend (.env)
```bash
REACT_APP_BACKEND_URL=http://localhost:8001
REACT_APP_NAME=ResuMatch AI
REACT_APP_VERSION=1.0.0
```

## 🧪 Testing

### Manual Testing
```bash
# Test backend health
curl http://localhost:8001/api/health

# Register a user
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Test User","email":"test@example.com","password":"password123"}'

# Login
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for comprehensive testing instructions.

### Automated Tests (Coming Soon)
```bash
# Backend tests
cd backend && pytest

# Frontend tests
cd frontend && npm test

# E2E tests
cd tests && npx playwright test
```

## 📊 Project Structure

```
ResuMatch/
├── backend/                 # FastAPI backend
│   ├── routers/            # API route handlers
│   ├── models/             # Pydantic models
│   ├── utils/              # Utility functions
│   ├── database.py         # Database connection
│   ├── server.py           # Main FastAPI app
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── public/            # Static assets
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   ├── context/       # React context
│   │   └── utils/         # Utility functions
│   └── package.json       # Node dependencies
├── tests/                 # Test files
├── docs/                  # Documentation
├── ROADMAP.md            # Product roadmap
├── TESTING_GUIDE.md      # Testing guide
└── README.md             # This file
```

## 🎯 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user

### Profile
- `GET /api/profiles/me` - Get user profile
- `POST /api/profiles/me` - Create profile
- `PUT /api/profiles/me` - Update profile
- `GET /api/profiles/completeness` - Get profile completeness score

### Job Descriptions
- `POST /api/jobs/` - Create job description
- `GET /api/jobs/` - Get all job descriptions
- `GET /api/jobs/{id}` - Get specific job
- `DELETE /api/jobs/{id}` - Delete job

### Resumes
- `POST /api/resumes/generate` - Generate resume
- `GET /api/resumes/` - Get all resumes
- `GET /api/resumes/{id}` - Get specific resume
- `DELETE /api/resumes/{id}` - Delete resume
- `GET /api/resumes/templates/list` - Get available templates

### Interview Preparation
- `POST /api/interviews/generate-questions` - Generate questions
- `GET /api/interviews/questions` - Get questions
- `GET /api/interviews/categories` - Get question categories

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- **Initial Development** - ResuMatch AI Team

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- React team for the amazing UI library
- MongoDB for the flexible database
- All open-source contributors

## 📞 Support

For support, email support@resumatch.ai or join our Slack channel.

## 🗺️ Roadmap

See [ROADMAP.md](ROADMAP.md) for our detailed product roadmap and upcoming features.

## 📈 Status

- **MVP Status:** ✅ Complete
- **Version:** 1.0.0
- **Last Updated:** November 7, 2025
- **Active Development:** Yes

---

Made with ❤️ by ResuMatch AI Team
