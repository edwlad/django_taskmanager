@REM python -m coverage erase
@REM python -m coverage run --source=app_task,api_task manage.py test app_task.tests.BaseModifyTestCase
@REM python -m coverage run --source=app_task,api_task manage.py test app_task.tests.BaseCorrectTestCase
@REM python -m coverage run --source=app_task,api_task manage.py test
@REM python -m coverage report --show-missing --skip-covered --skip-empty
@REM python -m coverage report --skip-covered --skip-empty
python manage.py test --cov --skip-covered --skip-empty
