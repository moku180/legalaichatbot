# Legal AI SaaS Platform

**Production-Ready Legal Intelligence SaaS with Multi-Agent RAG System**

A comprehensive legal AI platform featuring 8 specialized AI agents, multi-tenant architecture, enterprise security, and jurisdiction-aware legal research.

---

## 🎯 Product Overview

**Legal AI SaaS** is an enterprise-grade platform that provides:

- **Multi-Agent Legal Intelligence**: 8 specialized AI agents for comprehensive legal analysis
- **RAG-Based Research**: Retrieval-Augmented Generation with FAISS vector store
- **Multi-Tenant Architecture**: Complete data isolation per organization
- **Enterprise Security**: JWT authentication, RBAC, rate limiting
- **Jurisdiction-Aware**: Filters by jurisdiction, court level, and document type
- **Citation-Backed Responses**: All legal claims include proper citations
- **Safety Guardrails**: Refuses personalized legal advice, detects jurisdiction mismatches

**Target Customers**: Law firms, legal research startups, compliance teams, enterprises

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  Login │ Workspace │ Chat │ Documents │ Analytics           │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTPS/WSS
┌────────────────────▼────────────────────────────────────────┐
│                     Nginx Reverse Proxy                      │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   FastAPI Backend                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Multi-Agent System                       │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │
│  │  │Orchestr. │  │ Safety   │  │Verificat.│           │   │
│  │  └──────────┘  └──────────┘  └──────────┘           │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │
│  │  │Statutory │  │Case Law  │  │Contract  │           │   │
│  │  └──────────┘  └──────────┘  └──────────┘           │   │
│  │  ┌──────────┐  ┌──────────┐                         │   │
│  │  │Compliance│  │Retriever │                         │   │
│  │  └──────────┘  └──────────┘                         │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              RAG Pipeline                             │   │
│  │  Document → Chunker → Embeddings → FAISS (per org)   │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────┬─────────────────────────┬─────────────────────┘
             │                         │
┌────────────▼──────────┐  ┌──────────▼──────────┐
│   PostgreSQL          │  │   Redis             │
│   (Users, Docs, etc.) │  │   (Sessions, Rate)  │
└───────────────────────┘  └─────────────────────┘
```

---

## 🤖 AI Agents

### 1. **Orchestrator Agent**
- Intent classification
- Agent routing
- Cost-aware execution

### 2. **Safety & Policy Agent**
- Refuses personalized legal advice
- Detects jurisdiction mismatches
- Blocks illegal activity requests
- Enforces legal disclaimers

### 3. **Retriever Agent**
- Metadata-aware vector search
- Tenant-isolated retrieval
- MMR for diverse results

### 4. **Statutory Interpretation Agent**
- Interprets acts, sections, articles
- Plain-language explanations
- Cross-reference detection

### 5. **Case Law Research Agent**
- Precedent extraction
- Ratio decidendi identification
- Binding vs. persuasive authority

### 6. **Contract Analysis Agent**
- Clause extraction
- Risk detection
- Obligation mapping

### 7. **Compliance & Regulatory Agent**
- Rule matching
- Compliance verdicts
- Rationale generation

### 8. **Verification & Citation Agent**
- Hallucination detection
- Citation enforcement
- Confidence scoring

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- **Google Gemini API key** (FREE - Get yours at [Google AI Studio](https://aistudio.google.com/apikey))

### Setup

1. **Clone and navigate to project**:
   ```bash
   cd legalchatbot
   ```

2. **Create environment file**:
   ```bash
   cp .env.example .env
   ```

3. **Get your FREE Gemini API key**:
   - Visit [Google AI Studio](https://aistudio.google.com/apikey)
   - Click "Get API Key" → "Create API key"
   - Copy your API key

4. **Edit `.env` and add your API keys**:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   SECRET_KEY=your_secret_key_here_min_32_chars
   ```

4. **Start all services**:
   ```bash
   docker-compose up --build
   ```

5. **Access the application**:
   - Frontend: http://localhost
   - API Docs: http://localhost/api/v1/docs
   - Health Check: http://localhost/health

