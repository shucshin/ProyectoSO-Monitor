# Monitor de Sistema Básico (Proyecto SO)

Este proyecto implementa un monitor de recursos del sistema en tiempo real utilizando Python. Fue desarrollado como parte de la materia de Sistemas Operativos para visualizar métricas críticas como uso de CPU, memoria, disco, red y procesos.

## 📋 Características

- **Interfaz de Línea de Comandos (CLI)**: Visualización moderna y limpia en la terminal.
- **Tiempo Real**: Actualización dinámica de métricas (CPU y RAM).
- **Métricas Monitoreadas**:
  - **CPU**: Uso total y por núcleo (visualización de barras).
  - **Memoria**: RAM total, usada y disponible; uso de SWAP.
  - **Disco**: Espacio total y usado de la partición raíz.
  - **Red**: Bytes enviados y recibidos (acumulado).
  - **Procesos**: Tabla "Top 10" de procesos que más consumen CPU.

## 🛠️ Tecnologías Utilizadas

El monitor utiliza las siguientes librerías para su funcionamiento:

1.  **`psutil` (Process and System Utilities)**: 
    - Es la librería central del proyecto. Se utiliza para interactuar con las APIs del sistema operativo (independientemente de si es Linux, Windows o macOS). 
    - Permite obtener estadísticas de uso de CPU (`cpu_percent`), memoria (`virtual_memory`), discos (`disk_usage`), red (`net_io_counters`) y iterar sobre los procesos en ejecución (`process_iter`).
    
2.  **`rich`**: 
    - Utilizada para la interfaz gráfica en la terminal (TUI).
    - Facilita la creación de tablas, paneles con bordes, colores y, lo más importante, el componente `Live` que permite refrescar la pantalla sin parpadeos molestos, logrando una experiencia fluida.

## 🚀 Guía de Instalación y Uso

### Prerrequisitos
- Python 3.7 o superior.

### Pasos de Instalación

1. **Clonar o descargar este repositorio** en tu máquina local.

2. **Crear un entorno virtual** (recomendado para no afectar tu instalación global de Python):
   ```bash
   # En macOS/Linux
   python3 -m venv venv
   source venv/bin/activate

   # En Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Instalar las dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

### Ejecución

Una vez instaladas las dependencias, ejecuta el script principal:

```bash
python monitor.py
```

Para salir del monitor, presiona `Ctrl + C`.

## 📷 Capturas / Funcionamiento

Al ejecutar el programa, verás un dashboard dividido en paneles:
- **Izquierda**: Métricas de hardware (CPU, RAM, Disco/Red).
- **Derecha**: Lista de procesos activos ordenados por consumo de CPU.

---
*Desarrollado para la materia de Sistemas Operativos - 2026-1*

