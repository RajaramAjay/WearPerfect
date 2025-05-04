# WearPerfect: AI-Powered Weather-Based Outfit Recommendation System

## 🌟 Project Overview

WearPerfect is an AI-powered outfit recommendation system that assists users in selecting suitable clothing based on real-time weather and travel plans. The system enables users to upload images of their wardrobe, extract clothing attributes using CNN models, and receive context-aware outfit suggestions. It also includes a travel chatbot for optimized packing lists.

---

## 📋 Table of Contents

1. [Features](#features)
2. [Project Architecture](#project-architecture)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Screenshots](#screenshots)
6. [Deployment](#deployment)
7. [Future Scope](#future-scope)
8. [Contributors](#contributors)
9. [License](#license)

---

## ✨ Features

* Attribute extraction from user-uploaded clothing images.
* Rule-based score calculation for warmth, breathability, and occasion.
* Weather-based outfit recommendations using K-Prototypes clustering.
* Travel chatbot for generating packing lists based on destination, duration, and activity.
* Interactive web application with three modules:

  * Virtual Wardrobe
  * Instant Recommendations
  * Travel Packing Assistant

---

## 🏗️ Project Architecture
<p align="center">
  <img src="Journey%20-%20visual%20selection.png" width="700"/>
</p>
<p align="center"><i>This flowchart represents the end-to-end lifecycle from user wardrobe upload to real-time recommendations and travel packing assistance.</i></p>

---

## 🧰 Installation

```bash
# Clone the repo
$ git clone https://github.com/RajaramAjay/WearPerfect.git
$ cd WearPerfect

# Create a virtual environment
$ python -m venv venv
$ source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install required packages
$ pip install -r requirements.txt
```

---

## 🚀 Usage

1. Upload top and bottom wear clothing images.
2. System extracts attributes and calculates scores.
3. Choose "Instant Recommendation" or use the "Travel Chatbot."
4. Receive personalized outfit suggestions or travel packing list.

---

## 🖼️ Screenshots

* Virtual Wardrobe Interface
* Real-time Recommendation Display
* Travel Chatbot Interaction

(*Add your image files in `/assets/screenshots/` and embed them here*)

---

## ☁️ Deployment

* GitHub Repository ✅
* Local deployment through Flask/Gradio (optional)
* Future scope: Hosting on Streamlit or Hugging Face Spaces

---

## 🔮 Future Scope

* Integrate virtual try-on using pretrained models like StableVITON.
* Expand scoring to include color psychology for mood matching.
* Use advanced weather APIs for longer forecasts.
* Add user feedback loop to fine-tune outfit suggestions.

---

## 👥 Contributors

* Ajay Rajaram
* Sri Harsha Vardhan Madhiri
* Ashok Sai

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 📌 Acknowledgements

* DeepFashion Dataset
* ISO 11092 thermal resistance guidelines
* Hugging Face, OpenWeatherMap APIs
* StableVITON for virtual try-on (future integration)
