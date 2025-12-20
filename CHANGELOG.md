# Changelog

## [2.0.0] - 2024-12-19

### ✨ Major Improvements

#### Complete App Rewrite
- **Completely rewrote `app.py`** with professional structure and comprehensive features
- Added type hints and proper documentation throughout the code
- Implemented robust error handling and input validation

#### New Features Implemented
- ✅ **Configurable Neutral Threshold**: Sidebar slider (0.5-0.9) for adjusting confidence threshold
- ✅ **Real-time Statistics Dashboard**: Live metrics showing sentiment distribution
- ✅ **Temperature Indicator**: 3-level health monitoring (Good/Medium/High attention needed)
- ✅ **Complete History Management**: View last 20 or all analyzed tickets
- ✅ **CSV Export**: Download full analysis history
- ✅ **Enhanced Lexicon**: Expanded to 30+ positive and 35+ negative PT-BR terms
- ✅ **Improved CX Readings**: Contextualized recommendations for each sentiment type
- ✅ **Session Management**: Clear history functionality
- ✅ **Modern UI**: Responsive layout with sidebar and improved visual feedback

#### Technical Improvements
- Added `requirements.txt` with all necessary dependencies
- Created comprehensive `.gitignore` for Python projects
- Improved sentiment calculation algorithm with normalized scores
- Added confidence-based classification system
- Implemented proper session state management

#### Documentation
- Updated installation instructions in README.md
- Added code examples and usage guidelines
- Documented all new features

### 🔧 Fixed
- Fixed mismatch between README documentation and actual app implementation
- Resolved missing features that were documented but not implemented
- Improved error messages and user feedback

### 📝 Notes
- App now works standalone with lexical analysis (no ML model file required)
- All roadmap features from v1.0 have been implemented
- Ready for production use in CX analysis workflows
