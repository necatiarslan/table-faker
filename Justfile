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
    pipenv run pytest --junit-xml=junit_xml_test_report.xml --cov-branch --cov=tablefaker tests
    pipenv run coverage xml -i

build-sdist:
    /Users/necatiarslan/.pyenv/versions/table-faker/bin/python -m build --sdist tablefaker

build-wheel:
    /Users/necatiarslan/.pyenv/versions/table-faker/bin/python -m build --wheel tablefaker

publish:
	#brew install twine
	python setup.py sdist bdist_wheel
	twine upload dist/* 
	#rm -fr build dist .egg tablefaker.egg-info

flake8:
	python -m flake8 tablefaker

pip-install-tablefaker:
    pip install /Users/necatiarslan/GitHub/table-faker/dist/tablefaker-1.0.0-py3-none-any.whl --force-reinstall

clean-files:
    find . -type f -name "*.csv" -exec rm {} \;

test-cli:
    tablefaker --config /Users/necatiarslan/GitHub/table-faker/tests/test_table.yaml
