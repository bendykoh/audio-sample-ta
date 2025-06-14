# Audio-sample-ta

This is an assignment to create a full stack application for transcribing and searching a sqlite database.

1. [Assumptions](#assumptions)
2. [Starting Up](#starting-up)
3. [Containerization](#containerization)
4. [Test Cases](#test-cases)
5. [Future Improvement](#future-improvement-notes)

# Assumptions

- Only `.mp3` files will be accepted for now
- We are persisting the database in a local volume, in this case it is stored as `~/<path_to_repo>/audio-sample-ta/backend/transcription.db`.
  - In most cases, we would not be able to keep the storage locally and on git
  - But in this case, since we are using sqlite which is usually popular for in memory, I make the results persistent by storing it on a database in order to show the work done to create the entries to a new database.
- The setup works in containerization, local repo package installation is not needed.
- When a file with similar name is uploaded, it will be appended with a `_1`, `_2` etc.
- Assumes that conda has been installed on the host machine
- Assumes that we are currently using Windows machine to do development

# Starting up

1. The script `setup.bat` will start the creation of conda environment and the relevant python version
2. In the repository root, run `.\setup.bat`
3. After completion, there will be a new file called `install_packages.bat` created.
4. Run `conda activate audio-sample-env`
5. Run `.\install_packages.bat`. The packages will be installed in the virtual environment

# Containerization

To run the service, run `docker compose up --build` in root repo directory. Alternatively use `make start-containers` if Make commands are supported. run `docker compose down` to stop containers.

# Test cases

This section covers how to run test cases for both compoments

## Backend

- Run `pip install -r requirements.txt` in `/backend` to get all packages installed for python including test
- To run the test cases for the python backend, simply run `cd backend` and `pytest test`

## Frontend

- Run `npm install` in `/frontend` to get all packages installed for react
- To run the test cases for the python backend, simply run `cd frontend` and `npm test`

# Future Improvement Notes:

- Add API key verification between frontend and backend, so that people cannot randomly send request to backend without an API key
- and/or alternatively add a reverse proxy so that users cannot access backend
- Check for other formats that `whisper` model allows, and handle the formats dynamically in backend to do processing
