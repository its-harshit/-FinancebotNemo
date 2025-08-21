# FinanceBot - NeMoGuardrails Custom Capabilities Demo

A comprehensive demonstration of NeMoGuardrails' custom capabilities for a finance company bot that handles user grievances, compliance checking, security features, and customer support.

## 🚀 Features

### Core Capabilities
- **🎫 Grievance Management**: Create, track, and escalate customer grievances
- **🔒 Compliance Checking**: Automatic detection of sensitive information and regulatory compliance
- **🛡️ Security Features**: Pattern-based detection of SSNs, credit cards, passwords, and PINs
- **💬 Message Processing**: Intent classification and response generation with guardrails
- **💳 Account Operations**: Secure account information retrieval with data masking
- **⏱️ SLA Tracking**: Response time calculation and SLA compliance monitoring

### NeMoGuardrails Integration
- **Custom Actions**: Business logic for grievance management and compliance
- **Input Flows**: User intent classification, input validation, and sensitive data detection
- **Output Flows**: Response quality checking, compliance enforcement, and formatting
- **Security Patterns**: Regex-based detection of sensitive financial information
- **Compliance Rules**: Automatic disclaimer injection for investment advice

## 📁 Project Structure

```
nemo/
├── config/
│   ├── config.yml                 # Main NeMoGuardrails configuration (enhanced)
│   ├── rails.yaml                 # Legacy configuration (still supported)
│   ├── actions.py                 # Custom business logic actions (enhanced)
│   ├── rails/                     # Colang flow definitions
│   │   ├── input_flows.co         # User intent classification and input validation
│   │   ├── output_flows.co        # Response quality and compliance checking
│   │   └── dialog_flows.co        # Conversation management flows
│   └── prompts/                   # Context and response templates
│       ├── context.md
│       └── general.md
├── finance_bot.py                 # Main bot application
├── demo.py                        # Interactive terminal demo
├── test_finance_bot.py            # Comprehensive test suite
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.8 or higher
- OpenAI API key (for GPT-4 integration)

### Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your OpenAI API key**:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```
   
   Or create a `.env` file:
   ```
   OPENAI_API_KEY=your-openai-api-key-here
   ```

4. **Verify installation**:
   ```bash
   python -c "import nemoguardrails; print('NeMoGuardrails installed successfully!')"
   ```

## 🎮 How to Use

### Quick Start Demo
Run the interactive demo application:
```bash
python demo.py
```

This will present you with a menu-driven interface to explore all features:

1. **🎫 Grievance Management Demo** - Create and manage customer grievances
2. **🔒 Compliance Checking Demo** - Test compliance and security features
3. **💬 Message Processing Demo** - See how different message types are handled
4. **🛡️ Security Features Demo** - Test sensitive information detection
5. **💳 Account Operations Demo** - Explore account-related functionality
6. **🔄 Comprehensive Workflow Demo** - End-to-end customer interaction
7. **🧪 Run Automated Tests** - Execute the test suite
8. **🚪 Exit** - Close the application

### Basic Usage
```python
from finance_bot import FinanceBot

# Initialize the bot
bot = FinanceBot()

# Process a customer message
response = await bot.process_message(
    "I have a complaint about my account being frozen",
    user_id="customer123"
)

# Create a grievance
grievance = await bot.create_grievance(
    user_id="customer123",
    category="account_issue",
    description="Account frozen without notice",
    priority="high"
)

# Check compliance
compliance = await bot.check_compliance(
    "Should I invest in stocks for retirement?"
)
```

### Running Tests
```bash
# Run the comprehensive test suite
pytest test_finance_bot.py -v

# Run specific test
pytest test_finance_bot.py::TestFinanceBot::test_grievance_creation -v
```

## 🔧 Customization

### Adding New Actions
Edit `config/actions.py` to add new business logic:

```python
@action()
async def your_custom_action(param1: str, param2: int) -> Dict:
    """Your custom action description."""
    # Your business logic here
    return {"success": True, "result": "your_result"}
```

### Modifying Flows
Edit the `.co` files in `config/flows/` to customize:
- Input validation rules
- Response formatting
- Compliance checks
- Security patterns

### Updating Compliance Rules
Modify the `check_compliance` function in `config/actions.py` to:
- Add new sensitive terms
- Update investment advice detection
- Modify compliance logic

## 🧪 Testing

The project includes comprehensive tests covering:

- ✅ Grievance creation and management
- ✅ Compliance checking with various message types
- ✅ Security feature detection
- ✅ Message processing with different intents
- ✅ Account operations and data masking
- ✅ Response time calculations
- ✅ Error handling and edge cases

Run tests with:
```bash
pytest test_finance_bot.py -v --tb=short
```

## 🔒 Security Features

### Sensitive Information Detection
- **SSN Detection**: `\b\d{3}-\d{2}-\d{4}\b`
- **Credit Card Detection**: `\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b`
- **Password/PIN Detection**: Keywords and patterns
- **Automatic Masking**: Account balances and sensitive data

### Compliance Enforcement
- **Investment Advice**: Automatic disclaimer injection
- **Guarantees**: Prevention of financial guarantees
- **Professional Tone**: Input validation for appropriate language
- **Data Protection**: Secure handling of customer information

## 📊 Key Capabilities Demonstrated

### 1. Grievance Management
- Create grievance tickets with categories and priorities
- Track grievance status and escalation
- Calculate response times and SLA compliance
- Escalate urgent issues automatically

### 2. Compliance & Security
- Real-time compliance checking
- Sensitive information detection and handling
- Automatic disclaimer injection for investment advice
- Professional tone enforcement

### 3. Message Processing
- Intent classification (grievance, account inquiry, general support)
- Context-aware response generation
- Input validation and sanitization
- Response quality assurance

### 4. Account Operations
- Secure account information retrieval
- Data masking for sensitive information
- Error handling for invalid requests
- Audit trail for all operations

## 🤝 Contributing

To extend this demo:

1. **Add new actions** in `config/actions.py`
2. **Create new flows** in `config/flows/`
3. **Update prompts** in `config/prompts/`
4. **Add tests** in `test_finance_bot.py`
5. **Update documentation** in this README

## 📝 License

This is a demonstration project for educational purposes. Feel free to use and modify as needed.

## 🆘 Troubleshooting

### Common Issues

1. **OpenAI API Key Not Set**
   ```
   Error: OPENAI_API_KEY environment variable not set
   ```
   Solution: Set your OpenAI API key as described in setup instructions.

2. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'nemoguardrails'
   ```
   Solution: Install dependencies with `pip install -r requirements.txt`

3. **Flow Parsing Errors**
   ```
   Error parsing flow file
   ```
   Solution: Check flow file syntax and ensure proper indentation.

### Getting Help

If you encounter issues:
1. Check the error messages for specific details
2. Verify your OpenAI API key is valid and has sufficient credits
3. Ensure all dependencies are installed correctly
4. Review the test suite for working examples

## 🎯 Next Steps

This demo showcases the foundation. Consider extending it with:

- **Database Integration**: Replace mock data with real database
- **Authentication**: Add user authentication and authorization
- **API Endpoints**: Create REST API for external integration
- **Monitoring**: Add logging and performance monitoring
- **Advanced Flows**: Implement more complex business logic flows
- **Multi-language Support**: Add internationalization capabilities

---

**Happy coding! 🚀**
