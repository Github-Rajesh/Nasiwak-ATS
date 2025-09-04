# AI Resume Matcher & Ranking Tool

A intelligent web application that helps HR professionals and recruiters efficiently shortlist and rank candidates by matching resumes against job descriptions using advanced NLP and optional AI-powered matching.

## 🌟 Features

- **Smart Resume Parsing**: Extract text from PDF, DOC, DOCX, and TXT files
- **Intelligent Matching**: Advanced algorithms to match resumes with job descriptions
- **AI-Powered Enhancement**: Optional OpenAI integration for semantic matching
- **Comprehensive Scoring**: Multi-factor scoring system for candidate ranking
- **User-Friendly Interface**: Clean, responsive web interface
- **Bulk Processing**: Handle multiple resumes simultaneously
- **Export Results**: Download matching results for further analysis

## 🚀 Live Demo

The application is deployed and accessible at: **[Your Render URL will appear here after deployment]**

## 🛠️ Quick Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### Prerequisites
- GitHub account
- Render.com account (free tier available)
- (Optional) OpenAI API key for enhanced matching

### Deployment Steps

1. **Fork/Clone this repository**
2. **Push to your GitHub account**
3. **Deploy to Render:**
   - Option A: Use the "Deploy to Render" button above
   - Option B: Follow detailed instructions in [DEPLOYMENT.md](DEPLOYMENT.md)

## 🏃‍♂️ Local Development

### Prerequisites
- Python 3.11+
- pip package manager

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/ai-resume-matcher.git
   cd ai-resume-matcher
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

6. **Access the application**
   Open your browser to `http://localhost:5000`

## 📊 How It Works

1. **Upload Resumes**: Drag and drop or select multiple resume files
2. **Select Job Description**: Choose from pre-loaded job descriptions or upload new ones
3. **Configure Matching**: Set parameters like number of top candidates, similarity threshold
4. **AI Enhancement**: Optionally enable AI-powered semantic matching
5. **Get Results**: View ranked candidates with detailed scoring and explanations

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `FLASK_ENV` | Yes | Application environment (`development`/`production`) | `production` |
| `SECRET_KEY` | Yes | Flask secret key for sessions | - |
| `DATABASE_URL` | Yes | Database connection string | `sqlite:///rsart.db` |
| `OPENAI_API_KEY` | No | OpenAI API key for AI features | - |
| `OPENAI_MODEL` | No | OpenAI model to use | `gpt-4o-mini` |
| `USE_AI_MATCHING` | No | Enable AI matching features | `True` |

### Supported File Formats

- **Resumes**: PDF, DOC, DOCX, TXT (up to 16MB each)
- **Job Descriptions**: PDF, DOC, DOCX, TXT

## 🎯 Matching Algorithm

The application uses a multi-layered approach:

1. **Text Extraction**: Clean text extraction from various file formats
2. **NLP Processing**: Advanced natural language processing using spaCy
3. **Keyword Matching**: Skills, technologies, and domain-specific terms
4. **Semantic Analysis**: Context-aware matching using sentence transformers
5. **AI Enhancement**: Optional GPT-powered semantic understanding
6. **Scoring**: Weighted scoring across multiple factors

## 🏗️ Architecture

```
├── app/
│   ├── controllers/     # Route handlers
│   ├── services/        # Business logic
│   ├── models/          # Database models
│   ├── utils/           # Utility functions
│   ├── templates/       # HTML templates
│   └── static/          # CSS, JS, images
├── data/
│   ├── uploaded_resumes/    # Resume storage
│   └── job_descriptions/    # Job description storage
├── logs/                # Application logs
└── tests/               # Test cases
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app

# Run specific test
python -m pytest tests/test_matching.py
```

## 📈 Performance

- **Free Tier**: Handles ~50 resumes efficiently
- **Paid Tier**: Scales to hundreds of resumes
- **AI Features**: Optional, can be disabled for faster processing
- **Database**: SQLite for development, PostgreSQL for production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [DEPLOYMENT.md](DEPLOYMENT.md) for deployment help
- **Issues**: [GitHub Issues](https://github.com/your-username/ai-resume-matcher/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/ai-resume-matcher/discussions)

## 🎉 Acknowledgments

- Built with Flask and modern Python libraries
- Powered by spaCy for NLP processing
- Enhanced with OpenAI for semantic understanding
- Deployed on Render for reliable hosting

---

Made with ❤️ for better hiring processes