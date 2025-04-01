class Role:
    roles = {
        "ADMIN": {
            "name": "Admin",
            "description_ru": (
                "Права: работа с пользователями (создание, изменение, удаление) ниже ADMIN, "
                "мониторинг и работа со всеми объектами Docker, работа со всеми пользовательскими дашбордами."
            ),
            "description_en": (
                "Permissions: work with users (create, change, delete) below ADMIN, "
                "monitor and work with all Docker objects, work with all custom dashboards."
            ),
        },
        "SUPER_ADMIN": {
            "name": "Super Admin",
            "description_ru": (
                "Права: работа с пользователями (создание, изменение, удаление), изменение пользовательских ролей, "
                "мониторинг и работа со всеми объектами Docker, работа со всеми пользовательскими дашбордами."
            ),
            "description_en": (
                "Permissions: work with users (create, change, delete), change user roles, "
                "monitor and work with all Docker objects, work with all custom dashboards."
            ),
        },
        "USER": {
            "name": "User",
            "description_ru": "Права: мониторинг объектов Docker, создание своих кастомных дашбордов.",
            "description_en": "Permissions: monitor all Docker objects, creating own custom dashboards.",
        },
    }

    ADMIN = roles["ADMIN"]
    SUPER_ADMIN = roles["SUPER_ADMIN"]
    USER = roles["USER"]
