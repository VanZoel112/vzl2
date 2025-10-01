# Vzoel Fox's Lutpan - Development Roadmap

**Project:** Pure Userbot System Enhancement
**Brand:** Vzoel Fox's Lutpan
**Architecture:** Pure userbot (non-hybrid)
**Repository:** vzl2

---

## Phase 1: Voice Chat & Music System

**Objective:** Pure userbot VC integration with local playback

### Features

#### 1.1 Voice Chat Commands
- `.jlvc` - Join/Leave voice chat toggle
- `.startvc` - Create new voice chat in group
- **Implementation:** Pure userbot (bukan hybrid)
- **Tech:** PyTgCalls integration
- **Behavior:** Auto-join/create VC, manage connection state

#### 1.2 Music Playback
- `.play <query>` - Stream MP3 to OS audio (local playback)
- `.song <query>` - Download song to device
- **Source:** YouTube via yt-dlp
- **Format:** MP3 audio only
- **Quality:** High quality extraction
- **Cookies:** Implement from vzoelupgrade (YouTube auth bypass)

#### 1.3 Technical Requirements
- Port yt-dlp system from vzoelupgrade
- Port cookies handling from vzoelupgrade
- Adapt to vzl2 project structure
- Maintain existing emoji mapping
- Preserve animation system
- Keep database structure intact

---

## Phase 2: GitHub Direct Integration

**Objective:** Manage repository directly from Telegram

### Features

#### 2.1 Core Git Commands
- `.push` - Commit and push changes to GitHub
  - Auto-detect changes
  - Smart commit messages
  - Handle conflicts automatically

- `.pull` - Pull latest changes from GitHub
  - Auto-merge when possible
  - Detect rebase requirements
  - Handle merge conflicts

- `.settoken` - Configure GitHub classic token
  - Secure storage
  - Token validation
  - Expiry detection

#### 2.2 Auto-Resolution System
- **Commit Detection:** Auto-commit before push if needed
- **Rebase Handling:** Auto-rebase on pull conflicts
- **Conflict Resolution:** Notify user with clear options
- **Token Fallback:** Prompt .settoken if expired/missing

#### 2.3 User Experience
- No SSH/VPS access needed
- All operations via Telegram
- Clear status messages
- Error handling with suggestions

---

## Phase 3: Payment System Integration

**Objective:** Automated payment QR code management

### Features

#### 3.1 Payment Commands
- `.get` - Retrieve payment information
  - Show current payment setup
  - Display QR if available
  - Show transaction history

- `.setget` - Configure payment details
  - Payment gateway info
  - Account credentials
  - Merchant settings

#### 3.2 QR Code System
- `.getqr` - Display payment QR code
  - Fetch from configured payment
  - Send as image
  - Include payment details

- `.setgetqr` - Configure QR code source
  - **Prerequisite:** Runs `.getfileid` first
  - **Process:** Extract file_id from .getfileid
  - **Storage:** Save file_id to database
  - **Usage:** Quick QR retrieval

#### 3.3 File ID Helper
- `.getfileid` - Extract file_id from image
  - Reply to PNG/JPG image
  - Extract Telegram file_id
  - Display for user/system use
  - Used by .setgetqr automatically

---

## Phase 4: Utility Commands

**Objective:** Essential operational tools

### Features

#### 4.1 Logging System
- `.sendlog` - Send process logs to log group
  - Auto-detect log file
  - Format for readability
  - Include timestamp
  - Support log rotation

#### 4.2 Dependency Management
- `.install <package>` - Install dependencies from Telegram
  - **Example:** `.install pip py-tgcalls`
  - Direct package installation
  - No VPS SSH required
  - Progress feedback
  - Error reporting
  - Support: pip, npm, apt packages

#### 4.3 Configuration
- Create all necessary config files
- Secure credential storage
- Environment variable management
- Config validation

---

## Phase 5: Docker Automation

**Objective:** Containerization with auto-deployment

### Features

#### 5.1 Docker Command
- `.docker` - Auto-generate and deploy
  - Create Dockerfile automatically
  - Build container image
  - Deploy userbot in container
  - Handle dependencies

#### 5.2 GitHub Integration
- Auto-push Dockerfile with `.push`
  - Include in repository
  - Version control
  - Deployment history

#### 5.3 Fallback Mechanism
- Token validation before push
- Fallback to `.settoken` if:
  - GitHub token expired
  - Token not available
  - Token invalid
- Clear user prompts

---

## Phase 6: Sudo User System

**Objective:** Multi-user access with isolated environments

### Features

#### 6.1 Sudo Management
- `.gift <phone_number>` - Grant sudo access
  - **Process:**
    1. User provides phone number
    2. User provides login code
    3. Auto-generate session
    4. Auto-deploy to VPS
    5. Create isolated Docker container
    6. Setup separate database
    7. Notify both owner and sudo user

- `.cl` - Revoke sudo access
  - Stop sudo user session
  - Remove Docker container
  - Clean database entries
  - Notify affected users

