workspace {
    name "Travel companion search service"
    !identifiers hierarchical

    model {
        user = person "Пользователь" "создает маршрут/поедку или присоединяется к поездке" "c1,c2"

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
                technology "NoSQL Database"

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

                database_controller = component "Контроллер обращения к базе"{
                    
                    technology "Python"
                
                    description "Управляет подключением к базе данных и генерацией запросов"
                    -> auth_API_db "читает и сохраняет" "SQL/TCP"
                }
                
                auth_controller = component "Контроллер аутентификации"{
                    
                    technology "Python FastAPI"
                
                    description "Возвращает токен при аутентификации, сохраняет шифрованный пароль в базу при регистрации"

                    -> database_controller "AUTH_INFO"
                }

            }

            users_API = container "API пользователей" {
                tags ""
                technology "Python FastAPI"

                description "Реализует функциональность сервиса записи и получения информации о пользователях"
            
                -> users_API_db "Получает данные из запроса и сохраняет и получает данные о пользователе" "SQL/TCP"
                -> auth_API "Валидирует токен" "JSON/HTTPS"

                database_controller = component "Контроллер обращения к базе" {
                    
                    technology "Python"
                
                    description "Управляет подключением к базе данных и генерацией запросов"
                    -> users_API_db "читает и сохраняет" "SQL/TCP"
                }

                auth_controller = component "Контроллер авторизации" {
                    
                    technology "Python"
                
                    description "Ходит в сервис авторизации за проверкой токена"
                    -> auth_API "Валидирует токен"
                }
                
                users_controller = component "Контроллер пользователей"{
                    
                    technology "Python FastAPI"
                
                    description "CRUD операции с пользователями"

                    -> database_controller "USER_INFO"
                    -> auth_API "Регистрирует/валидирует токен" "JSON/HTTPS"
                    -> auth_controller "token" 
                }
            }

            geo_points_API = container "API географических координат" {
                tags ""
                technology "Python FastAPI"

                description "Реализует функциональность сервиса добавления, удаления и запроса данных о географических коодинатах"
            
                -> geo_points_API_db "Получает данные из запроса и сохраняет и получает данные о точке"
                -> auth_API "Валидирует токен" "JSON/HTTPS"

                database_controller = component "Контроллер обращения к базе" {
                    
                    technology "Python"
                
                    description "Управляет подключением к базе данных и генерацией запросов"
                    -> users_API_db "читает и сохраняет" 
                }

                auth_controller = component "Контроллер авторизации" {
                    
                    technology "Python"
                
                    description "Ходит в сервис авторизации за проверкой токена"
                    -> auth_API "Валидирует токен""JSON/HTTPS"
                }
                
                geopoints_controller = component "Контроллер географических точек"{
                    
                    technology "Python FastAPI"
                
                    description "CRUD операции с географическими координатами"

                    -> auth_controller "token" 
                    -> database_controller "GEO_POINT_INFO"
                }
            }  

            companion_search_API = container "API поездок" {
                tags ""
                technology "Python FastAPI"

                description "Реализует функциональность сервиса по созданию маршрутов, добавления в них точек, создание поездок и добавления людей"
            
                -> companion_search_API_db "Получает данные из запроса и сохраняет данные о поездке, маршруте"
                -> auth_API "Валидирует токен" "JSON/HTTPS"
                -> users_API "Запрашивает данные пользователя" "JSON/HTTPS"
                -> geo_points_API "Запрашивает данные географической точки" "JSON/HTTPS"

                database_controller = component "Контроллер обращения к базе" {
                    
                    technology "Python"
                
                    description "Управляет подключением к базе данных и генерацией запросов"
                    -> companion_search_API_db "читает и сохраняет" 
                }

                auth_controller = component "Контроллер авторизации" {
                    
                    technology "Python"
                
                    description "Ходит в сервис авторизации за проверкой токена"
                    -> auth_API "Валидирует токен""JSON/HTTPS"
                }
                
                routes_controller = component "Контроллер маршрутов"{
                    
                    technology "Python FastAPI"
                
                    description "CRUD операции с маршрутами"

                    -> database_controller "ROUTE_INFO"
                    -> auth_controller "Регистрирует/валидирует токен" "JSON/HTTPS"
                    -> geo_points_API "Валидирует точки и запрашивает о них информацию" "JSON/HTTPS"
                }

                trips_controller = component "Контроллер поездок"{
                    
                    technology "Python FastAPI"
                
                    description "CRUD операции с поездками"

                    -> database_controller "TRIPS_INFO"
                    -> auth_controller "Регистрирует/валидирует токен" "JSON/HTTPS"
                    -> users_API "Валидирует пользователей и запрашивает о них информацию" "JSON/HTTPS"
                }
            }

        
        }

        deploymentEnvironment "Docker" {
            deploymentNode "Docker Host" {
                technology "Docker Engine"
                description "Основной хост приложений"

                deploymentNode "Database Node" {
                    technology "Postgres 13-alpine"
                    containerInstance companion_search.auth_API_db {
                        
                    }
                }

                deploymentNode "Services" {
                    infrastructureNode "app-network" {
                        technology "Docker Network"
                    }

                    deploymentNode "auth_service" {
                        containerInstance companion_search.auth_API {
                            url "http://127.0.0.1:8000/docs#"
                        }
                    }

                    deploymentNode "geo_points_service" {
                        containerInstance companion_search.geo_points_API {
                            url "http://127.0.0.1:8001/docs#"
                        }
                    }

                    deploymentNode "user_service" {
                        containerInstance companion_search.users_API {
                            url "http://127.0.0.1:8003/docs#"
                        }
                    }

                    deploymentNode "trips_service" {
                        containerInstance companion_search.companion_search_API {
                            url "http://127.0.0.1:8002/docs#"
                        }
                    }

                    companion_search.auth_API -> companion_search.auth_API_db "SQL"
                    companion_search.geo_points_API -> companion_search.auth_API "HTTP"
                    companion_search.users_API -> companion_search.auth_API "HTTP"
                    companion_search.companion_search_API -> companion_search.auth_API "HTTP"
                    companion_search.companion_search_API -> companion_search.geo_points_API "HTTP"
                    companion_search.companion_search_API -> companion_search.users_API "HTTP"
                }
            }
        }
        


        user -> companion_search "пользуется приложением для подбора попутчиков"
        user -> companion_search.companion_search_API "Получает услугу записи в поездку"
        user -> companion_search.users_API "Регистрируется, получает список пользователей"
        user -> companion_search.auth_API "Получает токен"
        
        user -> companion_search.companion_search_API.trips_controller "Делает запросы к апи" "JSON/HTTPS"
        user -> companion_search.companion_search_API.routes_controller "Делает запросы к апи" "JSON/HTTPS"

        user -> companion_search.geo_points_API.geopoints_controller "Делает запросы к апи" "JSON/HTTPS"
        
        user -> companion_search.users_API.users_controller "Делает запросы к апи" "JSON/HTTPS"

        user -> companion_search.auth_API.auth_controller "Делает запросы к апи" "JSON/HTTPS"

        
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

        component companion_search.auth_API "c3_auth" {
            include *

            autoLayout
        }

        component companion_search.users_API "c3_users" {
            include *

            autoLayout
        }

        component companion_search.geo_points_API "c3_geo_points" {
            include *

            autoLayout
        }

        component companion_search.companion_search_API "c3_companion_search" {
            include *

            autoLayout
        }

        deployment * "Docker"{
            include *
            autoLayout
        }

        dynamic companion_search "CreateTrip" "Создание поездки" {
            autoLayout

            user -> companion_search.auth_API "отправляет логин и пароль и получает токен"
            user -> companion_search.companion_search_API "Отправляет информацию о поездке"
            companion_search.companion_search_API -> companion_search.auth_API "валидирует токен"
            companion_search.companion_search_API -> companion_search.users_API "валидирует добавляемых пользователей"
            companion_search.users_API -> companion_search.auth_API "валидирует токен"
            companion_search.companion_search_API -> companion_search.companion_search_API_db "Сохраняет данные"
            companion_search.companion_search_API -> user "Возвращает данные о созданной поездке"
        }

    }

   
}