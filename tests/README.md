# Selenium-тесты валидации документов

Тест-кейсы на проверку валидации загружаемых документов на каждом из четырёх
этапов мастера. Всего 43 теста.

Мастер на главной странице состоит из четырёх вкладок, и документ может быть
отклонён на любой из них:

| Этап | Вкладка | Файл с тестами | Тестов |
|------|---------|----------------|--------|
| 1 | Загрузка шаблона | `test_template_upload.py` | 13 |
| 2 | Загрузка таблицы данных | `test_datatable_upload.py` | 11 |
| 3 | Верификация | `test_verification.py` | 9 |
| 4 | Генерация и скачивание | `test_render_download.py` | 10 |

## Запуск

Весь стек (приложение, MongoDB, браузер) поднимается одной командой:

    docker compose -f docker-compose.selenium.yml up --abort-on-container-exit

Здесь приложению выставлен `RECAPTCHA_DISABLED=1`, потому что reCAPTCHA
требует живых ключей и обращается к Google.

Прогон с настоящими ключами — положите их в `.env` по образцу `.env.example`:

    docker compose -f docker-compose.localhost.yml up --abort-on-container-exit

Ключ reCAPTCHA привязан к домену, поэтому здесь контейнер с браузером делит
сетевое пространство с приложением: страница открывается как `localhost:5000`,
и Google принимает токен.

## Этап 1: загрузка шаблона

| Тест | Что проверяет |
|------|---------------|
| `test_valid_template_format_accepted` | все шесть форматов (docx, xlsx, pptx, odt, ods, odp) принимаются |
| `test_invalid_template_format_rejected` | txt, pdf, jpg отклоняются с «File extension is not supported» |
| `test_no_template_file_shows_error` | загрузка без выбранного файла даёт «No file chosen» |
| `test_empty_template_rejected` | пустой файл отклоняется сервером |
| `test_corrupted_template_handled_gracefully` | мусорные байты с расширением .docx не ломают интерфейс |
| `test_large_template_rejected` | файл больше 15 МБ отклоняется на клиенте |

## Этап 2: загрузка таблицы данных

| Тест | Что проверяет |
|------|---------------|
| `test_valid_data_format_accepted` | csv, xlsx, xls принимаются |
| `test_invalid_data_format_rejected` | txt, pdf, jpg отклоняются |
| `test_no_data_file_shows_error` | загрузка без выбранного файла даёт «No file chosen» |
| `test_empty_data_file_rejected` | пустой csv отклоняется сервером |
| `test_corrupted_xls_data_file_rejected` | битый xls не парсится, приходит ошибка |
| `test_corrupted_csv_data_file_rejected` | csv не в UTF-8 не декодируется, приходит ошибка |
| `test_large_data_file_rejected` | файл больше 15 МБ отклоняется на клиенте |

## Этап 3: верификация

Здесь документы разбираются впервые: из шаблона извлекаются плейсхолдеры
jinja2 и сверяются с колонками таблицы.

| Тест | Что проверяет |
|------|---------------|
| `test_verification_reports_field_mismatches` | отчёт о несовпадении полей для всех шести форматов |
| `test_verification_offers_csv_fields_for_naming` | колонки csv предлагаются как кнопки, первая подставляется в шаблон имени |
| `test_field_button_appends_to_filename_pattern` | нажатие кнопки поля дописывает тег в шаблон имени |
| `test_verification_of_corrupted_template_rejected` | битый шаблон не разбирается, приходит ошибка |

Сообщения проверяются на английском, поэтому перед запросом выставляется
cookie `_LOCALE_=en`.

## Этап 4: генерация и скачивание

| Тест | Что проверяет |
|------|---------------|
| `test_render_produces_one_file_per_data_row` | по одному документу на строку данных для docx, odt, xlsx |
| `test_render_offers_archive_of_all_files` | предлагается zip со всеми файлами |
| `test_generated_files_are_downloadable` | каждая ссылка отдаёт непустой файл |
| `test_filename_pattern_drives_generated_names` | шаблон имени управляет именами: `{{ last_name }}` даёт `B.docx`, `D.docx`, `я.docx` |
| `test_corrupted_template_never_reaches_render` | битый шаблон не доходит до генерации, вкладки остаются закрытыми |
| `test_start_over_resets_the_wizard` | кнопка сброса возвращает мастер на первый шаг |

## Устройство

`pages/home_page.py` — page object главной страницы: селекторы и действия всех
четырёх вкладок, ожидания загрузки и чтение результатов.

`conftest.py` — фикстуры. Валидные шаблоны и таблица берутся из
`app/tests/templates` и `app/tests/data`, xlsx и xls генерируются через
openpyxl. Файлы для негативных проверок создаются на лету: неподдерживаемые
расширения, пустые, битые и превышающие лимит размера.

Переменные окружения: `BASE_URL` — адрес приложения, `HEADLESS=0` — показать
браузер, `CHROME_BIN` — путь до chromium.
