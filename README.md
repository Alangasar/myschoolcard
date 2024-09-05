# Моя школьная карта
Неофициальный плагин для получения баланса школьных карт myschoolcard.ru в Home Assistant.

# Установка

## Вариант 1 - HACS
1. Перейти в HACS -> Интеграции -> Пользовательские репозитории. Добавить репозиторий https://github.com/Alangasar/myschoolcard в HACS.
2. Перезагрузить HA. 
3. Добавить интеграцию "My School Card" на странице Настройки -> Устройства и службы.

## Вариант 2 - Ручная установка
1. Cкопировать каталог myschoolcard в каталог custom_components.
2. Перезагрузить HA.
3. Добавить интеграцию "My School Card" на странице Настройки -> Устройства и службы.

## Примеры автоматизаций
### Изменение баланса карты
```yaml
alias: Баланс школьной карты
trigger:
  - platform: state
    entity_id:
      - sensor.school_card
    attribute: balance
condition: []
action:
  - data:
      message: >-
        Баланс школьной карты {% if trigger is defined and
        trigger.from_state is defined -%} {% set diff = trigger.to_state.state |
        float - trigger.from_state.state | float -%}
         {% if diff > 0 %}увеличился{%- else -%}уменьшился{% endif %} на <b>{{ diff|abs|round(2)}}</b> руб. и составил <b>{{ trigger.to_state.state }}</b> руб.
        {%- else -%}
          <code>{{ states('sensor.school_card') }}</code> руб.
        {% endif %}
    action: notify.tg_bot
```
### Ежедневное вечернее уведомление о низком балансе
```yaml
alias: Ежедневный баланс
trigger:
  - platform: time
    at: "21:00:00"
condition: []
action:
  - choose:
      - conditions:
          - condition: state
            entity_id: binary_sensor.workday_tomorrow
            state: "on"
          - condition: numeric_state
            entity_id: sensor.school_card
            below: 100
        sequence:
          - data:
              message: >-
                Низкий баланс школьной карты: {{states('sensor.school_card')}}
            action: notify.tg_bot
```
### Напоминание в последний день месяца о пополнении баланса для продления проездного
```yaml
alias: Последний день месяца. Баланс школьной карты
trigger:
  - platform: time
    at: "21:15:00"
condition:
  - condition: state
    entity_id: binary_sensor.last_month_day
    state: "on"
action:
  - data:
      message: >-
        На карте школьной карте - {{ states('sensor.school_card')}} руб., их{%- set tarif =
        state_attr("sensor.school_card", "transport_tarif") | replace("RUB", "") |
        float(0) -%} {% if states('sensor.school_card') | float - tarif > 0 %}
        хватает {% else %}  не хватает {% endif %}денег на продление проездного.
    action: notify.tg_bot
```