# Tableau Prep Flow Complete Variation Generator

## Overview

This application is designed to analyze and optimize Tableau Prep flow files using a Large Language Model (LLM). It leverages the `huihui_ai/qwen2.5-1m-abliterated:14b` model hosted on Ollama to provide detailed analysis and generate optimized variations of Tableau Prep flows. The application is built using Streamlit for the user interface and integrates with the LLM for advanced data processing and recommendations.

## Features

- **Flow Analysis**: Analyze the structure and transformations of a Tableau Prep flow.
- **Optimization Recommendations**: Provide Tableau-specific optimization recommendations.
- **Variation Generation**: Generate a complete, optimized variation of the Tableau Prep flow.
- **Validation**: Ensure the generated flow maintains the original structure and functionality.
- **Comparison**: Compare the original and optimized flows side by side.

## Prerequisites

- Python 3.7+
- Streamlit
- Ollama API access with the `huihui_ai/qwen2.5-1m-abliterated:14b` model
- Required Python packages: `crewai`, `langchain_openai`, `streamlit`, `json`, `pathlib`, `uuid`, `dotenv`, `re`

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/v1gneshkum4r21/tableau-try.git
   cd tableau-try
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the project root and add your Ollama API key:
   ```
   OPENAI_API_KEY=your_ollama_api_key
   ```

## Usage

1. **Run the application**:
   ```bash
   streamlit run app.py
   ```

2. **Upload a Tableau Prep flow JSON file**:
   - Use the file uploader to load your Tableau Prep flow JSON.
   - The application will analyze the flow structure and provide optimization recommendations.

3. **Generate and Review Variation**:
   - Click the "Generate and Review Variation" button to create an optimized variation of the flow.
   - The application will validate the output and save the optimized flow to the `variations` directory.
   - You can compare the original and optimized flows side by side.

## Model Details

- **Model**: `huihui_ai/qwen2.5-1m-abliterated:14b`
- **Hosted on**: Ollama
- **API Base**: `http://localhost:11434/v1`
- **API Key**: Set in the `.env` file

## File Structure

- `app.py`: Main application file containing the Streamlit interface and logic.
- `requirements.txt`: List of required Python packages.
- `.env`: Environment variables for API keys.
- `variations/`: Directory to store generated optimized flow JSON files.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments

- Thanks to Ollama for providing the `huihui_ai/qwen2.5-1m-abliterated:14b` model.
- Built with Streamlit and the `crewai` library for LLM integration.

