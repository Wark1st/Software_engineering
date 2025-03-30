workspace {
    name "Travel companion search service"
    !identifiers hierarchical

    model {
        admin = person "Администратор"

        passenger = person "Пассажир" "Присоединяется к поездке" "c1,c2"

        driver = person "Водитель" "Создает поездку и маршрут""c1,c2"

        companion_search = softwareSystem "Сервис поиска попутчиков" {
            description "Сервис, объединяющий в себе информацию о маршрутах и поездках"

            route_db = container "Таблица данных маршрутов" {
                tags "Database" "c2"
                technology "NoSQL Database"

                description "Хранит данные маршрутов"
            }

            trip_db = container "Таблица данных поездок" {
                tags "Database" "c2"
                technology "NoSQL Database"

                description "Хранит данные поездок"
            }

            trip_user_db = container "Таблица пользователей в поезде" {
                tags "Database" "c2"
                technology "NoSQL Database"

                description "Хранит данные пользователей в поездке"
            }

            route_point_db = container "Таблица точек в маршруте" {
                tags "Database" "c2"
                technology "NoSQL Database"

                description "Хранит данные точек в маршруте"
            }

            comp_search_API = container "API application" {
                tags "c2"
                technology "Python FastAPI"
                
                description "Предоставляет функциональность сервиса создания маршрута и поездки через JSON/HTTPS API"
                
                adc = component "sdsds"{
                    
                }

                -> route_db "Получает данные из запроса и сохраняет данные о маршруте" "SQL/TCP" 
                -> trip_db "Получает данные из запроса и сохраняет данные о поездке" "SQL/TCP" "c2"
                -> trip_user_db "Получает данные из запроса и сохраняет данные о пользователях в поездке" "SQL/TCP" "c2"
                -> route_point_db "Получает данные из запроса и сохраняет данные о точках в маршруте" "SQL/TCP" "c2"
            }
        }

        geo_points = softwareSystem "Сервис географических объектов" {
            tags "c2"
            description "Сервис, отвечающий за работу с географическими объектами"
        }

        user_service = softwareSystem "Сервис управления пользователями" {
            tags "c2"
            description "Отвечает за действия с пользовательской информацией"
        }

        auth_service = softwareSystem "Сервис авторизации" {
            tags "c2"
            description "Отвечает за авторизацию, валидацию токенов и регистрацию"
        }

        passenger -> companion_search "" "" "c1"
        passenger -> companion_search.comp_search_API "Создает API запрос через клиент" "JSON/HTTPS""c2"

        admin -> geo_points "Добавляет географические точки" "" "c1"
        admin -> auth_service "Удаляет пользователя" "" "c1"
        
        driver -> companion_search "Создает маршрут/поездку""" "c1"
        driver -> auth_service "Создает УЗ/Добавляет роль к УЗ""" "c1"
        driver -> geo_points "Запрашивает доступные точки маршрута""" "c1"
        driver -> companion_search.comp_search_API "Создает API запрос через клиент" "JSON/HTTPS""c2"

        passenger -> companion_search "Создает маршрут/вступает в поездку""" "c1"
        passenger -> auth_service "Создает УЗ""" "c1"
        
        auth_service -> user_service "Передает информацию при регистрации""" "c1"

        companion_search -> geo_points "Валидирует географические точки""" "c1"
        companion_search -> user_service "Запрашивает информацию о пользователе""" "c1"
        companion_search -> auth_service "Валидирует токен" "" "c1"
        companion_search.comp_search_API -> user_service "Создает API запрос на получение пользователей" "JSON/HTTPS" "c2"
        companion_search.comp_search_API -> geo_points "Создает API запрос на валидацию точек маршрута" "JSON/HTTPS" "c2"
        companion_search.comp_search_API -> auth_service "Создает API запрос на валидацию токена" "JSON/HTTPS" "c2"

        user_service -> auth_service "Валидирует токен""" "c1"

        geo_points -> auth_service "Валидирует токен""" "c1"

        
        
    }

    views {

        themes default

        styles {
            element "Database"{
                shape Cylinder
            }
        }

        systemContext companion_search "context_comp" {
            include *
            autoLayout
        }

        systemContext geo_points "context_geo" {
            include *
            autoLayout
        }

        container companion_search "c2" {
            include *
            exclude "relationship.tag==c1"
            autoLayout
        }

        component companion_search.comp_search_API "c3" {
            include *
            exclude "relationship.tag==c1"
            autoLayout
        }

    }

   
}