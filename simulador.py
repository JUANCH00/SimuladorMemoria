import math
from tabulate import tabulate

# Clase que representa el proceso en el sistema
class Process:
    def __init__(self, pid, size, page_size):
        self.pid = pid  # Identificador unico de cada proceso
        self.size = size  # Tamaño del proceso en KB
        self.page_size = page_size
        # Calcular el número de páginas necesarias (redondear hacia arriba)
        self.num_pages = math.ceil(size / page_size)
        self.page_table = {}  # Tabla de páginas
        self.state = "Ready"

    # Asigna marcos fisicos a las paginas del proceso
    def allocate_memory(self, available_frames):
        allocated_frames = []
        for page in range(self.num_pages):
            if available_frames:
                frame = available_frames.pop(0)
                self.page_table[page] = frame
                allocated_frames.append(frame)
            else:
                raise Exception("No hay suficientes marcos disponibles")
        return allocated_frames

    # Convertidor de direccion logica a fisica
    def logical_to_physical(self, logical_address):
        page = logical_address // self.page_size
        offset = logical_address % self.page_size

        if page in self.page_table:
            frame = self.page_table[page]
            physical_address = (frame * self.page_size) + offset
            return page, offset, frame, physical_address
        else:
            raise Exception("Página no encontrada en la tabla de páginas")

    # Cambiar el estado del proceso
    def change_state(self, new_state):
        self.state = new_state
        print(f"Proceso {self.pid} cambió al estado: {new_state}")


# Clase que gestiona la memoria y los procesos
class MemoryManager:
    def __init__(self, total_memory, page_size):
        self.total_memory = total_memory
        self.page_size = page_size
        self.num_frames = total_memory // page_size
        self.available_frames = list(range(self.num_frames))
        self.processes = {}  # Diccionario de procesos por PID
        self.memory_map = [None] * self.num_frames  # None = marco libre

    # Crea un nuevo proceso y asigna memoria
    def create_process(self, pid, size):
        if pid in self.processes:
            print(f"Error: Ya existe un proceso con el mismo PID {pid}")
            return False

        process = Process(pid, size, self.page_size)

        if process.num_pages > len(self.available_frames):
            print(f"Error: No hay suficientes marcos para el proceso {pid}")
            return False

        try:
            allocated_frames = process.allocate_memory(self.available_frames)
            self.processes[pid] = process

            # Actualizar el mapa de memoria
            for frame in allocated_frames:
                self.memory_map[frame] = pid

            process.change_state("Ready")
            print(f"Proceso {pid} creado y memoria asignada")
            return True
        except Exception as e:
            print(f"Error al asignar memoria: {e}")
            return False

    # Termina un proceso y libera su memoria
    def terminate_process(self, pid):
        if pid not in self.processes:
            print(f"Error: No existe el proceso {pid}")
            return False

        process = self.processes[pid]
        process.change_state("Terminated")

        # Liberar marcos de memoria
        for page, frame in process.page_table.items():
            self.available_frames.append(frame)
            self.memory_map[frame] = None

        # Ordenar los marcos disponibles
        self.available_frames.sort()

        # Eliminar el proceso
        del self.processes[pid]
        print(f"Proceso {pid} terminado y memoria liberada")
        return True

    # Traduce una dirección lógica a física y muestra la ubicación en el marco
    def translate_address(self, pid, logical_address):
        if pid not in self.processes:
            print(f"Error: No existe el proceso {pid}")
            return False

        process = self.processes[pid]

        if logical_address >= process.size:
            print(
                f"Error: Dirección lógica {logical_address} fuera del espacio del proceso"
            )
            return False

        try:
            page, offset, frame, physical_address = process.logical_to_physical(
                logical_address
            )

            print("\n--- Traducción de Dirección ---")
            print(f"Proceso: {pid}")
            print(f"Dirección lógica: {logical_address}")
            print(f"Tamaño de página: {self.page_size}")
            print(f"Cálculo:")
            print(f"  Página = {logical_address} // {self.page_size} = {page}")
            print(f"  Desplazamiento = {logical_address} % {self.page_size} = {offset}")
            print(f"Resultado:")
            print(f"  Marco físico: {frame}")
            print(
                f"  Dirección física: ({frame} * {self.page_size}) + {offset} = {physical_address}"
            )

            # Mostrar representación visual del marco
            self.show_frame_content(frame, offset, pid)

            return physical_address
        except Exception as e:
            print(f"Error en la traducción: {e}")
            return False

    # Muestra una representación visual del contenido del marco
    def show_frame_content(self, frame, offset, pid):
        print(f"\n--- Representación del Marco {frame} (Proceso {pid}) ---")

        # Crear una representación visual del marco
        marco_visual = []
        for i in range(self.page_size):
            if i == offset:
                marco_visual.append(f"[{i}: DIR_ACTUAL]")  # Marcar la dirección actual
            else:
                marco_visual.append(f"[{i}]")

        # Mostrar el marco en filas para mejor visualización
        print("Contenido del marco (desplazamientos):")
        for i in range(0, self.page_size, 8):  # Mostrar 8 elementos por fila
            fila = marco_visual[i : min(i + 8, self.page_size)]
            print(" ".join(fila))

        print(
            f"\nLa dirección se encuentra en el desplazamiento {offset} del marco {frame}"
        )

    # Muestra la tabla de páginas de un proceso
    def show_page_table(self, pid):
        if pid not in self.processes:
            print(f"Error: No existe el proceso {pid}")
            return False

        process = self.processes[pid]

        print(f"\n--- Tabla de Páginas del Proceso {pid} ---")
        table_data = []
        for page, frame in process.page_table.items():
            table_data.append([f"Página {page}", f"Marco {frame}"])

        print(
            tabulate(
                table_data, headers=["Página Lógica", "Marco Físico"], tablefmt="grid"
            )
        )

        # Mostrar información adicional
        print(f"\nInformación del proceso {pid}:")
        print(f"  Tamaño: {process.size} KB")
        print(f"  Número de páginas: {process.num_pages}")
        print(f"  Estado: {process.state}")

    # Muestra el mapa de memoria física
    def show_memory_map(self):
        print("\n--- Mapa de Memoria Física ---")
        print(f"Total de marcos: {self.num_frames}")
        print(f"Tamaño de página: {self.page_size} bytes")
        print(f"Memoria total: {self.total_memory} bytes")

        table_data = []
        for i in range(self.num_frames):
            status = (
                "Libre"
                if self.memory_map[i] is None
                else f"Proceso {self.memory_map[i]}"
            )
            table_data.append([f"Marco {i}", status])

        print(tabulate(table_data, headers=["Marco", "Estado"], tablefmt="grid"))

        # Mostrar estadísticas
        marcos_ocupados = sum(1 for marco in self.memory_map if marco is not None)
        print(f"\nEstadísticas:")
        print(f"  Marcos ocupados: {marcos_ocupados}/{self.num_frames}")
        print(f"  Marcos libres: {self.num_frames - marcos_ocupados}/{self.num_frames}")

    # Muestra los marcos disponibles
    def show_available_frames(self):
        print(f"\nMarcos disponibles: {len(self.available_frames)}/{self.num_frames}")
        print(f"Lista de marcos disponibles: {self.available_frames}")

        # Mostrar información de la memoria
        print(f"\nInformación de la memoria:")
        print(f"  Tamaño total: {self.total_memory} KB")
        print(f"  Tamaño de página: {self.page_size} KB")
        print(f"  Número total de marcos: {self.num_frames}")

