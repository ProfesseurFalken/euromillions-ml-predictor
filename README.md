# 🎰 EuroMillions ML Prediction System

A comprehensive machine learning system for EuroMillions lottery prediction with live data scraping, model training, and an interactive Streamlit web interface.

## 🌟 Features

- **Live Data Integration**: Automatically scrapes EuroMillions results from UK National Lottery
- **Machine Learning Models**: LightGBM-based prediction models for main numbers and stars
- **Interactive Web UI**: Comprehensive French Streamlit interface
- **Scoring System**: Analyze number frequency, patterns, and generate predictions
- **Data Management**: Full CRUD operations with SQLite database
- **Model Training**: Automated training pipeline with performance metrics
- **Ticket Generation**: AI-powered ticket suggestions with probability scoring

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ProfesseurFalken/euromillions-ml-predictor.git
   cd euromillions-ml-predictor
   ```

2. **Setup environment (Windows)**
   ```powershell
   .\bootstrap.ps1
   ```

   **Setup environment (Linux/Mac)**
   ```bash
   ./bootstrap.sh
   ```

3. **Launch the application**
   ```bash
   # Windows
   .\run_ui.bat
   
   # Linux/Mac
   ./run_ui.sh
   ```

4. **Open your browser**
   Navigate to `http://localhost:8501`

## 📊 Usage

### Web Interface

The Streamlit UI provides five main sections:

1. **🎯 Tableau de Bord**: System overview and status
2. **📊 Gestion des Données**: Initialize and manage historical data
3. **🤖 Entraînement des Modèles**: Train ML models
4. **🎲 Génération de Tickets**: Generate predictions and tickets
5. **⚙️ Configuration**: Environment settings

### Command Line Interface

```bash
# Initialize historical data
python build_datasets.py

# Train models
python cli_train.py

# Generate predictions
python demo_scoring.py

# Test scraping
python demo_scraper.py
```

## 🏗️ Architecture

```
euromillions-ml-prediction/
├── 📁 ui/                    # Streamlit web interface
├── 📁 data/                  # Database and processed data
├── 📁 models/               # Trained ML models
├── 📄 scraper.py            # Web scraping utilities
├── 📄 repository.py         # Database operations
├── 📄 train_models.py       # ML training pipeline
├── 📄 streamlit_adapters.py # UI backend adapters
├── 📄 config.py            # Configuration management
└── 📄 requirements.txt     # Python dependencies
```

## 🔧 Configuration

Create a `.env` file with your settings:

```env
# Scraping Configuration
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
REQUEST_DELAY=1.0
MAX_RETRIES=3

# Database Configuration
DATABASE_PATH=data/draws.db

# Model Configuration
MODEL_PATH=models/
RANDOM_STATE=42

# UI Configuration
STREAMLIT_PORT=8501
```

## 🤖 Machine Learning

### Models

- **Main Numbers Model**: Predicts probability distributions for numbers 1-50
- **Star Numbers Model**: Predicts probability distributions for stars 1-12

### Features

- Historical frequency analysis
- Gap pattern analysis
- Sequence detection
- Statistical correlations
- Time-based patterns

### Performance

Models are evaluated using:
- Log-loss scoring
- Cross-validation
- Out-of-sample testing
- Prediction accuracy metrics

## 📈 Data Sources

- **Primary**: UK National Lottery EuroMillions results
- **Format**: Structured HTML parsing with fallback patterns
- **Frequency**: Twice weekly (Tuesday and Friday)
- **Coverage**: Historical data from 2024 onwards

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python -m pytest test_*.py

# Run specific test files
python test_scraper.py
python test_repository.py
python test_train_models.py
```

## 📦 Dependencies

- **Web Scraping**: requests, beautifulsoup4, lxml
- **Data Processing**: pandas, numpy
- **Machine Learning**: lightgbm, scikit-learn
- **Web Interface**: streamlit
- **Database**: sqlite3 (built-in)
- **Configuration**: pydantic, python-dotenv
- **Utilities**: loguru, tenacity

## 🎯 Prediction Strategy

The system uses multiple approaches:

1. **Frequency Analysis**: Historical number occurrence patterns
2. **Gap Analysis**: Time between number appearances
3. **Pattern Recognition**: Sequence and grouping tendencies
4. **Machine Learning**: Advanced probability modeling
5. **Ensemble Methods**: Combining multiple prediction sources

## 🚨 Disclaimer

This system is for educational and entertainment purposes only. Lottery games are games of chance, and no system can guarantee winning numbers. Please gamble responsibly.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/ProfesseurFalken/euromillions-ml-predictor/issues) page
2. Create a new issue with detailed information
3. Include system information and error logs

## 🎉 Acknowledgments

- UK National Lottery for providing public results data
- LightGBM team for the excellent ML framework
- Streamlit team for the amazing web framework
- Open source community for inspiration and tools

---

**Happy Predicting! 🍀**
