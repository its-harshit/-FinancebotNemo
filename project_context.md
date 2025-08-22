# PROJECT_CONTEXT.md

# 🏢 Enterprise NeMo Guardrails FinanceBot - Development Context

## 📖 **Project Overview**

This is an **enterprise-grade guardrails system** for your company's hosted LLM that will cater to finance grievances and needs. Currently in development phase, preparing for production deployment.

### **Key Project Goals:**
- 🏢 **Enterprise Production Use**: This will protect your company's LLM in production
- 🔒 **100% Self-Hosted**: No external API dependencies for data privacy
- 💰 **Financial Services Focus**: Specialized for banking/finance domain
- 🛡️ **Multi-Layer Security**: Comprehensive defense against various threats

## 🏗️ **Current Architecture Status**

### **✅ Implemented Components:**

#### **1. Core NeMo Guardrails Setup**
- **Main Config**: `config/config.yml` - Enhanced configuration following official guide
- **Dual Model Setup**: 
  - GPT-4 Turbo (main conversations)
  - GPT-3.5 Turbo (validation tasks) - Cost optimized
- **Custom Prompts**: Financial-specific self-check prompts override NeMo defaults

#### **2. Three-Layer Rails Architecture**
- **Input Rails**: 6 security layers
  - Self-check input (LLM-based)
  - User intent classification 
  - Input validation (pattern-based)
  - Sensitive information detection
  - Simple jailbreak check
  - (Planned: Llama Guard integration)
- **Output Rails**: 4 quality layers
  - Self-check output (LLM-based)  
  - Response quality checking
  - Compliance enforcement
  - Response formatting
- **Dialog Rails**: 3 conversation flows
  - Grievance management
  - Account inquiry handling
  - General support

#### **3. Custom Actions Ecosystem (13+ Actions)**
- **Business Logic**: grievance creation, account operations
- **Security**: PII detection, input validation, compliance checking
- **Quality Assurance**: response improvement, formatting
- **AI-Powered**: intent classification using keyword matching

#### **4. Financial Domain Specialization**
- **Compliance Rules**: Investment advice disclaimers, regulatory checking
- **Security Patterns**: SSN, credit card, phone number detection
- **Business Processes**: Grievance ticketing, SLA tracking
- **Data Masking**: Automatic sensitive information protection

### **🔄 Current Development Phase: Llama Guard Integration**

**Status**: Planning API-first approach, then migrate to self-hosted
- **Immediate**: Hugging Face Inference API for Llama Guard
- **Future**: Self-hosted vLLM cluster for complete data sovereignty
- **Benefit**: Specialized safety model trained for content safety

### **📊 Performance Characteristics**
- **LLM Calls per Message**: 3 calls total
  1. Input validation (GPT-3.5, ~200ms)
  2. Main conversation (GPT-4, ~1-2s)  
  3. Output validation (GPT-3.5, ~200ms)
- **Total Response Time**: ~2-3 seconds
- **Cost per Message**: ~$0.01

## 🛠️ **Technical Implementation Details**

### **Configuration Architecture**
```yaml
# Key insight: NeMo uses prompt override system
prompts:
  - task: self_check_input    # Overrides NeMo's default
    models: [validator]       # Uses cheaper GPT-3.5
    content: |
      # Your custom financial-specific validation rules
```

### **Flow Execution Order**
User Input → Input Rails → Dialog Rails → LLM → Output Rails → Response

### **Model Usage Strategy**
- **GPT-4**: Complex reasoning, main conversations
- **GPT-3.5**: Binary decisions, validation tasks  
- **Future Llama Guard**: Specialized safety screening
- **Pattern Matching**: Fast local validation

## 🎯 **Planned Enhancements**

### **Phase 1: Llama Guard Integration (Current)**
- ✅ API approach for quick validation
- 🔄 Enhanced guardrail reporting system
- 🔄 Detailed blocking explanations for users
- 📋 Debug mode for development

