#initial setup
#install brew
#brew install pyenv
#brew install pyenv-virtualenv
set shell := ["zsh", "-cu"]
set positional-arguments

run:
    pyenv activate table-faker
    ~/.pyenv/versions/3.11.6/envs/table-faker/bin/python ~/GitHub/table-faker/tests/test_tablefaker.py

pip-install:
    pipenv lock --dev
    pipenv sync
    pipenv requirements > requirements.txt
    pipenv clean

pip-check:
    pipenv check #pipfile
    pipenv verify #pipfile.lock

pip-clean:
    pipenv clean

pip-graph:
    pipenv graph


#show active version
pyenv-version:
    pyenv version

#list local pythons
pyenv-versions:
    pyenv versions

#list of available python distros
pyenv-install-menu:
    pyenv install --list | grep " 3."

#install new python version
pyenv-install *args='':
    pyenv install -v $@

pyenv-uninstall *args='':
    pyenv uninstall -v $@

#provide python version
pyenv-virtualenv-create *args='':
    pyenv virtualenv 3.13.0 $(basename $(pwd))

pyenv-virtualenv-list:
    pyenv virtualenvs

pyenv-virtualenv-activate:
    #pyenv shell $(basename $(pwd))
    #pyenv local $(basename $(pwd)) #create .python-version file
    pyenv activate $(basename $(pwd))
    #pyenv virtualenv-init $(basename $(pwd))

pyenv-virtualenv-deactivate:
    pyenv deactivate $(basename $(pwd))

pyenv-virtualenv-uninstall:
    pyenv virtualenv-delete $(basename $(pwd))

pyenv-current-virtualenv:
    pyenv shell
    pyenv local
    pyenv version

test:
    pipenv run pytest --junit-xml=junit_xml_test_report.xml --cov-branch --cov=tablefaker tests
    pipenv run coverage xml -i

build:
    python setup.py sdist bdist_wheel
    
publish:
	twine upload dist/tablefaker-1.1.0*

# After you run the command, it will ask username and password
# Set your username to __token__
# Set your password to the token value, including the pypi- prefix

flake8:
	python -m flake8 tablefaker

pip-install-tablefaker:
    pip install ~/GitHub/table-faker/dist/tablefaker-1.0.3-py3-none-any.whl --force-reinstall

clean-files:
    find tests/exports -type f -name "*.*" -exec rm {} \;

test-cli:
    tablefaker --config ~/GitHub/table-faker/tests/test_cli.yaml --target ~/GitHub/table-faker/tests/exports
