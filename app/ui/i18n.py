"""Static interface translations; generated documents keep their original language."""

import streamlit as st

TEXT = {
    "Подготовка полного плана может занять до трёх минут. Не запускайте повторно, пока идёт генерация.": "Generating a complete plan can take up to three minutes. Please do not submit again while generation is running.",
    "ОТ ИДЕИ К ПЛАНУ РАЗРАБОТКИ": "FROM IDEA TO DEVELOPMENT PLAN",
    "Как пользоваться": "How to use",
    "Режим: {mode}": "Mode: {mode}",
    "Демо": "Demo",
    "Токены за день (расход + резерв): {used:,} / {limit:,}. Сброс в 00:00 по Израилю.": "Daily tokens (used + reserved): {used:,} / {limit:,}. Resets at midnight Israel time.",
    "Деморежим: один общий пример для любой идеи, без вызова OpenAI.": "Demo mode: the same generic example for every idea, with no OpenAI call.",
    "Генерация не настроена. Проверьте ключ и настройки сервера.": "Generation is not configured. Check the API key and server settings.",
    "Генерация через OpenAI. Каждый запуск расходует токены.": "Generation via OpenAI. Each run uses tokens.",
    "Сервер недоступен. Нужно запустить API вместе с интерфейсом.": "Server unavailable. Start the API alongside the interface.",
    "Сохранённые планы": "Saved plans",
    "Обновить список": "Refresh list",
    "Происхождение неизвестно": "Unknown origin",
    "После первой успешной генерации здесь появится ваш план.": "Your plan will appear here after the first successful generation.",
    "Превратите идею в план разработки": "Turn your idea into a development plan",
    '<p class="intro">Опишите, что хотите создать. Вы получите черновик требований, архитектуру и задачи для первой версии. Само приложение нужно будет разработать по этому плану.</p>': '<p class="intro">Describe what you want to build. Get draft requirements, architecture and tasks for the first release. The application itself still needs to be developed from this plan.</p>',
    "**1. Опишите идею** → **2. Создайте план** → **3. Проверьте и скачайте документы**": "**1. Describe your idea** → **2. Generate a plan** → **3. Review and download documents**",
    "01 / Опишите будущий продукт": "01 / Describe your product",
    "Идея продукта *": "Product idea *",
    "Сервис для репетитора: хранить учеников, назначать занятия и видеть расписание на неделю…": "A workspace for tutors to manage students, schedule lessons and view the week…",
    "Обязательное поле, минимум 10 символов. Кто пользователь, какая у него проблема и что он сможет сделать?": "Required, at least 10 characters. Who is the user, what problem do they have and what will they be able to do?",
    "Для кого": "Who is it for?",
    "Например, частные репетиторы": "For example, independent tutors",
    "Необязательно. Укажите конкретную аудиторию и её особенности.": "Optional. Describe the intended audience and their needs.",
    "Дополнительно: сценарий, ограничения и технологии": "More options: workflow, constraints and technologies",
    "Сценарий работы": "User workflow",
    "Добавить ученика → назначить занятие → открыть расписание": "Add a student → schedule a lesson → view the timetable",
    "Необязательно. Несколько действий пользователя по порядку.": "Optional. List a few user actions in order.",
    "Ограничения": "Constraints",
    "Один разработчик, неделя, без платежей и уведомлений": "One developer, one week, no payments or notifications",
    "Необязательно. Срок, ресурсы и функции, которые не нужны в первой версии.": "Optional. Deadline, resources and features to exclude from the first release.",
    "Технологии": "Technologies",
    "Набор инструментов для разработки. Если не знаете, оставьте предложенный вариант.": "Your preferred development tools. If unsure, keep the suggested stack.",
    "Создать план разработки →": "Generate development plan →",
    "Первый раз здесь?": "First time here?",
    "Начните с примера: посмотрите, как описать идею, затем замените текст своим.": "Start with an example to see how to describe an idea, then replace it with your own.",
    "Заполнить пример": "Fill in an example",
    "Заменит текст во всех полях. Генерация начнётся только по кнопке «Создать план разработки».": "Replaces all fields. Generation only starts when you click Generate development plan.",
    "Обязательно только поле со звёздочкой. Можно писать по-русски.": "Only the field marked * is required. You can write in English or Russian.",
    "**Что вы получите**  \nТребования, архитектуру, данные, API, план работ и список допущений.": "**What you get**  \nRequirements, architecture, data model, API, delivery plan and assumptions.",
    "**Что делать с результатом**  \nПроверьте требования и допущения, скачайте ZIP с документами и передайте разработчику или используйте для своей работы.": "**What to do next**  \nReview requirements and assumptions, download the documents as a ZIP and share them with a developer or use them yourself.",
    "**Уже создавали план?**  \nОткройте его в разделе «Сохранённые планы» слева — это не расходует токены.": "**Already generated a plan?**  \nOpen it under Saved plans on the left. Reopening uses no tokens.",
    "В режиме OpenAI описание отправляется модели. Не указывайте пароли, API-ключи и реальные данные клиентов.": "In OpenAI mode, your brief is sent to the model. Do not include passwords, API keys or real customer data.",
    "Опишите продукт подробнее: минимум 10 символов после удаления пробелов по краям.": "Describe your product in at least 10 characters, excluding surrounding spaces.",
    "Создаём план и проверяем документы. Дождитесь результата…": "Generating your plan and checking documents. Please wait…",
    "02 / Ваш план разработки": "02 / Your development plan",
    "Начните с вкладок «Требования» и «Допущения». Затем изучите план работ и скачайте документы ниже.": "Start with Requirements and Assumptions. Then review the Delivery plan and download the documents below.",
    "Сущности данных": "Data entities",
    "Запросы API": "API endpoints",
    "Задачи разработки": "Development tasks",
    "Требования": "Requirements",
    "Архитектура": "Architecture",
    "Данные": "Data model",
    "План работ": "Delivery plan",
    "Допущения": "Assumptions",
    "Подготовить ZIP": "Prepare ZIP",
    "Скачать документы ↓": "Download documents ↓",
    "ZIP с документами Markdown, исходниками схем Mermaid и данными JSON. Скачайте и передайте разработчику.": "ZIP with Markdown documents, Mermaid diagram sources and JSON data. Download and share with your developer.",
    "План появится здесь после генерации. Заполните идею выше или нажмите «Заполнить пример».": "Your plan will appear here after generation. Describe your idea above or click Fill in an example.",
    "Демо · Общий пример документов. Он не адаптирован к вашей идее.": "Demo · Generic document example, not adapted to your idea.",
    "Создано с OpenAI · Структура и ссылки между документами проверены.": "Generated with OpenAI · Structure and document references checked.",
    "Происхождение неизвестно · Это старый результат, согласованность документов не проверена.": "Unknown origin · Legacy result; document consistency has not been checked.",
    "Источник: {source} · Модель: {model} · Сохранено: {created}": "Source: {source} · Model: {model} · Saved: {created}",
    "Идентификатор: {id}": "Generation ID: {id}",
    "Детали проверки документов": "Document validation details",
    "Ошибка запроса (HTTP {status}). Проверьте введённые данные и повторите.": "Request failed (HTTP {status}). Check your input and retry.",
    "Сервер недоступен или истекло время ожидания. Проверьте историю перед повторным запуском.": "Server unavailable or request timed out. Check saved plans before retrying.",
    "{code} · Режим: {mode} · Новый результат не создан": "{code} · Mode: {mode} · No new result created",
    "Помощь: от идеи до готового плана": "Help: from idea to development plan",
    "Переключение языка меняет интерфейс. Текст идеи и созданные документы сохраняются на исходном языке.": "Switching language changes the interface. Your brief and generated documents keep their original language.",
    "Проблема": "Problem",
    "Пользователь": "Target user",
    "Входит в первую версию": "Scope in",
    "За пределами первой версии": "Scope out",
    "Путь пользователя": "User journey",
    "Нефункциональные требования": "Non-functional requirements",
    "Открытые вопросы": "Open questions",
    "Компоненты": "Components",
    "Потоки данных": "Data flow",
    "Риски": "Risks",
    "Схема Mermaid": "Mermaid diagram",
    "Поле": "Field",
    "Тип": "Type",
    "Первичный ключ": "Primary key",
    "Ссылка": "References",
    "Исходник схемы данных Mermaid": "Mermaid ERD source",
    "День 1": "Day 1",
    "Дни 2–3": "Days 2–3",
    "Неделя 1": "Week 1",
    "Проверка готовности": "Done checklist",
}

