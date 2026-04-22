# Practicum 4 semester lab 10

Flask-приложение для генерации изображений через модель Hugging Face
`black-forest-labs/FLUX.1-schnell`.

## Возможности

- `GET /login` возвращает JSON с идентификатором автора.
- `GET /makeimage` показывает HTML-форму для генерации изображения.
- `POST /makeimage` принимает размеры изображения и текстовый промпт,
  генерирует изображение и возвращает JPEG.

## Установка

Создайте и активируйте виртуальное окружение:

```bash
python3 -m venv venv
source venv/bin/activate
```

Установите зависимости:

```bash
pip install -r requirements.txt
```

## Настройка токена Hugging Face

Создайте файл `.env` в корне проекта и добавьте в него API-токен:

```env
HF_API_TOKEN=ваш_токен_huggingface
```

Токен не хранится в коде. Файл `.env` исключен из Git через `.gitignore`.

## Запуск

Запуск на стандартном порту `5000`:

```bash
flask --app app run
```

Если порт `5000` занят, можно указать другой порт:

```bash
flask --app app run --port 5001
```

После запуска откройте форму:

```text
http://127.0.0.1:5001/makeimage
```

## Маршруты

### GET /login

Возвращает:

```json
{"author": "1160491"}
```

### GET /makeimage

Возвращает HTML-страницу с формой:

- `width` - ширина изображения в пикселях;
- `height` - высота изображения в пикселях;
- `text` - текстовый промпт для модели.

Форма отправляется методом `POST` с типом
`application/x-www-form-urlencoded`.

### POST /makeimage

Параметры формы:

- `width` - положительное целое число;
- `height` - положительное целое число;
- `text` - промпт для генерации изображения.

Ограничения:

- `width` и `height` должны быть положительными целыми числами;
- `width` и `height` должны быть кратны `32`;
- разрешенный диапазон размеров: от `256` до `1024` пикселей.

При успешной генерации сервер возвращает JPEG:

```http
Content-Type: image/jpeg
```

При ошибке возвращается та же форма, а сообщение отображается красным цветом
над формой.

Возможные сообщения:

- `Invalid image size`
- `Width and height must be multiples of 32`
- `Model generation failed: ...`

## Пример запроса

```bash
curl -X POST http://127.0.0.1:5001/makeimage \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "width=512&height=512&text=cyberpunk cat with neon glasses" \
  --output image.jpg
```

В результате файл `image.jpg` будет содержать сгенерированное изображение.
