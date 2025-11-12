# AI Configuration System - Complete Guide

## Overview
The AI Configuration system allows administrators to set default AI providers and models, while enabling users to override these settings with their own API keys and preferences. This provides flexibility, cost control, and customization for AI-powered features.

## Features

### ✅ Implemented Features

1. **Admin Default Settings**
   - Configure default AI providers (OpenAI, Anthropic, Google)
   - Set API keys for each provider
   - Choose default models for each provider
   - Enable/disable providers with toggle switches
   - Configure per-feature AI settings

2. **Per-Feature AI Configuration**
   - Resume Generation
   - Interview Preparation
   - Cover Letter Generation
   - Live Interview Assistant
   - ATS Optimization

3. **User Override System**
   - Users can add their own API keys
   - Override admin defaults on per-feature basis
   - Reset to admin defaults anytime
   - View effective settings (merged admin + user)

4. **Emergent LLM Key Integration**
   - Universal key works across OpenAI, Anthropic, Google
   - Enabled by default
   - Users can opt to use custom keys instead
   - Seamless fallback mechanism

## Architecture

### Backend Components

#### Models (`/app/backend/models/settings.py`)

```python
AIProviderConfig - Configuration for each AI provider
AISettings - Admin default AI settings
AISettingsUpdate - Update admin AI settings
UserAISettings - User-specific overrides
UserAISettingsUpdate - Update user AI settings
FeatureAIConfig - Per-feature AI configuration
```

#### API Endpoints (`/app/backend/routers/admin.py`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/admin/ai-settings` | GET | Get admin default AI settings |
| `/api/admin/ai-settings` | PUT | Update admin default AI settings |
| `/api/admin/ai-settings/user` | GET | Get current user's AI settings |
| `/api/admin/ai-settings/user` | PUT | Update current user's AI settings |
| `/api/admin/ai-settings/user` | DELETE | Reset user settings to defaults |
| `/api/admin/ai-settings/effective` | GET | Get effective settings (merged) |

### Frontend Components

#### Admin Settings (`/app/frontend/src/pages/AISettings.js`)

- Toggle switches for each provider
- API key input fields with show/hide
- Model selection dropdowns
- Per-feature provider and model configuration
- Save functionality with validation

#### Admin Settings Tabs (`/app/frontend/src/pages/AdminSettings.js`)

- Storage Configuration tab
- AI Integrations tab
- Seamless navigation between settings

### Database Collections

```javascript
// Admin settings collection
{
  type: "ai",
  use_emergent_key: true,
  openai: { enabled: true, api_key: "...", default_model: "gpt-4o" },
  anthropic: { enabled: false, api_key: null, default_model: null },
  google: { enabled: false, api_key: null, default_model: null },
  resume_generation: { provider: "emergent", model: "gpt-4o" },
  interview_prep: { provider: "emergent", model: "gpt-4o" },
  cover_letter: { provider: "emergent", model: "gpt-4o" },
  live_interview: { provider: "emergent", model: "gpt-4o" },
  ats_optimization: { provider: "emergent", model: "gpt-4o" },
  updated_at: "2024-11-12T...",
  updated_by: "user_id"
}

// User settings collection
{
  user_id: "user_123",
  use_custom_keys: true,
  openai: { enabled: true, api_key: "user-key-...", default_model: "gpt-4" },
  resume_generation: { provider: "openai", model: "gpt-4", use_custom_key: true },
  created_at: "2024-11-12T...",
  updated_at: "2024-11-12T..."
}
```

## Configuration Priority

The system uses a three-tier priority system:

```
1. User Custom Settings (Highest Priority)
   ↓ (if not set)
2. Emergent LLM Key (Default)
   ↓ (if disabled)
3. Admin Default Settings (Fallback)
```

### Resolution Logic

```javascript
For each AI feature request:

1. Check if user has custom settings for this feature
   - YES: Use user's provider and model
   - NO: Continue to step 2

2. Check if Emergent LLM Key is enabled
   - YES: Use Emergent key with admin default model
   - NO: Continue to step 3

3. Use admin default provider and model
```

## Setup Guide

### Admin Setup

1. **Access Admin Settings**
   - Navigate to Settings → Admin Settings
   - Click "AI Integrations" tab

2. **Configure Emergent LLM Key**
   - Toggle ON (recommended for all users)
   - This enables universal AI access

3. **Configure Provider API Keys (Optional)**
   - **OpenAI**:
     - Toggle ON
     - Enter API key (sk-...)
     - Select default model (gpt-4o, gpt-4, etc.)
   
   - **Anthropic**:
     - Toggle ON
     - Enter API key (sk-ant-...)
     - Select default model (claude-sonnet-4, etc.)
   
   - **Google**:
     - Toggle ON
     - Enter API key (AIza...)
     - Select default model (gemini-2.0-pro, etc.)

