class Wagon:
    """
    Clase que representa un vagón de tren, gestionando dimensiones, velocidad, pasajeros
    y matrices para el control de la distribución y visualización.
    """
    
    wagon_counter = 0

    def __init__(self, wagon_length_m, wagon_width_m, speed, passenger_per_meter):
        """Inicializa una instancia de Wagon."""
        self.wagon_length_m = wagon_length_m
        self.wagon_width_m = wagon_width_m
        self.wagon_space_for_passenger = wagon_length_m * wagon_width_m * passenger_per_meter
        self.times = []
        self.positions = []
        self.speed = speed
        self.waiting_time = 0
        self.waiting_time_list = []
        self.train_index = None
        self.passengers = []
        Wagon.wagon_counter += 1
        self.wagon_id = self.generate_wagon_name()
        self.state = 0
        self.assigned_station = None
        self.passenger_matrix = self.initialize_passenger_matrix()
        self.color_matrix = [[0 for _ in range(wagon_length_m)] for _ in range(wagon_width_m)]
        self.is_initial_wagon = False

    def initialize_passenger_matrix(self):
        """Inicializa la matriz que representa la distribución de pasajeros."""
        num_rows = int(self.wagon_width_m)
        num_columns = int(self.wagon_length_m)
        matrix = []
        for _ in range(num_rows):
            row = [0] * num_columns
            matrix.append(row)
        return matrix

    def generate_wagon_name(self):
        """Genera un identificador único para el vagón."""
        return f"Wagon{Wagon.wagon_counter}"
    
    def add_passenger(self, passenger, row, col):
        """Agrega un pasajero al vagón y actualiza su posición."""
        self.passenger_matrix[row][col] += 1
        self.passengers.append(passenger)
        passenger.wagon_position = (row, col)

    def _determine_cell_color(self, passengers_in_cell):
        """
        Determina el color de una celda basado en los pasajeros presentes.
        Retorna:
            0 si la celda está vacía,
            1 si todos tienen la estación destino igual a la asignada,
            2 si todos se mueven a la derecha sin tener la estación asignada,
            3 si todos se mueven a la izquierda sin tener la estación asignada,
            4 en otros casos.
        """
        if not passengers_in_cell:
            return 0
        if all(p.end_station == p.current_wagon.assigned_station for p in passengers_in_cell):
            return 1
        elif all(p.direction == 'right' and p.end_station != p.current_wagon.assigned_station for p in passengers_in_cell):
            return 2
        elif all(p.direction == 'left' and p.end_station != p.current_wagon.assigned_station for p in passengers_in_cell):
            return 3
        else:
            return 4

    def update_color_matrix(self):
        """Actualiza la matriz de colores según la distribución de pasajeros."""
        for row in range(self.wagon_width_m):
            for col in range(self.wagon_length_m):
                passengers_in_cell = [p for p in self.passengers if p.wagon_position == (row, col)]
                self.color_matrix[row][col] = self._determine_cell_color(passengers_in_cell)