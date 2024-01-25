# dataiku_python_api
apis needed to automate the dss install/config


I’ve installed the python module on my mac, as it looks like the rest api docs dont showcase how to build an env on an installed plugin but the python docs do.

To install the dataiku module on my mac m1 i did the following

Installed latest python via pyenv needed to include the xz flag on my mac  CFLAGS="-I$(brew --prefix xz)/include" LDFLAGS="-L$(brew --prefix xz)/lib" pyenv install 3.9.1 (python3.9.1 not import lzma · Issue #1800 · pyenv/pyenv )


installed the module that is in the dss pip install(Using the APIs outside of DSS — Dataiku DSS 9.0 documentation 

installed the api module (dataiku-api-client )

I also had to install wheel and pandas via pip

Then imported the module and set the config details

## Installing the environment
- Execute `pipenv install`

## Running the code
- Execute `pipenv run python files/main.py`

## Testing the code
- Set the environment: `. test-env.sh`
- Install testing packages: `pipenv install -d`
- Run the tests: `pipenv run pytest`