### **Phase 2: Self-Hosted Migration**
- 🔄 vLLM deployment for Llama Guard
- 🔄 Complete API independence
- 🔄 Performance optimization

### **Phase 3: Enterprise Production**
- 🔄 Kubernetes deployment
- 🔄 Load balancing and scaling
- 🔄 Full observability stack (Prometheus, Grafana, Jaeger)
- 🔄 Audit logging and compliance reporting

### **Phase 4: Advanced Features**
- 🔄 Presidio PII detection integration
- 🔄 Custom financial threat models
- 🔄 Real-time monitoring and alerting
- 🔄 Integration with company's LLM

## 🔍 **Key Learnings & Insights**

### **NeMo Guardrails Architecture Understanding**
1. **Prompt Override System**: Custom prompts replace NeMo defaults
2. **Flow Execution**: Input → Dialog → Output rails sequence
3. **Model Assignment**: Can use different models for different tasks
4. **Action Integration**: Python functions seamlessly integrated
5. **Configuration Flexibility**: YAML-based, highly customizable

### **Performance Optimization Strategies**
1. **Dual Model Approach**: Expensive model only for complex tasks
2. **Early Termination**: Stop processing on first security violation
3. **Pattern Matching**: Fast local checks before LLM calls
4. **Caching Strategy**: Planned for repeated safety checks

### **Security Layer Philosophy**
1. **Defense in Depth**: Multiple independent validation layers
2. **Fail Open Strategy**: Maintain availability when components fail
3. **Transparency**: Detailed reporting of blocking decisions
4. **Domain Specialization**: Financial-specific threat models

## 📁 **File Structure Context**

### **Core Files**
- `config/config.yml`: Main configuration (enhanced from basic rails.yaml)
- `config/actions.py`: 13+ custom actions (354 lines of business logic)
- `config/rails/*.co`: Colang flow definitions
- `finance_bot.py`: Main application class
- `chat.py`: Interactive testing interface

### **Configuration Files**
- `config/prompts/`: Reference templates (not auto-loaded)
- `CONFIGURATION_GUIDE.md`: Migration and usage documentation
- `PROJECT_CONTEXT.md`: This file

## 🚨 **Important Notes for Future Sessions**

### **Environment Setup**
```bash
# Required environment variables
export OPENAI_API_KEY="your-key"
export HUGGINGFACE_API_KEY="hf_your-token"  # For Llama Guard API

# Key dependencies
pip install nemoguardrails>=0.9.0 openai>=1.3.0
```

### **Common Commands**
```bash
# Test the bot
python chat.py

# Run comprehensive tests  
python demo.py

# Debug guardrails (when implemented)
python -c "from config.actions import debug_all_guardrails; import asyncio; print(asyncio.run(debug_all_guardrails('test message')))"
```

### **Current Issues/Limitations**
1. **External Dependencies**: Still using OpenAI APIs (temporary)
2. **Llama Guard**: Not yet integrated (next priority)
3. **Monitoring**: Basic logging only (needs enterprise observability)
4. **Scaling**: Single instance (needs clustering for production)

### **Architecture Decisions Made**
1. **Config over Rails.yaml**: Following official NeMo guidelines
2. **Dual Model Strategy**: Cost optimization while maintaining quality
3. **API-First Llama Guard**: Faster development, migrate later
4. **Enhanced Reporting**: Transparency for debugging and compliance

## 🎯 **Next Immediate Steps**

1. **Complete Llama Guard Integration**
   - Implement API version
   - Add enhanced reporting system
   - Test with various attack vectors

2. **Prepare for Self-Hosting**
   - Document hardware requirements
   - Plan vLLM deployment strategy
   - Design migration path

3. **Enterprise Hardening**
   - Add comprehensive monitoring
   - Implement audit logging
   - Design production deployment

---

**This project represents a production-ready foundation for enterprise AI safety in financial services.** 🏆