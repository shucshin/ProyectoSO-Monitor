import time
import psutil
import platform
from datetime import datetime
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.console import Console
from rich.text import Text
from rich import box

# ==========================================
# Funciones de Ayuda y Formateo
# ==========================================

def get_size(bytes, suffix="B"):
    """
    Convierte un valor numérico en bytes a un formato legible por humanos (ej. 10MB, 1GB).
    Recorre las unidades iterativamente dividiendo por 1024.
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

# ==========================================
# Generadores de Paneles (Vistas)
# ==========================================

def get_header():
    """
    Genera el encabezado superior con información estática del Host.
    Utiliza platform.uname() para obtener detalles del kernel y arquitectura.
    """
    uname = platform.uname()
    return Panel(
        f"[bold blue]Sistema:[/bold blue] {uname.system} {uname.release} | "
        f"[bold blue]Nodo:[/bold blue] {uname.node} | "
        f"[bold blue]Arquitectura:[/bold blue] {uname.machine}",
        title="🖥️  Monitor del Sistema - Proyecto SO",
        border_style="green"
    )

def get_cpu_panel():
    """
    Genera el panel de uso de CPU.
    - psutil.cpu_percent(percpu=True): Devuelve una lista con el % de uso de cada núcleo.
    - Renderiza una barra de progreso visual basada en el porcentaje.
    """
    # percpu=True nos da una lista, ej: [10.5, 20.0, 5.0, ...]
    cpu_percent = psutil.cpu_percent(percpu=True)
    # Promedio global de todos los núcleos
    avg_cpu = psutil.cpu_percent()
    
    table = Table(show_header=False, box=None, expand=True)
    table.add_column("Core", justify="right")
    table.add_column("Usage", justify="left")
    
    # Fila de resumen total
    table.add_row(
        "[bold]Total[/bold]", 
        f"[{'red' if avg_cpu > 80 else 'green'}]{'━' * int(avg_cpu / 5)} {avg_cpu}%"
    )
    table.add_row("", "") # Espaciador visual

    # Iteramos sobre los primeros 8 núcleos para mostrar barras individuales
    for i, p in enumerate(cpu_percent[:8]):
        # Calculamos longitud de la barra (cada '━' representa 5%)
        bar_length = int(p / 5)
        # Cambio de color dinámico según carga: Verde < 50% < Amarillo < 80% < Rojo
        color = "red" if p > 80 else "yellow" if p > 50 else "green"
        bar = f"[{color}]{'━' * bar_length}[/{color}]"
        table.add_row(f"Core {i}", f"{bar} {p}%")
        
    # Si hay más de 8 núcleos, indicamos que están ocultos por espacio
    if len(cpu_percent) > 8:
        table.add_row("...", f"+{len(cpu_percent)-8} núcleos más")

    return Panel(
        table, 
        title=f"🧠 CPU ({psutil.cpu_count()} Cores)", 
        border_style="blue"
    )

def get_memory_panel():
    """
    Genera el panel de Memoria RAM y SWAP.
    - virtual_memory(): Estadísticas de la memoria física.
    - swap_memory(): Estadísticas de la memoria de intercambio (disco).
    """
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    table = Table(show_header=False, box=None, expand=True)
    
    # Alerta visual si la RAM supera el 80%
    ram_color = "red" if mem.percent > 80 else "green"
    
    table.add_row("RAM Total", f"{get_size(mem.total)}")
    table.add_row(
        "RAM Uso", 
        f"[{ram_color}]{get_size(mem.used)} ({mem.percent}%)[/{ram_color}]"
    )
    # 'Available' es más preciso que 'Free' porque incluye memoria en caché liberable
    table.add_row("RAM Disp.", f"{get_size(mem.available)}")
    
    table.add_row("", "") # Espaciador
    
    table.add_row("SWAP Uso", f"{get_size(swap.used)} ({swap.percent}%)")
    
    return Panel(
        table, 
        title="💾 Memoria", 
        border_style="magenta"
    )

def get_disk_network_panel():
    """
    Genera panel combinado de Disco y Red.
    - disk_usage('/'): Espacio en la partición raíz.
    - net_io_counters(): Estadísticas globales de I/O de red.
    """
    disk_usage = psutil.disk_usage('/')
    net_io = psutil.net_io_counters()
    
    grid = Table.grid(expand=True)
    grid.add_column()
    
    grid.add_row(f"[bold]Disco (Root)[/bold]")
    grid.add_row(f"Total: {get_size(disk_usage.total)}")
    grid.add_row(f"Uso:   {get_size(disk_usage.used)} ({disk_usage.percent}%)")
    
    grid.add_row("") # Espaciador
    
    grid.add_row(f"[bold]Red (Total)[/bold]")
    # Bytes enviados/recibidos desde el arranque del sistema
    grid.add_row(f"Enviado:  {get_size(net_io.bytes_sent)}")
    grid.add_row(f"Recibido: {get_size(net_io.bytes_recv)}")
    
    return Panel(
        grid,
        title="💿 Disco & 🌐 Red",
        border_style="cyan"
    )

def get_processes_panel():
    """
    Genera tabla con los procesos más pesados ordenados por CPU.
    Recupera PID, nombre, usuario y %CPU.
    """
    processes = []
    # Iteramos sobre todos los PIDs activos.
    # Usamos ['name', 'cpu_percent'] en el constructor para optimizar la llamada al sistema.
    for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent']):
        try:
            pinfo = proc.info
            processes.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # NoSuchProcess: El proceso murió mientras iterábamos.
            # AccessDenied: No tenemos permisos (ej. procesos del sistema/root).
            pass
            
    # Ordenamos la lista de diccionarios por la clave 'cpu_percent'.
    # IMPORTANTE: Filtramos valores None que pueden causar errores en la comparación.
    top_processes = sorted(
        [p for p in processes if p['cpu_percent'] is not None],
        key=lambda p: p['cpu_percent'], 
        reverse=True
    )
    
    # Construcción de la tabla visual
    table = Table(expand=True, box=box.SIMPLE)
    table.add_column("PID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Nombre", style="magenta")
    table.add_column("User", style="green")
    table.add_column("CPU %", justify="right", style="yellow")
    
    for p in top_processes:
        table.add_row(
            str(p['pid']),
            str(p['name']),
            str(p['username']),
            f"{p['cpu_percent']:.1f}"
        )
        
    return Panel(
        table,
        title="⚙️  Top Procesos (CPU)",
        border_style="white"
    )

# ==========================================
# Gestión del Layout (Interfaz)
# ==========================================

def make_layout():
    """
    Define la estructura de cuadrícula de la interfaz.
    Divide la pantalla en Header (arriba) y Cuerpo (abajo),
    y luego subdivide el cuerpo en columnas y filas.
    """
    layout = Layout(name="root")
    
    # División principal: Header (3 líneas) vs Resto
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1)
    )
    
    # El cuerpo principal se divide en dos columnas
    layout["main"].split_row(
        Layout(name="left"),         # Columna izquierda (Hardware)
        Layout(name="right", ratio=2) # Columna derecha (Procesos) - Más ancha
    )
    
    # La columna izquierda se divide en 3 filas
    layout["left"].split(
        Layout(name="cpu"),
        Layout(name="memory"),
        Layout(name="disk_net")
    )
    
    return layout

def update_layout(layout):
    """
    Función de refresco. Llama a los generadores de paneles 
    y actualiza el objeto layout existente.
    """
    layout["header"].update(get_header())
    layout["cpu"].update(get_cpu_panel())
    layout["memory"].update(get_memory_panel())
    layout["disk_net"].update(get_disk_network_panel())
    layout["right"].update(get_processes_panel())

def main():
    console = Console()
    layout = make_layout()
    
    console.clear()
    console.print("[bold green]Iniciando Monitor de Sistema...[/bold green]")
    time.sleep(1) # Breve pausa para lectura
    
    # Live context manager: Se encarga de redibujar la pantalla sin parpadeos
    with Live(layout, refresh_per_second=1, screen=True) as live:
        while True:
            update_layout(layout)
            time.sleep(1) # Intervalo de actualización (1 segundo)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Captura Ctrl+C para salir limpiamente sin mostrar errores feos
        print("\n[red]Monitor detenido por el usuario.[/red]")
