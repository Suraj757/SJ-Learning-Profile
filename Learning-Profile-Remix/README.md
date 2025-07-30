# Begin Learning Profile - Day 1 Back to School

A comprehensive learning assessment platform that creates a bridge between teachers and parents to understand each child's unique learning style from the first day of school.

## 🎯 Key Features

- **Teacher-First Distribution**: Teachers assign profiles to parents during Back to School week
- **Dual Results System**: Separate insights for teachers (classroom strategies) and parents (Begin products + home activities)
- **Classroom-Focused Assessment**: 24 questions based on observable classroom behaviors
- **Begin Ecosystem Integration**: Personalized recommendations across apps, kits, classes, and tutoring
- **Secure Assignment Workflow**: Token-based URLs for controlled access and tracking

## 🚀 Quick Start

### Local Development
```bash
pip install -r requirements.txt
streamlit run main.py
```

### Web Deployment
Deploy on [Streamlit Cloud](https://share.streamlit.io) or [Replit](https://replit.com) for instant web access.

## 🎭 Demo Flow

1. **Teacher Registration**: Create educator account and assign student profiles
2. **Parent Assessment**: Complete 5-minute learning style questionnaire via teacher assignment
3. **Dual Results**: Teachers get classroom strategies, parents get Begin product recommendations
4. **Collaboration**: Shared understanding enables better home-school learning support

## 📋 Architecture

- **Frontend**: Streamlit web application with custom CSS styling
- **Backend**: Python with PostgreSQL database (optional - works without DB for demos)
- **Authentication**: Email-based teacher accounts with secure assignment tokens
- **Recommendations**: AI-driven matching of learning profiles to Begin products

## 🔧 Configuration

The app works out-of-the-box for demos. For production deployment:
- Set `DATABASE_URL` environment variable for PostgreSQL
- Update email configurations for teacher assignments
- Configure domain settings for assignment URLs

## 📚 Documentation

- `PRODUCT_FEATURES.md` - Comprehensive feature documentation
- `DEMO_GUIDE.md` - Step-by-step demo instructions
- `DEPLOYMENT_OPTIONS.md` - Web deployment guide
- `Revised_Product_Strategy_Day1_Back_to_School.md` - Strategic framework

---

**Built for Begin's mission to help every child discover their unique learning language.**