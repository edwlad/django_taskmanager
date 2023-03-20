# Курсовой по Джанго: TaskManagers

## Введение

Задание: реализовать приложение **TaskManager** для работы с тасками (задачами). Минимальные фичи:

- управление задачами (создание\изменение (в том числе переход по статусам и назначение исполнителя) \удаление)
- управление статусами задачи (создание\изменение (в том числе последовательности статусов) \удаление)
- разделение задач по проектам (+ создание\изменение\удаление проектов)
- разделение задач по спринтам внутри проектов (+создание\изменение\удаление спринтов)
- просмотр истории изменения задач
- оповещение исполнителя об изменении текущего статуса задачи

## Требования

- должна быть авторизация
- должно быть не менее одной модели. Между моделями (не обязательно
всеми) должна существовать связь.
- должны быть юнит-тесты
- должно быть rest api, использоваться сериализаторы drf.
- должно быть логгирование
- должно быть графическое представление для пользователей, которого хватает для управления функционалом приложения

## Реализация

### Используемые ресурсы

- Интерпретатор [Python v 3.10](https://www.python.org/).
- Фреймворк [Django 4.1](https://www.djangoproject.com/).
- База данных [Postgres](https://).
- Модуль [Django REST framework](https://www.django-rest-framework.org/).
- и другие модули [requirements.txt](requirements.txt)

### Работа

#### Общее

В менеджере три основных составляющих (категории): **проект**, **спринт** и **задача**. Спринт обязательно принадлежит проекту. Задача обязательно принадлежит проекту и может принадлежать спринту.

Все пользователи могут просматривать всю информацию в интерфейсе и получать данные с помощью API. Создавать новые записи могут авторизированые пользователи с правом создания записей в определённой категории. Редактировать и удалять может автор записи. Исполнитель задания может изменить дату завершения задания.

При изменении проекта, спринта или задачи записывается информация в истории зависимых не закрытых задач. А так же создаётся email всем авторам и исполнителям зависимых не закрытых спринтов и задач.

По умолчанию, при выводе списка в интерфейсе, выводится список из пяти записей на страницу. В API - десять записей.

При открытии сайта или выборе пункта меню ***"Главная"*** выводится список не завершённых задач.

#### Проекты

При выборе пункта меню ***"Проекты"*** выводится список не завершённых проектов. Отфильтровать проекты по статусу можно с помощью кнопок *"Весь список"*, *"Выполнено"*, *"В работе"*. Авторизированые пользователи могут дополнительно отобрать проекты с помощью кнопок *"Автор"* или *"Без отбота"*. В зависимости от прав будет отображена кнопка *"Добавить"*, а также кнопки *"Редактироваь"* и *"Удалить"* у проектов в списке.

При выборе проекта из списка откроется страница детальной информации. На ней дополнительно будут показаны списки спринтов и задач проекта и, в зависимости от прав, - кнопки *"Добавить"*, *"Редактироваь"* и *"Удалить"*.

Проект нельзя закрыть пока есть не закрытые спринты или задачи. Минимальная дата закрытия вычисляется исходя из даты создания проекта и дат закрытия спринтов и задач проекта.

Удаление проекта удаляет все зависимые спринты и задачи.

#### Спринты

При выборе пункта меню ***"Спринты"*** выводится список не завершённых спринтов. Кнопки отображаются согласно прав пользователя. При выборе спринта из списка откроется страница детальной информации.

Спринт нельзя закрыть пока есть не закрытые задачи. Минимальная дата закрытия вычисляется исходя из даты создания спринта и дат закрытия задач спринта.

Планируемая дата вычисляется как минимальная от планируемых дат выполнения проекта и спринта.

Удаление спринта удаляет все зависимые задачи.

При редактировании спринта проект выбирается из списка не закрытых проектов.

При использовании кнопки добавить со страницы детальной информации, в создаваемом сприте автоматически подставится проект текущего спринта.

#### Задачи

При выборе пункта меню ***"Задачи"*** выводится список не завершённых задач. Кнопки отображаются согласно прав пользователя. При выборе задачи из списка откроется страница детальной информации. В фильтрах по пользователю добаляется пункт *"Исполнитель"*.

На странице детальной информации отображается список зависимых задач (если они есть) и история изменения задачи, а так же истроия изменений в родительской задаче, спринте и проекте. Автор и исполнитель задачи могут добавить информацию в историю.

Зависимость задач друг от друга - одноуровневая. Задача имеющая зависимые задачи не может сама быть зависимой.

Планируемая дата вычисляется как минимальная от планируемых дат выполнения проекта, спринта и задачи.

При редактировании задачи проект выбирается из списка не закрытых проектов. Спринт выбирается из списка не закрытых спринтов проекта (список пересоздаётся при выборе проекта). Родительская задача выбирается из списка не закрытых задач спринта, если выбран спринт. Или списка задач проекта, если спринт не выбран. Список задач пересоздаётся при выборе проекта или спринта.

Исполнитель может изменить только дату закрытия задачи.

При использовании кнопки добавить со страницы детальной информации, в создаваемой задаче автоматически подставятся проект и спринт текущей задачи.

#### Поиск

При выборе пункта меню ***"Поиск"*** выводятся списки не завершённых проектов, спринтов и задач. Можно использовать фильтрацию по статусу и автору. Кнопки отображаются согласно прав пользователя. Поиск производится не зависимо от регистра в названиях проектов, спринтов и задач.

#### API

При выборе пункта меню ***"API"*** выводится вэб интерфейс фреймворка Django REST framework. Работает простой фильтр по имени поля и точному совпадению занчений. Например:  
`/api/tasks/?date_end=none&date_beg=2023-06-10`  
Можно только получать информацию. Создания и редактирования записей через API нет.

#### Авторизация

Если пользователь не авторизирован, в правом верхнем углу отображается пункт меню *"Вход"*. При его выборе окрывается страница авторизации. При успешной авторизации пользователь перенаправляется на главную страницу.

Если пользователь авторизирован, в правом верхнем углу отображается имя пользователя и пункты меню *"Смена"* и *"Выход"*. При выборе *"Смена"* окрывается страница авторизации. При выборе *"Выход"* пользователь переводится в статус не авторизиваного. При успешной переавторизации или выходе, пользователь перенаправляется на главную страницу.

### Особенности

#### Доработка manage.py

Добавлено распознавание аргументов запуска и вывода информации для модуля **Coverage**. Аргументы:

- `--cov` - запускать модуль Coverage
- `--skip-covered` - не выводить в отчете информацию о модулях со 100% покрытием
- `--skip-empty` - не выводить в отчете информацию о пустых модулях
- `--show-missing` - выводить в отчете информацию о пропущеных строках в модулях

Пример команды для запуска тестов:  
`python manage.py --cov --skip-covered --skip-empty test`

#### Тестирование

В тестировании (на момент создания README) два блока.

В первом блоке генерируются случайные данные (если база пустая) и проверяется корректность записанной информации в базе.

Во втором блоке генерируются случайные данные (если база пустая) и имитируеся открытие страниц со списками проектов, спринтов и задач. Проверяется наличие шаблона и коррекность выбранных данных.

Использование кода в тестировании (на момент создания README):

```text
Name  Stmts   Miss  Cover  
TOTAL 1318    364    72%
```

#### Генерация данных

Проект позволяет сгенерировать данные. Можно запустить файл [generator.bat](generator.bat) или, например, воспользоваться командой:  
`python manage.py shell -c="from app_task.functions import gen_data; gen_data(cnt=50, close=60, clear=True, parent=True, clear_user=True)"`  
Запустится функция `gen_data` из модуля `app_task.functions`. Ниже описание параметров функции (указаны значения по умолчанию):

- `cnt=0` - Количество генерируемых проектов,
- `close=0` - Процент закрытия проектов и спринтов
- `clear=False` - Очищать базу перед генерацией
- `parent=False` - Создавать зависимые задачи
- `clear_user=False` - Удалить тестовых пользователей

Даты для данных выбираются из диапазона +\\- 3 месяца от текущей даты. Шаблон начала имени тестового пользователя указан в настройках `MY_TEST_USER`. Если его нет, то - `user`. Пароль - `MY_TEST_PASS` или, если нет, то - `U-321rew`. Шаги генерации данных:

1. Если есть очистка базы, то удаляются все проекты (а соответственно все зависимые спринты и задачи) авторами которых являются тестовые пользователи.
1. Если есть удаление тестовых пользователей, то удаляются пользователи совпадающие с шаблоном.
1. Если количество генерируемых проектов не равно нулю и не найдены тестовые пользователи, то генерируются пять пользователей по шаблону:  
`<значение_MY_TEST_USER><счётчик_начиная_с_0>`  
Пароль - из настрйки `MY_TEST_PASS`
1. Создётся указанное число проектов. Для проекта указывается случайные автор, дата создания и планируемая дата закрытия.  
1. Создётся удвоеное число спринтов. Для спринтов - случайные автор, проект, дата создания и планируемая дата закрытия.  
1. Создётся в десять раз увеличеное число задач. Для задач - случайные автор, исполнитель, проект, спринт, дата создания и планируемая дата закрытия.
1. Если есть зависимые задачи, попытка в поекте создать их. Выбираются две случайные задачи проекта главная и зависимая.
1. Попытка закрыть указанное число спринтов. Выбираются случайные даты закрытия задач (не всех) спринта и дата закрытия спринта.  
1. Попытка закрыть указанное число проектов. Выбирается случайные даты закрытия задач (не всех) проекта и дата закрытия проекта.

Запись данных происходит с помощью метода `save` модели. В результате при записи проверяется корректность информации:

- даты больше/меньше чем надо,
- можно ли создать зависимости
- можно ли закрыть проект/спринт/задачу
- и пр.

