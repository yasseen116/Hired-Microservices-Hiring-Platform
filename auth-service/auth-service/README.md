# Authentication Service API

A microservice for user authentication and profile management, built with FastAPI and JWT tokens.

## 🚀 Quick Start

### 1. Set up a virtual environment (recommended)
```bash
cd auth-service/auth-service
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the service
```bash
uvicorn main:app --reload --port 8001
```

The service will be available at:
- **API**: http://localhost:8001
- **Swagger Docs**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

---

## 📋 API Endpoints

### Authentication (Public)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Register new user (email, password, name) |
| POST | `/api/auth/login` | Login and get JWT token |
| GET | `/api/auth/verify` | Verify token (for other services) |

### Profile (Protected - requires JWT)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/auth/me` | Get current user data |
| PUT | `/api/auth/profile` | Update profile fields |
| POST | `/api/auth/profile/photo` | Upload profile photo |
| DELETE | `/api/auth/profile/photo` | Remove profile photo |
| POST | `/api/auth/profile/cv` | Upload CV file |
| DELETE | `/api/auth/profile/cv` | Remove CV file |

---

## 🔐 Using the API

### 1. Register a new user
```bash
curl -X POST http://localhost:8001/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepass123",
    "name": "John Doe"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "john@example.com",
    "name": "John Doe",
    ...
  }
}
```

### 2. Login
```bash
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepass123"
  }'
```

### 3. Access protected routes
Use the token from login/signup in the Authorization header:

```bash
curl http://localhost:8001/api/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

### 4. Update profile
```bash
curl -X PUT http://localhost:8001/api/auth/profile \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Senior Developer",
    "skills": ["Python", "FastAPI", "React"],
    "location": "New York, USA"
  }'
```

### 5. Upload profile photo
```bash
curl -X POST http://localhost:8001/api/auth/profile/photo \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/photo.jpg"
```

---

## 🔗 Frontend Integration

### JavaScript Example

```javascript
// API base URL
const AUTH_API = 'http://localhost:8001';

// Signup
async function signup(email, password, name) {
    const response = await fetch(`${AUTH_API}/api/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, name })
    });
    const data = await response.json();
    
    // Store token in localStorage
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    
    return data;
}

// Login
async function login(email, password) {
    const response = await fetch(`${AUTH_API}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });
    const data = await response.json();
    
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    
    return data;
}

// Make authenticated requests
async function fetchProtected(endpoint) {
    const token = localStorage.getItem('token');
    
    const response = await fetch(`${AUTH_API}${endpoint}`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    
    return response.json();
}

// Logout
function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = 'login.html';
}

// Check if logged in
function isLoggedIn() {
    return localStorage.getItem('token') !== null;
}
```

### Update the Frontend Login.js

Replace the simulated login with a real API call:

```javascript
async handleLogin() {
    this.isLoading = true;
    this.errorMessage = null;

    try {
        const response = await fetch('http://localhost:8001/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: this.email,
                password: this.password
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Login failed');
        }

        const data = await response.json();
        
        // Save token and user to localStorage
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        // Redirect to home
        window.location.href = 'index.html';

    } catch (error) {
        this.errorMessage = error.message;
        this.isLoading = false;
    }
}
```

---

## 🔄 Cross-Service Authentication

When _other services_ (like Job Service) need to verify a user's token:

```python
# In Job Service
import requests

def verify_user_token(token: str):
    """Call Auth Service to verify a token."""
    response = requests.get(
        'http://localhost:8001/api/auth/verify',
        headers={'Authorization': f'Bearer {token}'}
    )
    
    if response.status_code == 200:
        data = response.json()
        return data.get('user_id')  # Returns user ID if valid
    
    return None  # Token invalid
```

---

## 📁 Project Structure

```
auth-service/
└── auth-service/
    ├── main.py          # FastAPI app entry point
    ├── database.py      # SQLite database configuration
    ├── models.py        # SQLAlchemy User model
    ├── schemas.py       # Pydantic validation schemas
    ├── routes.py        # API endpoint handlers
    ├── auth_utils.py    # JWT & password utilities
    ├── file_utils.py    # File upload helpers
    ├── requirements.txt # Python dependencies
    ├── auth.db          # SQLite database (auto-created)
    └── uploads/         # Uploaded files
        ├── photos/      # Profile photos
        └── cvs/         # CV/resume files
```

---

## 🔒 Security Notes

1. **Secret Key**: Change `SECRET_KEY` in `auth_utils.py` for production
2. **CORS**: Restrict `allow_origins` to your actual frontend domain
3. **HTTPS**: Always use HTTPS in production
4. **Token Expiry**: Tokens expire after 7 days by default

---

## 🧪 Testing with Swagger

1. Go to http://localhost:8001/docs
2. Use the "Authorize" button at the top
3. Paste your JWT token (without "Bearer " prefix)
4. Test any protected endpoint