EN_TO_RU = {english: russian for russian, english in TEXT.items()}

ERRORS = {
    "provider_timeout": (
        "Модель не успела ответить. Результат не сохранён. Проверьте счётчик токенов перед повтором.",
        "The model timed out. No result was saved. Check your token counter before retrying.",
    ),
    "daily_token_limit": (
        "Дневной лимит исчерпан. Он сбросится в 00:00 по Израилю.",
        "Daily token budget exhausted. It resets at midnight Israel time.",
    ),
    "provider_error": (
        "OpenAI отклонил запрос. Проверьте ключ, доступ к модели и настройки сервера.",
        "OpenAI rejected the request. Check your key, model access and server settings.",
    ),
    "provider_rate_limit": (
        "Достигнут лимит или исчерпан баланс OpenAI. Проверьте свой API-аккаунт.",
        "OpenAI rate or quota limit reached. Check your API account.",
    ),
    "provider_unavailable": (
        "Нет связи с OpenAI. Попробуйте позже.",
        "Cannot connect to OpenAI. Try again later.",
    ),
    "missing_api_key": (
        "На сервере не задан ключ OpenAI. Добавьте его в настройки и перезапустите API.",
        "OpenAI mode requires OPENAI_API_KEY on the server. Configure it and restart the API.",
    ),
    "invalid_mode": (
        "Неизвестный режим генерации. Проверьте настройки сервера.",
        "Unknown generation mode. Check server settings.",
    ),
    "incomplete_response": (
        "Модель вернула неполный ответ. Попробуйте упростить описание.",
        "The model returned an incomplete response. Try simplifying your brief.",
    ),
    "invalid_provider_response": (
        "Модель вернула некорректный ответ. Попробуйте ещё раз.",
        "The model returned an invalid response. Please retry.",
    ),
    "invalid_specification": (
        "Документы не прошли проверку. Упростите первую версию и повторите запрос.",
        "Document validation failed. Simplify the first release and retry.",
    ),
}


def language() -> str:
    return st.session_state.get("language", "ru")


def persist_language() -> None:
    st.query_params["lang"] = language()


def tr(text: str, **values) -> str:
    translated = TEXT.get(text, text) if language() == "en" else EN_TO_RU.get(text, text)
    return translated.format(**values) if values else translated


def error_message(code: str, status: int) -> str:
    pair = ERRORS.get(code)
    if pair:
        return pair[language() == "en"]
    return tr(
        "Ошибка запроса (HTTP {status}). Проверьте введённые данные и повторите.", status=status
    )
