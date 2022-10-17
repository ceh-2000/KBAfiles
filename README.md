# KBA Files

## Prerequisites
1. Install Python 3.9 using the `pyenv` package manager: https://realpython.com/intro-to-pyenv/
2. Create a new virtual environment with Python 3.9 as the chosen installation. 
   With `pyenv`, run the following:
   
   `pyenv virtualenv 3.9 <environment_name>`
   
    Choose an environment name for `<environment_name>` like `kba_env`.
3. Install `pip3`, a Python package manager: https://monsterhost.com/what-is-pip-and-how-to-install-pip3/
4. Install the necessary dependencies: `pip3 install -r requirements.txt`

## Running script
1. `cd` to the root of the directory.
2. Run the following and replace `<authentication_token>` with a token provided by the [Key Biodiversity Areas Secretariat](https://www.keybiodiversityareas.org/):

    `python3 main.py --token <authentication_token>`

