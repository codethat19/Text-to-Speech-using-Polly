## Setup guide for Text to Speech using Amazon Polly
1. Install virtual environment `pip install virtualenv`
2. Setup local virtual environment for package installation `virtualenv myenv`
3. Activating the virtual environment `myenv\Scripts\activate`
4. Installing Dependencies `pip install -r requirements.txt`
5. Running the app :
    a. `cd app\main\service`
    b. `uvicorn main:app --reload`