#Manejar la creación de un nuevo proceso
def handle_create_process(memory_manager):
    pid = input("Ingrese el PID del proceso: ")
    try:
        size = int(input("Ingrese el tamaño del proceso (KB): "))
        if memory_manager.create_process(pid, size):
            print(f"Proceso {pid} creado exitosamente")
    except ValueError:
        print("Error: El tamaño debe ser un número entero")

#Manejar la traducción de direcciones lógicas a físicas
def handle_translate_address(memory_manager):
    pid = input("Ingrese el PID del proceso: ")
    try:
        logical_address = int(input("Ingrese la dirección lógica: "))
        result = memory_manager.translate_address(pid, logical_address)
        if result is not False:
            print(f"Traducción completada. Dirección física: {result}")
    except ValueError:
        print("Error: La dirección debe ser un número entero")

def main():
    # Configuración inicial
    total_memory = 64  # KB
    page_size = 4  # KB
    memory_manager = MemoryManager(total_memory, page_size)

    while True:
        print("\n" + "=" * 50)
        print("SIMULADOR DE ADMINISTRADOR DE MEMORIA")
        print("=" * 50)
        print("1. Mostrar información de memoria")
        print("2. Crear proceso")
        print("3. Terminar proceso")
        print("4. Mostrar tabla de páginas de un proceso")
        print("5. Traducir dirección lógica a física")
        print("6. Mostrar mapa de memoria")
        print("7. Salir")

        try:
            choice = input("\nSeleccione una opción: ")

            match choice:
                case "1":
                    memory_manager.show_available_frames()

                case "2":
                    handle_create_process(memory_manager)

                case "3":
                    pid = input("Ingrese el PID del proceso a terminar: ")
                    memory_manager.terminate_process(pid)

                case "4":
                    pid = input("Ingrese el PID del proceso: ")
                    memory_manager.show_page_table(pid)

                case "5":
                    handle_translate_address(memory_manager)

                case "6":
                    memory_manager.show_memory_map()

                case "7":
                    print("Saliendo del simulador...")
                    break

                case _:
                    print("Opción no válida. Intente de nuevo.")

        except KeyboardInterrupt:
            print("\n\nInterrupción detectada. Saliendo del simulador...")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
