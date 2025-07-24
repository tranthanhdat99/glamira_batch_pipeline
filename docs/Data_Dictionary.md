# Data Dictionary (Raw Tables)

This document describes the **raw** BigQuery tables in the `glamira_raw` dataset.

---

## `summary_raw`

| Column                     | Type     | Description                                                                                  |
|--------------------------- |--------- |--------------------------------------------------------------------------------------------- |
| `_id`                      | JSON     | Original MongoDB document ID                                                                 |
| `time_stamp`               | STRING   | Event timestamp (epoch seconds), e.g.: 1597266092                                           |
| `ip`                       | STRING   | Client IP address, e.g.: `37.170.17.183`                                                    |
| `user_agent`               | STRING   | Device/browser user agent, e.g.: `Mozilla/5.0 (...)`                                        |
| `resolution`               | STRING   | Screen resolution, e.g.: `375x667`                                                           |
| `user_id_db`               | STRING   | Authenticated user ID (blank if anonymous), e.g.: `502567`                                  |
| `device_id`                | STRING   | Device identifier, e.g.: `beb2cacb-20af-4f05-9c03-c98e54a1b71a`                             |
| `api_version`              | STRING   | API version used, e.g.: `1.0`                                                                |
| `store_id`                 | STRING   | Store identifier, e.g.: `12`                                                                 |
| `local_time`               | STRING   | Client-local timestamp, e.g.: `2020-06-04 12:21:27`                                         |
| `show_recommendation`      | BOOLEAN  |                                                                                            |
| `current_url`              | STRING   | URL of the event, e.g.: `https://...glamira-pendant.html?alloy=yellow-375`                   |
| `referrer_url`             | STRING   | Referring page URL, e.g.: `https://.../men-s-necklaces/`                                     |
| `email_address`            | STRING   | User email if signed in, e.g.: `user@example.com`                                           |
| `recommendation`           | BOOLEAN  |                                                                                            |
| `utm_source`               | STRING   |                                                                                            |
| `collection`               | STRING   | Event type (e.g. `view_product_detail`, `checkout_success`, `select_product_option_quality`) |
| `product_id`               | STRING   | Product ID for event, e.g.: `85796`                                                          |
| `viewing_product_id`       | STRING   | Alternative product ID for certain events                                                   |
| `cat_id`                   | STRING   |                                                                                            |
| `collect_id`               | STRING   | Collection ID, e.g.: `159`                                                                   |
| `option`                   | RECORD[] | Nested options; see `option` schema below                                                   |
| `order_id`                 | STRING   | Order identifier                                                                            |
| `recommendation_product_id`| STRING   | ID of recommended product                                                                    |
| `recommendation_clicked_position` | STRING |                                                                                   |
| `utm_medium`               | STRING   |                                                                                            |
| `key_search`               | STRING   |                                                                                            |
| `price`                    | STRING   | Price value (product or order)                                                             |
| `currency`                 | STRING   | Currency code for `price`                                                                  |
| `recommendation_product_position` | INTEGER |                                                                              |
| `is_paypal`                | BOOLEAN  | Indicates PayPal payment                                                                   |
| `cart_products`            | RECORD[] | Array of cart items; see `cart_products` schema below                                       |

### Nested: `option` (REPEATED RECORD)
| Field           | Type   | Description                        |
|---------------- |------- |----------------------------------- |
| `option_label`  | STRING | e.g. `alloy`, `diamond`           |
| `option_id`     | STRING |                                    |
| `value_label`   | STRING | e.g. `red-585`                    |
| `value_id`      | STRING |                                    |
| `quality`       | STRING | e.g. `AAA`                        |
| `quality_label` | STRING |                                    |
| `alloy`         | STRING |                                    |
| `diamond`       | STRING |                                    |
| `shapediamond`  | STRING |                                    |
| `stone`         | STRING |                                    |
| `pearlcolor`    | STRING |                                    |
| `finish`        | STRING |                                    |
| `price`         | STRING |                                    |
| `category_id`   | STRING |                                    |
| `kollektion`    | STRING |                                    |
| `kollektion_id` | STRING |                                    |

### Nested: `cart_products` (REPEATED RECORD)
| Field       | Type     | Description                  |
|------------ |--------- |----------------------------- |
| `product_id`| STRING   | Product ID                   |
| `price`     | STRING   | Price per item               |
| `currency`  | STRING   | Currency code                |
| `amount`    | INTEGER  | Quantity                     |
| `option`    | RECORD[] | Nested `option` records      |

---

## `ip_locations_raw`

| Column          | Type   | Description                                             |
|---------------- |------- |-------------------------------------------------------- |
| `ip`            | STRING | Client IP address                                       |
| `country_short` | STRING | ISO 3166-1 alpha-2 country code                         |
| `country_long`  | STRING | Full country name                                       |
| `region`        | STRING | Region or state                                        |
| `city`          | STRING | City name                                              |
| `timezone`      | STRING | Timezone (e.g. `Europe/Berlin`)                         |

*Columns with blank descriptions indicate fields needing further clarification.*
