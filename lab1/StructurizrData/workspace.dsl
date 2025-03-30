workspace {
    name "Travel companion search service"
    !identifiers hierarchical

    model {
        passenger = person "Пассажир" "Присоединяется к поездке" "c1,c2"

        driver = person "Водитель" "Создает поездку и маршрут""c1,c2"

        companion_search = softwareSystem "Сервис поиска попутчиков" {
            description "Сервис, позволяющий зарегистрироваться в сервисе, создать точки маршрута, добавить их в маршрут и создать поездку с добавлением в нее пользователей"
        
            
            
            companion_search_API_db = container "База данных API поездок" {
                tags "Database"
                technology "NoSQL Database"

                description "Хранит схему данных маршрутов, поездок, точек в марщруте и пользователей в поездке"
            }

            auth_API_db = container "База данных API аутентификации" {
                tags "Database"
                technology "PostgreSQL Database"

                description "Хранит схему данных логинов и паролей"
            }

            geo_points_API_db = container "База данных API географических координат" {
                tags "Database"
                technology "PostgreSQL Database"

                description "Хранит схему данных географических координат"
            }

            users_API_db = container "База данных API пользователей" {
                tags "Database"
                technology "PostgreSQL Database"

                description "Хранит схему данных информации о пользователях"
            }

            auth_API = container "API аутентификации" {
                tags ""
                technology "Python FastAPI"

                description "Реализует функциональность сервиса регистрации и валидации токенов"

                -> auth_API_db "Получает данные из запроса и сохраняет и получает данные о логине и пароле пользователе" "SQL/TCP" 
            }

            users_API = container "API пользователей" {
                tags ""
                technology "Python FastAPI"

                description "Реализует функциональность сервиса записи и получения информации о пользователях"
            
                -> users_API_db "Получает данные из запроса и сохраняет и получает данные о пользователе"
                -> auth_API "Валидирует токен" "JSON/HTTPS"
            }

            geo_points_API = container "API географических координат" {
                tags ""
                technology "Python FastAPI"

                description "Реализует функциональность сервиса добавления, удаления и запроса данных о географических коодинатах"
            
                -> geo_points_API_db "Получает данные из запроса и сохраняет и получает данные о точке"
                -> auth_API "Валидирует токен" "JSON/HTTPS"
            }  

            companion_search_API = container "API поездок" {
                tags ""
                technology "Python FastAPI"

                description "Реализует функциональность сервиса по созданию маршрутов, добавления в них точек, создание поездок и добавления людей"
            
                -> companion_search_API_db "Получает данные из запроса и сохраняет данные о поездке, маршруте"
                -> auth_API "Валидирует токен" "JSON/HTTPS"
                -> users_API "Запрашивает данные пользователя" "JSON/HTTPS"
                -> geo_points_API "Запрашивает данные географической точки" "JSON/HTTPS"
            } 

        
        }

        driver -> companion_search "Создает маршрут и поездку, может добавить в нее пассажиров"
        driver -> companion_search.companion_search_API "Получает услуги связанные с созданием поезкок"

        passenger -> companion_search "Добавляется в поездку"
        passenger -> companion_search.companion_search_API "Получает услугу записи в поездку"


        
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


        container companion_search "c2" {
            include *
            autoLayout
        }

        // component companion_search.comp_search_API "c3" {
        //     include *
        //     exclude "relationship.tag==c1"
        //     autoLayout
        // }

    }

   
}