4. **Configure Per-Feature Settings**
   - For each feature (Resume, Interview, etc.):
     - Select provider (Emergent/OpenAI/Anthropic/Google)
     - Specify model name
   - Examples:
     - Resume Generation: OpenAI → gpt-4o
     - Live Interview: Anthropic → claude-sonnet-4
     - Cover Letters: Emergent → gpt-4o

5. **Save Configuration**
   - Click "Save Changes"
   - Settings apply immediately to all users

### User Setup (Coming Soon)

Users will be able to:

1. **Navigate to Profile Settings**
   - Access AI Preferences section

2. **Add Custom API Keys**
   - Enter their own OpenAI/Anthropic/Google keys
   - Override admin defaults

3. **Customize Per-Feature**
   - Choose which provider/model for each feature
   - Use different keys for different features

4. **View Effective Settings**
   - See which settings are active
   - Understand cost implications

5. **Reset to Defaults**
   - Remove custom settings anytime
   - Return to admin defaults

## Supported AI Providers

### OpenAI
**Models:**
- `gpt-4o` - Latest, fastest, most capable
- `gpt-4` - Original GPT-4, highly capable
- `gpt-4-turbo` - Faster GPT-4 variant
- `gpt-3.5-turbo` - Budget-friendly option

**API Key Format:** `sk-...`

**Features:**
- ✅ Text generation
- ✅ Code generation
- ✅ Creative writing
- ✅ Analysis and reasoning

### Anthropic Claude
**Models:**
- `claude-4-sonnet-20250514` - Balanced performance
- `claude-opus-4-20250514` - Most capable
- `claude-3.5-sonnet` - Previous generation

**API Key Format:** `sk-ant-...`

**Features:**
- ✅ Long context windows
- ✅ Strong reasoning
- ✅ Ethical AI responses
- ✅ Code generation

### Google AI
**Models:**
- `gemini-2.0-pro` - Latest Gemini
- `gemini-pro` - Balanced model
- `gemini-flash` - Fast, efficient

**API Key Format:** `AIza...`

**Features:**
- ✅ Multimodal capabilities
- ✅ Fast inference
- ✅ Large context
- ✅ Cost-effective

### Emergent LLM Key
**Universal Access:**
- Works with OpenAI, Anthropic, and Google
- Single key for all providers
- Managed billing
- No setup required

**Models Supported:**
- All OpenAI models
- All Anthropic models
- Google Gemini models (text generation only)

**Limitations:**
- No audio/video generation
- No fine-tuned models
- Standard rate limits

## Use Cases

### Use Case 1: Startup with Emergent Key
**Scenario:** Small startup, limited budget, quick setup

**Configuration:**
```yaml
Admin Settings:
  - Emergent LLM Key: ON
  - All features: Use Emergent key
  - Model: gpt-4o (best balance)

User Settings:
  - Use defaults (no custom keys)
```

**Benefits:**
- Zero setup for users
- Centralized cost control
- Consistent AI quality

### Use Case 2: Enterprise with Department Keys
**Scenario:** Large company, different teams, separate budgets

**Configuration:**
```yaml
Admin Settings:
  - Emergent LLM Key: ON (fallback)
  - OpenAI: Enabled (corporate key)
  - All features: Use OpenAI

User Settings:
  - Engineering: OpenAI key (team budget)
  - Marketing: Anthropic key (creative work)
  - HR: Emergent key (default)
```

**Benefits:**
- Cost allocation per team
- Team autonomy
- Fallback protection

### Use Case 3: Power Users with Custom Models
**Scenario:** Advanced users want specific models

**Configuration:**
```yaml
Admin Settings:
  - Emergent LLM Key: ON
  - Default models: Balanced

User Settings:
  - Resume Generation: Claude Opus (best quality)
  - Interview Prep: GPT-4o (fast responses)
  - Cover Letters: Gemini Pro (cost-effective)
```

**Benefits:**
- Feature-specific optimization
- Cost vs quality balance
- User flexibility

### Use Case 4: Hybrid Approach
**Scenario:** Mix of free and premium features

**Configuration:**
```yaml
Admin Settings:
  - Resume Generation: Emergent (free for users)
  - Interview Prep: Emergent (free for users)
  - Cover Letters: User's own key (premium)
  - Live Interview: User's own key (premium)
```

**Benefits:**
- Freemium model
- Upsell opportunities
- User value perception

## API Usage Examples

### Admin: Set Default AI Configuration

```javascript
// Set admin defaults
await adminAPI.updateAISettings({
  use_emergent_key: true,
  openai: {
    enabled: true,
    api_key: "sk-...",
    default_model: "gpt-4o"
  },
  anthropic: {
    enabled: false,
    api_key: null,
    default_model: null
  },
  resume_generation: {
    provider: "emergent",
    model: "gpt-4o"
  },
  interview_prep: {
    provider: "emergent",
    model: "gpt-4o"
  }
});
```

