echo "BUILD START"

# create a virtual environment named 'venv' if it doesn't already exist
python3.9 -m venv venv

# activate the virtual environment
source venv/bin/activate

# build_files.sh
pip install -r requirements.txt

echo "BUILD END"

flask run --reload --port 5001