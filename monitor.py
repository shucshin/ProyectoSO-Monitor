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

def get_size(bytes, suffix="B"):
    """Convierte bytes a un formato legible (ej. 10MB, 1GB)."""
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

def get_header():
    """Genera el encabezado con información del sistema."""
    uname = platform.uname()
    return Panel(
        f"[bold blue]Sistema:[/bold blue] {uname.system} {uname.release} | "
        f"[bold blue]Nodo:[/bold blue] {uname.node} | "
        f"[bold blue]Arquitectura:[/bold blue] {uname.machine}",
        title="🖥️  Monitor del Sistema - Proyecto SO",
        border_style="green"
    )

def get_cpu_panel():
    """Genera el panel de uso de CPU."""
    cpu_percent = psutil.cpu_percent(percpu=True)
    avg_cpu = psutil.cpu_percent()
    
    table = Table(show_header=False, box=None, expand=True)
    table.add_column("Core", justify="right")
    table.add_column("Usage", justify="left")
    
    # Mostrar uso promedio
    table.add_row(
        "[bold]Total[/bold]", 
        f"[{'red' if avg_cpu > 80 else 'green'}]{'━' * int(avg_cpu / 5)} {avg_cpu}%"
    )
    table.add_row("", "") # Espaciador

    # Mostrar uso por núcleo (limitado a los primeros 8 para que quepa)
    for i, p in enumerate(cpu_percent[:8]):
        bar_length = int(p / 5)
        color = "red" if p > 80 else "yellow" if p > 50 else "green"
        bar = f"[{color}]{'━' * bar_length}[/{color}]"
        table.add_row(f"Core {i}", f"{bar} {p}%")
        
    if len(cpu_percent) > 8:
        table.add_row("...", f"+{len(cpu_percent)-8} núcleos más")

    return Panel(
        table, 
        title=f"🧠 CPU ({psutil.cpu_count()} Cores)", 
        border_style="blue"
    )

def get_memory_panel():
    """Genera el panel de Memoria RAM."""
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    table = Table(show_header=False, box=None, expand=True)
    
    # RAM
    ram_color = "red" if mem.percent > 80 else "green"
    table.add_row(
        "RAM Total", 
        f"{get_size(mem.total)}"
    )
    table.add_row(
        "RAM Uso", 
        f"[{ram_color}]{get_size(mem.used)} ({mem.percent}%)[/{ram_color}]"
    )
    table.add_row(
        "RAM Disp.", 
        f"{get_size(mem.available)}"
    )
    
    table.add_row("", "") # Espaciador
    
    # SWAP
    table.add_row("SWAP Uso", f"{get_size(swap.used)} ({swap.percent}%)")
    
    return Panel(
        table, 
        title="💾 Memoria", 
        border_style="magenta"
    )

def get_disk_network_panel():
    """Genera panel combinado de Disco y Red."""
    # Disco
    disk_usage = psutil.disk_usage('/')
    
    # Red
    net_io = psutil.net_io_counters()
    
    grid = Table.grid(expand=True)
    grid.add_column()
    grid.add_row(f"[bold]Disco (Root)[/bold]")
    grid.add_row(f"Total: {get_size(disk_usage.total)}")
    grid.add_row(f"Uso:   {get_size(disk_usage.used)} ({disk_usage.percent}%)")
    grid.add_row("")
    grid.add_row(f"[bold]Red (Total)[/bold]")
    grid.add_row(f"Enviado:  {get_size(net_io.bytes_sent)}")
    grid.add_row(f"Recibido: {get_size(net_io.bytes_recv)}")
    
    return Panel(
        grid,
        title="💿 Disco & 🌐 Red",
        border_style="cyan"
    )

def get_processes_panel():
    """Genera tabla con los procesos más pesados (CPU)."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent']):
        try:
            pinfo = proc.info
            processes.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            
    # Ordenar por CPU y tomar los top 10
    # Filtramos procesos donde cpu_percent es None
    top_processes = sorted(
        [p for p in processes if p['cpu_percent'] is not None],
        key=lambda p: p['cpu_percent'], 
        reverse=True
    )[:10]
    
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

def make_layout():
    """Define la estructura del layout."""
    layout = Layout(name="root")
    
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1)
    )
    
    layout["main"].split_row(
        Layout(name="left"),
        Layout(name="right", ratio=2)
    )
    
    layout["left"].split(
        Layout(name="cpu"),
        Layout(name="memory"),
        Layout(name="disk_net")
    )
    
    layout["right"].update(get_processes_panel())
    
    return layout

def update_layout(layout):
    """Actualiza el contenido de cada sección."""
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
    time.sleep(1)
    
    with Live(layout, refresh_per_second=1, screen=True) as live:
        while True:
            update_layout(layout)
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[red]Monitor detenido por el usuario.[/red]")

