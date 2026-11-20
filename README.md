# LASER SPOT — сайт студии лазерной эпиляции (Атырау)

Статичный сайт: откройте `index.html` в браузере. Сборка не нужна — можно загрузить папку на любой хостинг (GitHub Pages, Netlify, Tilda «Zero/HTML» и т.п.).

## Структура
- `index.html` — весь текст и разметка
- `styles.css` — оформление (цвета — в блоке `:root` в начале файла)
- `script.js` — меню, анимации, ссылки WhatsApp
- `images/` — все фотографии и логотип
- `favicon.png` — иконка вкладки

## Как заменить
| Что | Где |
|---|---|
| Фотографии | Положите новые файлы в `images/` с теми же именами: `photo-procedure.jpg`, `photo-underarm.jpg`, `photo-face.jpg` (коллаж первого экрана и галерея), `photo-device.jpg` (О нас), `photo-legs.jpg` (Процедура). Затем обновите `alt` у `<img>` в `index.html`. |
| Логотип | `images/logo.png` (круглый, квадратный файл) |
| Адрес | `index.html`, раздел «КОНТАКТЫ»: `<dd ... data-edit="address">Уточнить у администратора</dd>` |
| График работы | там же: `<dd ... data-edit="hours">` |
| Цены и состав | `index.html`, раздел «УСЛУГИ И ЦЕНЫ»: `price__value` — цена, `price__zones` — зоны, `data-wa` у кнопки — текст сообщения |
| Номер WhatsApp | `script.js`, константа `WHATSAPP_NUMBER`, и видимый номер в `index.html` (поиск: `+7 702 582 98 89`) |

Шрифты: Cormorant Garamond (заголовки), Great Vibes (рукописные слова), Montserrat (текст) — Google Fonts.
