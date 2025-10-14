# 🧠 Kaggle Copilot Frontend

A beautiful, modern Streamlit-based frontend for the Kaggle Competition Assistant multi-agent system.

## ✨ Features

- **🎯 Copilot-style Interface**: Clean, professional chat interface
- **👤 User Profiles**: Save your Kaggle username and competition details
- **💬 Real-time Chat**: Interactive conversation with the multi-agent system
- **📚 Chat History**: Save and load previous conversations
- **🔗 Backend Integration**: Seamless connection to Flask backend
- **🎨 Modern UI**: Beautiful gradients and responsive design
- **📱 Responsive**: Works on desktop and mobile

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Backend running on `http://localhost:5000`

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the frontend:**
   ```bash
   python run_frontend.py
   ```
   
   Or directly with Streamlit:
   ```bash
   streamlit run app.py
   ```

3. **Open your browser:**
   - Navigate to `http://localhost:8501`
   - Set up your profile in the sidebar
   - Start chatting with your AI assistant!

## 🎨 Interface Overview

### Sidebar Features
- **Competition Setup**: Enter your Kaggle username and competition details
- **System Status**: Real-time backend connection status
- **Chat History**: Access previous conversations
- **Clear Chat**: Reset current conversation

### Main Chat Area
- **Welcome Screen**: Introduction and feature overview
- **Message Bubbles**: User messages (blue) and AI responses (pink)
- **Processing Indicators**: Shows when the multi-agent system is thinking
- **Error Handling**: Clear error messages and troubleshooting tips

## 🔧 Configuration

### Backend URL
The frontend connects to the backend at `http://localhost:5000` by default. To change this:

1. Edit `app.py`
2. Modify the `BACKEND_URL` variable:
   ```python
   BACKEND_URL = "http://your-backend-url:port"
   ```

### Customization
- **Styling**: Modify the CSS in the `st.markdown()` section
- **Features**: Add new functionality in the `main()` function
- **API Integration**: Update the `submit_query_to_backend()` function

## 🐛 Troubleshooting

### Backend Connection Issues
- Ensure the Flask backend is running on port 5000
- Check the backend URL in `app.py`
- Verify firewall settings allow localhost connections

### Installation Issues
- Make sure you have Python 3.8 or higher
- Try upgrading pip: `pip install --upgrade pip`
- Install dependencies individually if batch install fails

### Performance Issues
- The multi-agent system may take 10-30 seconds to respond
- Large conversations may slow down the interface
- Consider clearing chat history if needed

## 🚀 Deployment

### Streamlit Cloud
1. Push your code to GitHub
2. Connect your repo to Streamlit Cloud
3. Set environment variables for backend URL
4. Deploy!

### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

### Local Production
```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

## 📱 Mobile Support

The interface is responsive and works well on mobile devices. The sidebar collapses automatically on smaller screens.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is part of the Kaggle Competition Assistant system.