### First-Time Setup

1. Register a new organization and user at http://localhost
2. Upload legal documents (PDF, DOCX, TXT)
3. Start querying the legal AI assistant

---

## 📁 Project Structure

```
legalchatbot/
├── backend/
│   ├── app/
│   │   ├── agents/          # 8 AI agents
│   │   ├── api/             # FastAPI routes
│   │   ├── core/            # Config, security, dependencies
│   │   ├── db/              # Database setup
│   │   ├── middleware/      # Tenant isolation, rate limiting
│   │   ├── models/          # SQLAlchemy models
│   │   ├── rag/             # RAG pipeline
│   │   ├── services/        # LLM, embedding services
│   │   └── main.py          # FastAPI app
│   └── requirements.txt
├── frontend/                # React application
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🔐 Security Features

- **JWT Authentication**: Secure token-based auth
- **RBAC**: Admin, Lawyer, Researcher, Viewer roles
- **Multi-Tenancy**: Complete data isolation per organization
- **Rate Limiting**: Per-user and per-organization limits
- **Input Validation**: Pydantic schemas
- **Password Hashing**: bcrypt

---

## 📊 Usage & Billing

The platform tracks:
- Token usage per query
- Cost estimation (input/output tokens)
- Query history with timestamps
- Per-organization analytics

---

## ⚖️ Legal Compliance

### Mandatory Disclaimer

All responses include:
> "This platform provides general legal information and not legal advice. Consult a qualified attorney for specific legal matters."

### Safety Guardrails

- ❌ Refuses personalized legal advice
- ❌ Blocks illegal activity requests
- ❌ Warns on jurisdiction mismatches
- ✅ Requires citations for all claims
- ✅ Confidence scoring for responses

---

## 🔧 Configuration

### Environment Variables

See `.env.example` for all configuration options:

**Required**:
- `GEMINI_API_KEY`: Google Gemini API key (FREE from Google AI Studio)
- `SECRET_KEY`: JWT secret (min 32 chars)

**Optional**:
- `GEMINI_MODEL`: LLM model (default: gemini-2.0-flash-exp)
- `CHUNK_SIZE`: Document chunk size (default: 600 tokens)
- `RATE_LIMIT_PER_MINUTE`: Rate limit (default: 60)

---

## 📈 Scaling Strategy

### Horizontal Scaling

- **Backend**: Stateless FastAPI - scale with load balancer
- **Database**: PostgreSQL read replicas
- **Vector Store**: Shard FAISS indexes by organization
- **Redis**: Redis Cluster for sessions

### Performance Optimization

- **Caching**: Redis for frequent queries
- **Async Processing**: Celery for document ingestion
- **Connection Pooling**: SQLAlchemy pool
- **Batch Embeddings**: Reduce API calls

---

## 🧪 Testing

### Run Tests

```bash
cd backend
pytest tests/ -v --cov=app
```

### Test Coverage

- Unit tests for all agents
- Integration tests for RAG pipeline
- API endpoint tests
- Multi-tenancy isolation tests

---

## 📝 API Documentation

Interactive API docs available at: http://localhost/api/v1/docs

### Key Endpoints

**Authentication**:
- `POST /api/v1/auth/register` - Register user & organization
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Current user info

**Documents**:
- `POST /api/v1/documents/upload` - Upload legal document
- `GET /api/v1/documents` - List documents
- `DELETE /api/v1/documents/{id}` - Delete document

**Chat**:
- `POST /api/v1/chat/query` - Submit legal query

---

## 🛠️ Development

### Local Development (without Docker)

1. **Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

---

## 📄 License

Proprietary - All rights reserved

---

## 🤝 Support

For enterprise support, custom deployments, or feature requests, contact your account manager.

---

## 🎯 Roadmap

- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Custom LLM fine-tuning
- [ ] Mobile app (iOS/Android)
- [ ] API rate limit tiers
- [ ] Webhook integrations
- [ ] SSO/SAML support

---

**Built with ❤️ for the legal industry**