#### 6.2 Sudo User Features (Limited Access)
Available commands for sudo users:
- `.id` - Show user/chat information
- `.help` - Available commands
- `.alive` - Bot status check
- `.ping/.pink/.ponk/.pong` - Latency check variants
- `.limit` - Usage limits/quotas
- `.gcast` - Global broadcast
- `.blacklistgcast` - Manage broadcast blacklist
- `.tagall` - Tag all members
- `.stoptagall` - Stop tagging
- `.jlvc` - Join/leave voice chat
- `.leavevc` - Leave voice chat

#### 6.3 Isolation Architecture
- **Database:** Separate database per sudo user
- **Docker:** Individual container per sudo
- **Resources:** Isolated resource allocation
- **Permissions:** Limited command set
- **Monitoring:** Owner can view sudo activity

---

## Phase 7: Premium Emoji & Animation System

**Objective:** Maintain and enhance existing features

### Requirements

#### 7.1 Emoji Mapping
- All premium emojis properly mapped
- Test each emoji functionality
- Ensure rendering works
- No broken emoji references

#### 7.2 Animation System
- All edit animations functioning
- Smooth transitions
- No animation lag
- Preserve timing/sequences
- Maintain current behavior

#### 7.3 Testing
- Comprehensive emoji test
- Animation flow verification
- Edge case handling
- Performance optimization

---

## Phase 8: Branding & Polish

**Objective:** Consistent Vzoel Fox's Lutpan identity

### Requirements

#### 8.1 Brand Identity
- **All messages:** "Vzoel Fox's Lutpan" branding
- **Contact:** @VZLfxs
- **Tone:** Professional, elegant
- **Style:** Minimal emoji, clean formatting

#### 8.2 Message Refinement
- Remove excessive emojis
- Professional language
- Clear status messages
- Helpful error messages
- Consistent formatting

#### 8.3 Code Quality
- Clean comments
- Proper documentation
- Type hints where applicable
- Error handling
- Logging standards

---

## Technical Specifications

### Project Structure
```
vzl2/
├── config.py           # Main configuration
├── main.py            # Entry point
├── core/              # Core systems
│   ├── voice_chat.py  # VC management
│   ├── music.py       # Music playback
│   ├── git_manager.py # GitHub integration
│   ├── payment.py     # Payment system
│   └── docker.py      # Docker automation
├── modules/           # Feature modules
│   ├── sudo.py        # Sudo user management
│   ├── utils.py       # Utility commands
│   └── emoji.py       # Emoji mapping
├── database/          # Database layer
│   ├── main_db.py     # Owner database
│   └── sudo_db.py     # Sudo databases
└── Dockerfile         # Auto-generated

```

### Dependencies to Port from vzoelupgrade
- yt-dlp integration
- YouTube cookies system
- PyTgCalls configuration
- Media streaming logic

### New Dependencies
- Docker Python SDK
- GitHub API (PyGithub)
- Payment gateway SDKs
- QR code generation

### Configuration Files Needed
- config.py (main config)
- config_local.py (secrets)
- .env (environment variables)
- docker-compose.yml (if multi-container)
- requirements.txt
- .gitignore

---

## Implementation Priority

### High Priority (Execute First)
1. Phase 1 - Voice Chat & Music (core functionality)
2. Phase 7 - Emoji & Animations (preserve existing)
3. Phase 8 - Branding (apply throughout)

### Medium Priority
4. Phase 2 - GitHub Integration (developer workflow)
5. Phase 4 - Utility Commands (operational needs)

### Lower Priority (But Important)
6. Phase 3 - Payment System (specific use case)
7. Phase 5 - Docker Automation (deployment)
8. Phase 6 - Sudo System (multi-user)

---

## Success Criteria

### Functionality
- [ ] All commands working as specified
- [ ] No regression in existing features
- [ ] Smooth animations maintained
- [ ] Emoji mapping complete
- [ ] Database integrity preserved

### Code Quality
- [ ] Clean, documented code
- [ ] Proper error handling
- [ ] Consistent branding
- [ ] Type safety where possible
- [ ] No security vulnerabilities

### User Experience
- [ ] Intuitive commands
- [ ] Clear feedback
- [ ] Fast response times
- [ ] Helpful error messages
- [ ] Professional presentation

---

## Risk Management

### Potential Issues
1. **PyTgCalls Compatibility** - Test on Termux environment
2. **Docker in VPS** - Ensure VPS supports Docker
3. **GitHub Token Security** - Implement secure storage
4. **Sudo Isolation** - Prevent resource conflicts
5. **Database Migration** - Backup before changes

### Mitigation Strategies
- Test incrementally
- Backup before major changes
- Fallback mechanisms
- Clear error messages
- Rollback capability

---

## Timeline Estimate (This Session)

With ~80k tokens remaining:

**Phase 1:** ~15k tokens (VC & Music)
**Phase 7:** ~5k tokens (Emoji check)
**Phase 8:** ~10k tokens (Branding)
**Phase 2:** ~20k tokens (Git integration)
**Phase 4:** ~15k tokens (Utilities)
**Phase 3:** ~10k tokens (Payment)
**Buffer:** ~5k tokens (Testing/fixes)

**Total:** ~80k tokens
**Target:** Stop at ~3k remaining

---

**Developed by Vzoel Fox**
**Contact: @VZLfxs**
