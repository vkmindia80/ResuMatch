# How to Test Live Interview Assistant

## Quick Test Guide

### 1. Access the Application
- Open your browser (Chrome or Edge recommended)
- Navigate to the frontend URL
- Log in to your account

### 2. Navigate to Live Interview
- Click "Live Assistant" in the navigation bar
- You should see the session setup page

### 3. Start a Session

#### Basic Setup:
1. **Session Title**: Enter a title (e.g., "Software Engineer Interview Test")
2. **Resume Source**: Choose "Use Profile Resume (Default)"
3. **Job Description**: Optional - select one if available
4. **Click "Start Live Session"**

#### What to Look For:
- ✅ Session should start immediately
- ✅ Timer should begin counting
- ✅ Green/red microphone button should appear

### 4. Test Speech Recognition

1. **Click the Microphone Button** (should turn green)
2. **Speak a question** clearly, for example:
   - "Tell me about your experience with Python"
   - "What are your greatest strengths?"
   - "Describe a challenging project you worked on"

#### Expected Behavior:
- ✅ Your speech appears as you talk (interim)
- ✅ Question is added to transcript when you pause
- ✅ "Generating AI answer..." indicator appears
- ✅ AI answer displays within 3-5 seconds

### 5. Verify AI Answer Display

The AI answer should show in a green card with:
- ✅ "AI Suggested Answer:" heading
- ✅ The generated answer text
- ✅ Model indicator (GPT-4 or Claude)
- ✅ "Based on:" context information

### 6. Test Multiple Questions

Continue speaking more questions to verify:
- ✅ Each question generates a new answer
- ✅ Previous questions appear in transcript
- ✅ Session time continues counting
- ✅ Question count updates

### 7. End Session

1. Click "End Session" button
2. Should navigate to analysis page
3. Review your session transcript

## Console Debugging

### Open Browser Console (F12)
Look for these log messages:

#### Session Start:
```
[LiveInterview] Starting session...
[LiveInterview] Session started: {...}
[LiveInterview] Session ID: abc123...
```

#### Question Detection:
```
[LiveInterview] Final transcript received: Tell me about...
[LiveInterview] Using sessionId: abc123...
[LiveInterview] Saving transcript to backend...
[LiveInterview] Transcript saved successfully
```

#### AI Answer Generation:
```
[LiveInterview] Generating AI answer...
[LiveInterview] AI answer received: {...}
```

### If You See Errors:

#### "No sessionId - cannot generate answer"
- ❌ This should NOT happen anymore after the fix
- If it does, refresh and try again

#### "Failed to generate AI answer"
- Check backend logs: `tail -f /var/log/supervisor/backend.err.log`
- Verify Emergent LLM Key is set in backend .env
- Check internet connectivity

#### "Speech recognition error"
- Make sure you're using Chrome or Edge
- Allow microphone permissions
- Check microphone is working in other apps

## Advanced Testing

### Test Different Models
1. Before starting session, click "Advanced Settings"
2. Change AI Model to "Claude Sonnet"
3. Start session and verify Claude responses

### Test Different Languages
1. In Advanced Settings, change Language
2. Speak in that language
3. Verify recognition and answers work

### Test with Job Description
1. Create a job description first
2. Select it when starting live session
3. Verify answers are tailored to the role

### Test with Generated Resume
1. Generate an optimized resume first
2. Select "Use Generated Resume"
3. Choose a resume from dropdown
4. Verify answers use resume content

## Performance Expectations

| Metric | Expected Value |
|--------|---------------|
| Session start time | < 2 seconds |
| Speech to text delay | < 1 second |
| AI answer generation | 3-5 seconds |
| Total question → answer | 4-7 seconds |
| Microphone start delay | Instant |

## Common Issues & Solutions

### Issue: Microphone button stays red
**Solution**: 
- Click the button again
- Check browser microphone permissions
- Reload page and try again

### Issue: Speech not detected
**Solution**:
- Speak clearly and loudly
- Check microphone input level in system settings
- Try different browser (Chrome recommended)

### Issue: No AI answer appears
**Solution**:
- Check browser console for errors (F12)
- Verify backend is running: `sudo supervisorctl status backend`
- Check backend logs for errors
- Verify Emergent LLM Key in backend .env

### Issue: "Failed to generate AI answer" error
**Solution**:
- Check internet connection
- Verify Emergent LLM Key balance
- Try refreshing the page
- Check backend logs for API errors

### Issue: Answers are generic/not personalized
**Solution**:
- Complete your profile fully
- Add more experience, skills, education
- Use generated resume for more optimized content
- Add job description for role-specific answers

## Testing Checklist

Use this checklist to verify everything works:

- [ ] Session starts successfully
- [ ] Session ID is logged in console
- [ ] Microphone button works (green when active)
- [ ] Speech is transcribed correctly
- [ ] Questions appear in transcript
- [ ] Loading indicator shows "Generating AI answer..."
- [ ] AI answers appear within 5 seconds
- [ ] Answers are relevant to profile
- [ ] Multiple questions work in sequence
- [ ] Session timer counts correctly
- [ ] Question counter updates
- [ ] Context panel shows profile info
- [ ] End session works
- [ ] Navigate to analysis page works

## Browser Console Quick Check

Run this in console during active session:
```javascript
// Check if session is active
console.log('Session Active:', sessionActive);
console.log('Session ID:', sessionId);
console.log('Is Listening:', isListening);
console.log('Questions Count:', transcript.length);
```

## API Endpoint Testing

Test the backend directly with curl:

### Health Check:
```bash
curl http://localhost:8001/api/health
```

### Test Answer Generation (requires auth token):
```bash
curl -X POST http://localhost:8001/api/live-interview/sessions/YOUR_SESSION_ID/generate-answer \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "Tell me about yourself", "session_id": "YOUR_SESSION_ID"}'
```

## Success Indicators

✅ **Everything is working correctly if you see:**
1. Questions are transcribed
2. Loading indicator appears
3. AI answers display within 5 seconds
4. Answers are personalized to your profile
5. No errors in console
6. Session flows smoothly

❌ **Something is wrong if:**
1. Loading indicator never appears
2. No AI answers show up
3. Console shows errors
4. Session crashes or freezes

## Support

If issues persist:
1. Check `/app/LIVE_INTERVIEW_FIX_SUMMARY.md` for technical details
2. Review backend logs: `tail -f /var/log/supervisor/backend.err.log`
3. Review frontend logs: `tail -f /var/log/supervisor/frontend.err.log`
4. Verify all services running: `sudo supervisorctl status`

---

**Last Updated**: November 2024
**Version**: 1.0.1 (Bug Fix Applied)
