# WearPerfect

An AI-powered wardrobe management and outfit recommendation system that helps users organize their clothing and get personalized outfit suggestions based on weather conditions.

## Features

- **Smart Wardrobe Management**
  - Upload and categorize clothing items
  - Automatic attribute detection for clothing items
  - Organize items by type (top wear, bottom wear)

- **Intelligent Recommendations**
  - Weather-based outfit suggestions
  - Event-specific clothing recommendations
  - Trip planning wardrobe assistance

- **User Authentication**
  - Secure login system
  - Personal wardrobe space
  - Password reset functionality

## Installation

1. Clone the repository:
```sh
git clone https://github.com/yourusername/WearPerfect.git
cd WearPerfect
```

2. Install dependencies:
```sh
pip install -r requirements.txt
```

3. Configure the application:
   - Copy `config/config.toml.example` to `config/config.toml`
   - Update the configuration with your settings

4. Run the application:
```sh
python app.py
```

## Project Structure

```
├── app.py                 # Main Flask application
├── config/
│   └── config.toml       # Configuration file
├── data/                 # CSV data files
├── Models/               # ML models
├── src/                  # Source code
├── static/              # Static assets
├── templates/           # HTML templates
└── uploads/            # User uploaded images
```

## Technologies Used

- Python 3.x
- Flask
- TensorFlow/Keras
- OpenAI API
- HTML/CSS/JavaScript
- CSV for data storage

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all contributors who participated in this project
- Special thanks to UMBC for supporting this project
