workspace {
    model {
        user = person "Пользователь" "Физическое лицо, использующее приложение для планирования поездок."
        
        trip_system = softwareSystem "Trip Management System" {
            description "Система для управления пользователями, маршрутами и поездками с микросервисной архитектурой."
            
            // Контейнеры уровня C2
            client = container "Клиентское приложение" {
                description "Web/Mobile приложение для взаимодействия с системой"
                technology "React, TypeScript"
            }
            
            api_gateway = container "API Gateway" {
                description "Единая точка входа с маршрутизацией и аутентификацией"
                technology "NGINX, порт 443"
            }
            
            auth_service = container "Auth Service" {
                description "Микросервис аутентификации и авторизации"
                technology "Python FastAPI, порт 8000\nJWT, OAuth2"
            }
            
            user_service = container "User Service" {
                description "Микросервис управления пользователями"
                technology "Python FastAPI, порт 8001"
            }
            
            route_service = container "Route Service" {
                description "Микросервис управления маршрутами"
                technology "Python FastAPI, порт 8002"
            }
            
            route_point_service = container "Route Points Service" {
                description "Микросервис управления точками маршрута"
                technology "Python FastAPI, порт 8003"
            }
            
            trip_service = container "Trip Service" {
                description "Микросервис управления поездками"
                technology "Python FastAPI, порт 8004"
            }
            
            auth_db = container "Auth PostgreSQL" {
                description "База данных аутентификации"
                technology "PostgreSQL 15, порт 5432"
            }
            
            user_db = container "User PostgreSQL" {
                description "База данных пользователей"
                technology "PostgreSQL 15, порт 5433"
            }
            
            route_db = container "Route PostgreSQL" {
                description "База данных маршрутов"
                technology "PostgreSQL 15, порт 5434"
            }
            
            route_point_db = container "Route Points PostgreSQL" {
                description "База данных точек маршрута"
                technology "PostgreSQL 15, порт 5435"
            }
            
            trip_db = container "Trip PostgreSQL" {
                description "База данных поездок"
                technology "PostgreSQL 15, порт 5436"
            }
            
            kafka = container "Kafka Broker" {
                description "Брокер событий для нотификаций"
                technology "Apache Kafka, порт 9092"
            }

            // Связи
            user -> client "Взаимодействие" "HTTPS"
            client -> api_gateway "API запросы" "HTTPS"
            
            api_gateway -> auth_service "Аутентификация" "HTTP /auth/*"
            api_gateway -> user_service "Запросы пользователей" "HTTP /users/*"
            api_gateway -> route_service "Управление маршрутами" "HTTP /routes/*"
            api_gateway -> route_point_service "Управление точками" "HTTP /points/*"
            api_gateway -> trip_service "Управление поездками" "HTTP /trips/*"
            
            auth_service -> auth_db "Хранение учетных данных" "JDBC"
            user_service -> user_db "Хранение профилей" "JDBC"
            route_service -> route_db "Хранение маршрутов" "JDBC"
            route_point_service -> route_point_db "Хранение точек" "JDBC"
            trip_service -> trip_db "Хранение поездок" "JDBC"
            
            trip_service -> kafka "Публикация событий (подключение пользователей)" "Kafka Protocol"
            kafka -> user_service "Нотификации пользователям" "WebSocket"
        }
    }

    views {
        // Контекстная диаграмма (C1)
        systemContext trip_system {
            include *
            autolayout
            title "C1: Контекстная диаграмма системы"
        }
        
        // Диаграмма контейнеров (C2)
        container trip_system {
            // perspective "C2"
            include user client api_gateway auth_service user_service route_service route_point_service trip_service auth_db user_db route_db route_point_db trip_db kafka
            autolayout
            title "C2: Диаграмма контейнеров"
        }
    }
}