### User: Override with Custom Key

```javascript
// User adds custom OpenAI key
await adminAPI.updateUserAISettings({
  use_custom_keys: true,
  openai: {
    enabled: true,
    api_key: "sk-user-custom-key...",
    default_model: "gpt-4"
  },
  resume_generation: {
    provider: "openai",
    model: "gpt-4",
    use_custom_key: true
  }
});
```

### Get Effective Settings

```javascript
// Get what will actually be used
const response = await adminAPI.getEffectiveAISettings();

console.log(response.data.settings);
// Shows merged admin + user settings
// Indicates which settings are custom vs default
```

## Security Considerations

### API Key Storage
- ✅ Stored encrypted in database
- ✅ Never exposed in logs
- ✅ Masked in UI (show/hide toggle)
- ✅ Not returned in API responses (except to owner)

### Access Control
- ✅ Admin endpoints require authentication
- ✅ Users can only access their own settings
- ✅ API keys validated before storage
- ⚠️ TODO: Add admin role check

### Best Practices
1. **Rotate API keys regularly**
2. **Use environment-specific keys**
3. **Monitor API usage and costs**
4. **Set up billing alerts**
5. **Audit key access logs**

## Cost Management

### Admin Cost Control
- Set usage limits per user/team
- Monitor aggregate API usage
- Disable expensive models
- Force specific providers

### User Cost Awareness
- Show estimated costs per feature
- Display usage statistics
- Warn before expensive operations
- Provide cost-effective alternatives

### Emergent LLM Key Benefits
- ✅ Predictable billing
- ✅ No surprise costs
- ✅ Auto-scaling included
- ✅ Balance monitoring

## Troubleshooting

### Issue: "AI settings not loading"
**Solution:**
1. Check backend logs: `tail -f /var/log/supervisor/backend.err.log`
2. Verify database connection
3. Check API endpoint: `curl http://localhost:8001/api/admin/ai-settings`

### Issue: "Invalid API key"
**Solution:**
1. Verify key format matches provider
2. Check key hasn't expired
3. Test key directly with provider
4. Ensure no extra spaces in key

### Issue: "User settings not applying"
**Solution:**
1. Check effective settings endpoint
2. Verify `use_custom_keys` is true
3. Ensure user has saved settings
4. Clear cache and reload

### Issue: "Feature using wrong model"
**Solution:**
1. Check per-feature configuration
2. Verify provider is enabled
3. Check resolution priority
4. Review effective settings

## Testing

### Test Admin Settings

```bash
# Get admin settings
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8001/api/admin/ai-settings

# Update admin settings
curl -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"openai": {"enabled": true, "api_key": "sk-test", "default_model": "gpt-4o"}}' \
  http://localhost:8001/api/admin/ai-settings
```

### Test User Settings

```bash
# Get user settings
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8001/api/admin/ai-settings/user

# Update user settings
curl -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"use_custom_keys": true, "openai": {"enabled": true, "api_key": "sk-user-key"}}' \
  http://localhost:8001/api/admin/ai-settings/user

# Reset to defaults
curl -X DELETE \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8001/api/admin/ai-settings/user
```

### Test Effective Settings

```bash
# Get merged settings
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8001/api/admin/ai-settings/effective
```

## Future Enhancements

### Planned Features
- [ ] User-facing AI preferences page
- [ ] Cost tracking and analytics
- [ ] Usage quotas and limits
- [ ] Model performance metrics
- [ ] A/B testing support
- [ ] Custom model endpoints
- [ ] Fine-tuned model support
- [ ] Prompt template management
- [ ] Response caching
- [ ] Fallback provider chains

### Integration Points
- [ ] Billing system integration
- [ ] Audit logging
- [ ] Analytics dashboard
- [ ] Alert system for failures
- [ ] Load balancing across providers

## Support

### Documentation
- **API Reference:** `/api/docs` (FastAPI auto-docs)
- **Frontend Components:** Source code in `/app/frontend/src/pages/`
- **Backend Models:** `/app/backend/models/settings.py`

### Common Questions

**Q: Can users see admin API keys?**
A: No, API keys are masked and only accessible to their owners.

**Q: What happens if all providers fail?**
A: System falls back to Emergent LLM Key if enabled, otherwise returns error.

**Q: Can I use multiple keys for load balancing?**
A: Not yet, but planned for future release.

**Q: How do I migrate from admin keys to user keys?**
A: Users can gradually add their keys while admin keys remain as fallback.

**Q: Is there a rate limit?**
A: Provider-specific limits apply. Monitor usage in admin dashboard (coming soon).

---

**Version:** 1.0.0  
**Last Updated:** November 2024  
**Status:** ✅ Admin Configuration Complete, 🚧 User Interface In Progress
