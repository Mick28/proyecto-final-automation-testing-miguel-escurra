# Proyecto Final · Framework de Automatización de Pruebas

![CI Status](https://github.com/Mick28/proyecto-final-automation-testing-miguel-escurra/actions/workflows/ci.yml/badge.svg)

Trabajo Final Integrador del curso **Automatización QA (Talento Tech)**.
Autor: **Miguel A. Escurra**

## Propósito del proyecto

Framework de testing automatizado en Python que combina:

- **Pruebas de UI** sobre [saucedemo.com](https://www.saucedemo.com) con Selenium WebDriver y el patrón **Page Object Model**.
- **Pruebas de API** sobre [JSONPlaceholder](https://jsonplaceholder.typicode.com) con la biblioteca Requests.
- **Reportes HTML** con screenshots automáticos de los fallos y un **log** centralizado de cada ejecución.
- **Integración continua** con GitHub Actions: la suite corre sola en cada push y deja los reportes como artefactos.

Es la evolución de la [Pre-Entrega](https://github.com/Mick28/pre-entrega-automation-qa): los tests de login, catálogo y carrito pasaron de funciones auxiliares a Page Objects, se sumaron el checkout, los escenarios negativos, los datos externos (CSV/JSON), la suite de API y el pipeline de CI.

## Tecnologías utilizadas

| Herramienta | Uso |
|---|---|
| **Python 3.12** | Lenguaje principal |
| **Pytest** | Framework de testing: fixtures, markers, parametrización |
| **Selenium WebDriver 4** | Automatización del navegador (Chrome) |
| **Requests** | Pruebas de API REST |
| **jsonschema** | Validación de la estructura de las respuestas JSON |
| **pytest-html** | Reporte HTML autocontenido |
| **pytest-rerunfailures** | Reintentos ante fallos de red en las pruebas de API |
| **logging** (módulo estándar) | Log con rotación de archivos |
| **Git, GitHub y GitHub Actions** | Control de versiones e integración continua |

## Estructura del proyecto

```
proyecto-final-automation-testing-miguel-escurra/
├── .github/workflows/ci.yml      # pipeline de GitHub Actions
├── pages/                        # Page Objects (una clase por página)
│   ├── base_page.py              #   acciones genéricas + encabezado común (carrito, menú)
│   ├── login_page.py             #   login
│   ├── inventory_page.py         #   catálogo de productos
│   ├── cart_page.py              #   carrito
│   └── checkout_pages.py         #   checkout: datos, resumen y confirmación
├── tests/
│   ├── ui/                       # pruebas de interfaz (Selenium)
│   │   ├── test_login.py
│   │   ├── test_inventory.py
│   │   ├── test_cart.py
│   │   ├── test_checkout.py
│   │   └── test_demo_screenshot.py   # falla a propósito (solo con DEMO_FALLO=1)
│   └── api/                      # pruebas de API (Requests)
│       ├── conftest.py           #   fixture del cliente HTTP
│       ├── test_posts.py
│       └── test_chained_requests.py
├── utils/
│   ├── config.py                 # URLs, timeouts y rutas (configurables por variables de entorno)
│   ├── driver_factory.py         # creación del Chrome
│   ├── logger.py                 # logger centralizado con rotación
│   ├── data_loader.py            # lectura de CSV y JSON
│   ├── api_client.py             # cliente HTTP con logging
│   └── schemas.py                # JSON Schemas de las respuestas
├── datos/                        # datos de prueba externos
│   ├── login_users.csv
│   ├── sort_options.json
│   ├── cart_products.json
│   ├── checkout_data.json
│   └── api_posts.json
├── reports/                      # report.html y screenshots/ (se generan al ejecutar)
├── logs/                         # suite.log (se genera al ejecutar)
├── conftest.py                   # fixtures de UI, screenshots y personalización del reporte
├── pytest.ini                    # configuración de pytest y markers
└── requirements.txt
```

**Separación de responsabilidades:** los tests solo describen *qué* se prueba; los Page Objects saben *cómo* interactuar con cada página; los datos viven en `datos/`. Para agregar un caso nuevo alcanza, muchas veces, con sumar una fila al CSV o un objeto al JSON.

## Casos de prueba

### UI — SauceDemo (22 ejecuciones)

| ID | Test | Qué valida | Datos |
|---|---|---|---|
| TC-UI-01 | `test_login_con_distintas_credenciales` | Login exitoso y 5 escenarios negativos (usuario bloqueado, contraseña incorrecta, usuario inexistente, campos vacíos) con su mensaje de error | `login_users.csv` |
| TC-UI-02 | `test_logout_vuelve_al_login` | Cerrar sesión desde el menú lateral | — |
| TC-UI-03 | `test_acceso_directo_al_catalogo_sin_login` | Entrar a `/inventory.html` sin sesión muestra error *(negativo)* | — |
| TC-UI-04 | `test_catalogo_muestra_elementos_principales` | Título, 6 productos con nombre y precio, menú, filtro y carrito vacío | — |
| TC-UI-05 | `test_ordenar_catalogo` | Ordenamiento por nombre (A-Z, Z-A) y precio (menor/mayor) | `sort_options.json` |
| TC-UI-06 | `test_agregar_productos_al_carrito` | Contador del carrito y productos listados (1, 3 y 6 productos) | `cart_products.json` |
| TC-UI-07 | `test_quitar_producto_del_carrito` | Quitar un producto actualiza la lista y el contador | — |
| TC-UI-08 | `test_compra_completa` | Flujo completo login → carrito → checkout → confirmación, verificando subtotal y total | `checkout_data.json` |
| TC-UI-09 | `test_checkout_con_datos_incompletos` | Sin nombre, apellido o código postal el checkout no avanza *(negativo)* | `checkout_data.json` |

### API — JSONPlaceholder (12 ejecuciones)

| ID | Test | Método | Qué valida |
|---|---|---|---|
| TC-API-01 | `test_obtener_post_existente` | GET | Status 200, header JSON, tiempo de respuesta, esquema y contenido |
| TC-API-02 | `test_listar_posts_filtrados_por_usuario` | GET | Query params: 10 posts, todos del usuario pedido |
| TC-API-03 | `test_obtener_post_inexistente_devuelve_404` | GET | Status 404 y cuerpo vacío *(negativo, 3 ids)* |
| TC-API-04 | `test_crear_post` | POST | Status 201, esquema y datos devueltos *(3 posts desde `api_posts.json`)* |
| TC-API-05 | `test_actualizar_post` | PUT | Status 200 y recurso actualizado |
| TC-API-06 | `test_eliminar_post` | DELETE | Status 200 y cuerpo vacío |
| TC-API-07 | `test_crear_post_y_consultar_su_autor` | POST → GET | **Encadenamiento:** el `userId` del post creado se usa para pedir `/users/{id}` |
| TC-API-08 | `test_obtener_post_y_sus_comentarios` | GET → GET | **Encadenamiento:** el `id` del post se usa para pedir sus comentarios |

> JSONPlaceholder es una API simulada: responde como si creara o borrara recursos, pero no guarda los cambios. Por eso el encadenamiento usa datos de la respuesta (el `userId`, el `id`) en lugar de volver a pedir el post recién creado, que devolvería 404.

### Markers disponibles

| Marker | Qué agrupa |
|---|---|
| `ui` / `api` | Tipo de prueba |
| `smoke` | Pruebas críticas y rápidas |
| `negative` | Escenarios negativos |
| `demo` | Test que falla a propósito para mostrar el screenshot |

## Instalación de dependencias

Requisitos previos: **Python 3.10 o superior** y **Google Chrome**.

1. Clonar el repositorio:

   ```bash
   git clone https://github.com/Mick28/proyecto-final-automation-testing-miguel-escurra.git
   cd proyecto-final-automation-testing-miguel-escurra
   ```

2. (Recomendado) Crear y activar un entorno virtual:

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux / macOS
   source venv/bin/activate
   ```

3. Instalar las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

**Sobre ChromeDriver:** Selenium 4 lo descarga solo (Selenium Manager) según tu versión de Chrome. Si preferís usar uno propio, definí la variable `CHROMEDRIVER_PATH` con su ruta.

## Cómo ejecutar las pruebas

Todos los comandos se ejecutan desde la carpeta raíz. Las opciones del reporte ya están en `pytest.ini`, así que **`pytest` solo alcanza**.

```bash
pytest                      # toda la suite (UI + API) y genera reports/report.html
pytest tests/ui             # solo UI
pytest tests/api            # solo API
pytest -m smoke             # solo pruebas críticas
pytest -m negative          # solo escenarios negativos
pytest -k checkout          # por nombre
pytest --headless           # Chrome sin ventana
```

Modo headless con variable de entorno (equivalente a `--headless`):

```bash
# Linux / macOS
HEADLESS=true pytest
# Windows (PowerShell)
$env:HEADLESS="true"; pytest
```

**Demostración de screenshot ante un fallo** (test que falla a propósito):

```bash
# Linux / macOS
DEMO_FALLO=1 pytest -m demo
# Windows (PowerShell)
$env:DEMO_FALLO="1"; pytest -m demo
```

Otras variables de entorno disponibles (ver `utils/config.py`): `BASE_URL`, `API_BASE_URL`, `EXPLICIT_WAIT`, `API_TIMEOUT`.

## Cómo interpretar los reportes generados

### Reporte HTML — `reports/report.html`

Se abre con doble clic en cualquier navegador; es un único archivo con todo incluido.

1. **Environment:** datos de la corrida (autor, sitio UI, API, navegador, versión de Python).
2. **Summary:** total de tests y duración, con contadores de *Passed*, *Failed*, *Skipped*, *Errors* y *Reruns*. Las casillas permiten filtrar la tabla por estado.
3. **Tabla de resultados:** una fila por test con **Result** (estado), **Test** (archivo, función y caso parametrizado entre corchetes), **Tipo** (UI o API), **URL** (página en la que estaba el navegador al terminar el test) y **Duration**.
4. **Detalle de cada fila** (clic en la fila): traceback del error, logs capturados paso a paso y, si un test de UI falló, el **screenshot** del momento del fallo.

Se recomienda mirar primero el reporte (*qué* falló) y después el log (*cómo* llegó hasta ahí).

### Screenshots — `reports/screenshots/`

Cada fallo de UI guarda un PNG con el nombre del test y la fecha y hora, por ejemplo:
`test_compra_completa_comprador_argentino_20261111_185054.png`.

### Log — `logs/suite.log`

Registro cronológico de toda la ejecución (nivel INFO o superior). Cada línea tiene fecha y hora, nivel, módulo y mensaje:

```
2026-11-11 18:50:58 | INFO     | qa.conftest | ▶ INICIO  tests/ui/test_login.py::test_login_con_distintas_credenciales[usuario_vacio]
2026-11-11 18:50:58 | INFO     | qa.pages.LoginPage | Login con usuario '<vacío>'
2026-11-11 18:50:58 | INFO     | qa.pages.LoginPage | Mensaje de error mostrado: Epic sadface: Username is required
2026-11-11 18:50:58 | INFO     | qa.conftest | Resultado tests/ui/test_login.py::test_login_con_distintas_credenciales[usuario_vacio] -> PASSED (0.19 s)
```

En las pruebas de API se registra cada petición (`→ POST .../posts | body: {...}`) y su respuesta (`← status 201 | 85 ms`). Los fallos se registran con nivel ERROR e incluyen la ruta del screenshot. El archivo rota al llegar a 1 MB y conserva los 5 anteriores.

## Integración continua (GitHub Actions)

El workflow `.github/workflows/ci.yml` se ejecuta en cada **push**, en cada **pull request a `main`** y manualmente desde la pestaña *Actions*:

1. Prepara un runner Ubuntu con Python 3.12.
2. Instala las dependencias.
3. Ejecuta toda la suite en Chrome headless.
4. Sube como artefactos (aunque haya fallos) **`reporte-html`** (reporte y screenshots) y **`suite-log`** (log de ejecución), disponibles 30 días.

Para ver los resultados: pestaña **Actions** → elegir la ejecución → sección **Artifacts** al pie del resumen. El badge del principio de este README muestra el estado de la última ejecución (verde = todo pasó, rojo = algún test falló).

## Buenas prácticas aplicadas

- **Tests independientes:** cada test de UI abre su propio navegador y lo cierra en el teardown de la fixture, así una falla no afecta a los demás.
- **Esperas explícitas** (`WebDriverWait`) en lugar de `sleep`.
- **Locators centralizados** en cada Page Object: si cambia la página, se corrige en un solo lugar.
- **Datos externos** en CSV/JSON y parametrización con identificadores legibles (`[usuario_bloqueado]`, `[sin_apellido]`).
- **Reintentos** solo en las pruebas de API, que dependen de un servicio externo.
- **Configuración por variables de entorno**, sin rutas ni URLs fijas en los tests.

## Flujo de trabajo con Git

El desarrollo se hizo con ramas por funcionalidad que luego se fusionaron en `main`:

| Rama | Contenido |
|---|---|
| `feature/estructura-base` | Estructura, configuración y logger |
| `feature/ui-page-objects` | Page Objects, tests de UI, datos y screenshots |
| `feature/api-tests` | Cliente HTTP, esquemas y tests de API |
| `feature/reportes` | Personalización del reporte HTML |
| `feature/ci-github-actions` | Pipeline de CI |
| `docs/readme` | Documentación |
