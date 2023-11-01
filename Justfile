#initial setup
#install brew
#brew install pyenv
#brew install pyenv-virtualenv

pip-install:
    pipenv lock
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
    pyenv virtualenv $@ $(basename $(pwd))

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
    pipenv run pytest --junit-xml=junit_xml_test_report.xml --cov-branch --cov=table_faker tests
    pipenv run coverage xml -i

build-sdist:
    python3 -m build --sdist table_faker

build-wheel:
    python3 -m build --wheel table_faker

deploy:
    twine upload dist/package-name-version.tar.gz dist/package-name-version-py3-none-any.whl