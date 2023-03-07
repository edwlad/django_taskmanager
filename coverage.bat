python -m coverage erase
@REM python -m coverage run --source=app_task,api_task manage.py test app_task.tests.BaseModifyTestCase
@REM python -m coverage run --source=app_task,api_task manage.py test app_task.tests.BaseCorrectTestCase
python -m coverage run --source=app_task,api_task manage.py test
@REM python -m coverage report --show-missing --skip-covered --skip-empty
python -m coverage report --skip-covered --skip-empty
