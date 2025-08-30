# Contributing to CtrlHub

Thank you for your interest in contributing to CtrlHub! This project aims to make control systems education accessible and engaging through hands-on experimentation and first-principles learning.

## 🎯 Project Mission

CtrlHub bridges the gap between theoretical control systems knowledge and practical implementation by providing:
- Real hardware integration with educational software
- Mathematical modeling from first principles
- Professional-grade simulation tools in an educational context
- Modern web interfaces with desktop agent capabilities

## 🤝 How to Contribute

### 🐛 Bug Reports

When reporting bugs, please include:
- **Environment**: OS, Python version, browser version
- **Hardware Setup**: Arduino model, sensors, actuators
- **Steps to Reproduce**: Clear, numbered steps
- **Expected vs Actual**: What should happen vs what actually happens
- **Logs**: Include relevant error messages or log files

### 💡 Feature Requests

We welcome suggestions for:
- New educational modules or experiments
- Additional hardware support (sensors, actuators, microcontrollers)
- Enhanced simulation capabilities
- UI/UX improvements
- Documentation improvements

### 🔧 Code Contributions

#### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/CtrlHub.git
   cd CtrlHub
   ```

2. **Backend Development**
   ```bash
   cd local_agent
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -e .  # Install in development mode
   ```

3. **Frontend Development**
   ```bash
   cd frontend
   npm install
   npm start
   ```

4. **Run Tests**
   ```bash
   # Backend tests
   cd local_agent
   pytest

   # Frontend tests
   cd frontend
   npm test
   ```

#### Code Standards

**Python Code**
- Follow PEP 8 style guidelines
- Use type hints for function signatures
- Write docstrings for all public functions and classes
- Include unit tests for new functionality
- Mathematical models should be documented with equations

**TypeScript/React Code**
- Use functional components with hooks
- Follow React best practices
- Implement proper error boundaries
- Use TypeScript strict mode
- Document props and interfaces

**Educational Focus**
- All features should enhance learning outcomes
- Include comprehensive documentation
- Provide clear examples and use cases
- Consider progressive difficulty levels

#### Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write clean, well-documented code
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Thoroughly**
   - Run all existing tests
   - Test with real hardware when applicable
   - Verify across different platforms

4. **Submit Pull Request**
   - Provide clear description of changes
   - Link to related issues
   - Include screenshots for UI changes
   - Request specific reviewers if needed

### 📚 Documentation

We appreciate help with:
- **User Guides**: Step-by-step tutorials for students
- **Hardware Setup**: Wiring diagrams and assembly instructions
- **API Documentation**: Comprehensive endpoint documentation
- **Educational Content**: Theoretical background and exercises
- **Troubleshooting**: Common issues and solutions

## 🏗️ Architecture Guidelines

### Educational Philosophy
- **First Principles**: Start with fundamental physics and mathematics
- **Experimental Validation**: Real measurements vs theoretical predictions
- **Progressive Complexity**: Build from simple to advanced concepts
- **Hands-On Learning**: Physical hardware interaction essential

### Technical Architecture
- **Separation of Concerns**: Clear boundaries between frontend, agent, and hardware
- **Platform Independence**: Support Windows, macOS, and Linux
- **Scalability**: Design for classroom deployment (20-30 students)
- **Reliability**: Robust error handling and recovery mechanisms

### Code Organization
```
CtrlHub/
├── frontend/              # React web application
├── local_agent/          # Python desktop application
│   ├── models/           # Mathematical models (DC motor, etc.)
│   ├── controllers/      # Control algorithms (PID, etc.)
│   ├── simulations/      # Simulation engine
│   ├── hardware/         # Hardware interfaces
│   └── gui/              # Desktop GUI components
├── arduino/              # Arduino firmware
├── docs/                 # Documentation
└── installer/            # Installation scripts
```

## 🧪 Testing Guidelines

### Unit Tests
- Test mathematical models against known solutions
- Validate control algorithms with standard test cases
- Mock hardware interfaces for consistent testing

### Integration Tests
- Test full workflow from frontend to hardware
- Validate data flow and communication protocols
- Test error handling and recovery

### Hardware Tests
- Test with multiple Arduino models
- Validate different motor and sensor combinations
- Ensure robust serial communication

## 📋 Development Workflow

1. **Issue Discussion**: Discuss major changes in GitHub issues first
2. **Development**: Create feature branch and implement changes
3. **Testing**: Comprehensive testing on multiple platforms
4. **Documentation**: Update relevant documentation
5. **Review**: Code review process with maintainers
6. **Integration**: Merge after approval and testing

## 🏷️ Release Process

### Version Numbering
- **Major**: Breaking changes or significant new features
- **Minor**: New features, backward compatible
- **Patch**: Bug fixes and minor improvements

### Release Types
- **Development**: Continuous integration builds
- **Beta**: Feature-complete, testing phase
- **Stable**: Production-ready releases

## 🆘 Getting Help

- **GitHub Discussions**: General questions and community support
- **GitHub Issues**: Bug reports and feature requests
- **Documentation**: Comprehensive guides at docs/
- **Email**: team@ctrlhub.edu for sensitive matters

## 🎓 Educational Impact

When contributing, consider:
- **Learning Objectives**: How does this enhance student understanding?
- **Accessibility**: Can students with different backgrounds use this?
- **Engagement**: Does this make learning more interactive and fun?
- **Real-World Relevance**: Connection to industry practices

## 📜 Code of Conduct

### Our Standards
- **Respectful Communication**: Professional and constructive feedback
- **Inclusive Environment**: Welcome contributors of all backgrounds
- **Educational Focus**: Keep student learning as primary goal
- **Collaborative Spirit**: Work together to improve the platform

### Unacceptable Behavior
- Harassment or discriminatory language
- Personal attacks or trolling
- Sharing private information without permission
- Any behavior inappropriate in an educational setting

## 🙏 Recognition

Contributors will be recognized through:
- **GitHub Contributors**: Automatic recognition in repository
- **Documentation Credits**: Listed in project documentation
- **Release Notes**: Significant contributions highlighted
- **Community Recognition**: Featured in project updates

## 📞 Contact

- **Project Lead**: [Your Name] - your.email@ctrlhub.edu
- **Community**: GitHub Discussions
- **Issues**: GitHub Issues
- **Security**: security@ctrlhub.edu

---

**Thank you for helping make control systems education more accessible and engaging for students worldwide!** 🎛️📚