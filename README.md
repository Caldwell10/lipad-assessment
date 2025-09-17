# Mini Loan Request Platform
A backend system that allows users to register and apply for small loans with integrated credit scoring and asynchronous callback handling.


### Installation & Setup

1. **Clone or download the project**
   ```bash
   cd lipad-assessment
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv lipad-env
   source lipad-env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Access the API**
   - Server: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs

## 📊 Database Schema

The application uses SQLite with the following tables:

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    phone_number VARCHAR NOT NULL
);
```

### Loan Requests Table
```sql
CREATE TABLE loan_requests (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    amount FLOAT NOT NULL,
    status VARCHAR DEFAULT 'PENDING',
    reason VARCHAR,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### API Logs Table
```sql
CREATE TABLE api_logs (
    id INTEGER PRIMARY KEY,
    direction VARCHAR NOT NULL,
    url VARCHAR NOT NULL,
    payload TEXT,
    status_code INTEGER NOT NULL,
    created_at DATETIME NOT NULL
);
```

## 🔗 API Endpoints

### 1. Create User
**POST** `/users`

Create a new user in the system.

**Request Body:**
```json
{
    "name": "John Doe",
    "email": "john@example.com",
    "phone_number": "1234567890"
}
```

**Response:**
```json
{
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "phone_number": "1234567890"
}
```

### 2. Create Loan Request
**POST** `/loan-requests`

Submit a new loan application.

**Request Body:**
```json
{
    "user_id": 1,
    "amount": 5000.00
}
```

**Response:**
```json
{
    "id": 1,
    "user_id": 1,
    "amount": 5000.0,
    "status": "PENDING",
    "created_at": "2025-01-17T10:30:00",
    "updated_at": "2025-01-17T10:30:00"
}
```

### 3. Get Loan Request Status
**GET** `/loan-requests/{loan_id}`

Retrieve the status and details of a specific loan request.

**Response:**
```json
{
    "id": 1,
    "user_id": 1,
    "amount": 5000.0,
    "status": "APPROVED",
    "created_at": "2025-01-17T10:30:00",
    "updated_at": "2025-01-17T10:35:00"
}
```

### 4. Credit Score Webhook
**POST** `/webhook/credit-score`

Receives asynchronous callbacks from the credit scoring API.

**Request Body:**
```json
{
    "loan_id": 1,
    "score": 720,
    "status": "APPROVED",
    "reason": "Good credit history"
}
```

**Response:**
```json
{
    "message": "Loan updated",
    "loan_id": 1,
    "status": "APPROVED"
}
```

## Testing with curl

### 1. Create a User
```bash
curl -X POST "http://localhost:8000/users" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Kibe",
       "email": "kibe@example.com",
       "phone_number": "0742453295"
     }'
```

### 2. Submit Loan Request
```bash
curl -X POST "http://localhost:8000/loan-requests" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": 1,
       "amount": 5000
     }'
```

### 3. Check Loan Status
```bash
curl -X GET "http://localhost:8000/loan-requests/1"
```

### 4. Simulate Credit Score Callback
```bash
curl -X POST "http://localhost:8000/webhook/credit-score" \
     -H "Content-Type: application/json" \
     -d '{
       "loan_id": 1,
       "score": 720,
       "status": "APPROVED",
       "reason": "Good credit history"
     }'
```

## Business Logic & Validations

### User Registration
- Email must be unique
- Email format validation
- Phone number length validation (7-15 characters)
- All fields are required

### Loan Applications
- User must exist in the system
- Amount must be greater than 0 and less than 1,000,000
- Only one pending loan request per user allowed
- Status tracking (PENDING → APPROVED/REJECTED)

### External API Integration
- Sends loan data to mock credit scoring API
- Includes callback URL for asynchronous responses

## Loan Request Flow

1. **Submission**: User submits loan request
2. **Validation**: System validates user existence, amount constraints, and duplicate requests
3. **External API**: Request sent to credit scoring API with callback URL
4. **Logging**: All outgoing requests logged in database
5. **Webhook**: External API calls back with scoring result
6. **Update**: Loan status updated based on callback data
7. **Timestamp**: Updated timestamp reflects last modification

## Database Inspection

To inspect the database directly:
```bash
sqlite3 loans.db

# View tables
.tables

# View users
SELECT * FROM users;

# View loan requests
SELECT * FROM loan_requests;

# View API logs
SELECT * FROM api_logs;
```

## Error Handling

API returns HTTP status codes:
- **200**: Success
- **400**: Bad Request 
- **404**: Resource Not Found
- **422**: Unprocessable Entity 

**Tech Stack**: Python, FastAPI, SQLAlchemy, SQLite, Pydantic