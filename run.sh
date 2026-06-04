#!/usr/bin/env bash
set -e

VENV_DIR=".venv"

if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment in $VENV_DIR"
  python -m venv "$VENV_DIR"
fi

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OS" == "Windows_NT" ]]; then
  # Git Bash / Windows
  source "$VENV_DIR/Scripts/activate"
else
  source "$VENV_DIR/bin/activate"
fi

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Starting FastAPI with uvicorn..."
echo
echo "To run the Streamlit UI (in another terminal) use:"
echo "  source $VENV_DIR/bin/activate  # or .venv\\Scripts\\activate on Windows"
echo "  streamlit run app/ui/streamlit_app.py"
echo

uvicorn app.main:app --reload


