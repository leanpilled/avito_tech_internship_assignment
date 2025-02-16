для запуска приложения
1. создайте в корне проекта файл .env, поместите в него содержимое .env.example и по желанию замените переменные окружения
2. выполните из корня проекта docker compose up --build -d
сервис находится на порту 8080

чтобы прогнать линтеры выполните make lint
чтобы запустить тесты, установите зависимости:
pip3 install uv
uv sync
и с развернутым приложением выполните make test

про задание от меня

работу с транзакциями решил вынести прямо в сервисы, думаю это важная часть бизнес логики
поэтому и реализовал по сути фиктивный класс SessionManager, лишь для того чтобы работа с сессией была как можно более явной,
хотя можно и просто у одного из репозиториев вызывать session.begin() и тд, но это мне показалось не очень красивым решением

чтобы я сделал чуть по-другомк если бы имел больше времени:
  1. в тестах используется боевая бдшка, хоть я и подчищаю все в тестах или можно поднять еще одну тестовую,
  я пытался изначально сделать по-другому, а именно просто работать с бд только внутри транзакции, ничего не комитить, а потом ролбечить
  однако этого у меня не вышло так как моя фикстура по перезаписи сессии в di контейнере упорно отказывалась работать
  (мне удалось ее заменить, но при попытке зарезолвить в тесте какой-нибудь репозиторий или сервис я получал ошибку, что у меня 2 event loop)
  если бы удалось тесты вышли бы куда лаконичнее без лишних commit/delete
  2. прикрутил бы что-нибудь для генерации данных для тестов типо polyfactory или factory_boy

я попытался провести нагрузочное тестирование, но чего-то здравого не вышло
в моем сценарии пользователи сначала логинились, что и стало узким горлом системы
потому что это по сути единственная cpu-bound нагрузка на сервисе (захешировать пароль, сгенерить jwt) - все упералось в ручку логина

что касается потенциальных оптимизаций, я могу предложить лишь добавить полнотекстовый индекс на users.username, чтобы ускорить sendCoin,
а все другие запросы и так по айдишникам ищут/джоинят
