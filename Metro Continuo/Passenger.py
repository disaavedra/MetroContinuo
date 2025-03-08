import uuid

class Passenger:
    """
    Clase que representa un pasajero, almacenando información sobre su viaje,
    sus estaciones de origen y destino, y su estado durante el trayecto.
    """
    
    def __init__(self, start_station, end_station):
        """
        Inicializa una instancia de Passenger asignándole un identificador único
        y definiendo las estaciones de origen y destino.

        Parámetros:
            start_station: Estación de origen del pasajero.
            end_station: Estación de destino del pasajero.
        """
        self.name = str(uuid.uuid4())
        self.start_station = start_station
        self.end_station = end_station
        self.travel_time = 0
        self.current_train = None
        self.current_wagon = None
        self.wagon_position = 0
        self.movement_speed = 1
        self.boarded_recently = True
        self.direction = 'right'
        self.assigned_direction = False
        self.move_count = 0

    def start_timer(self):
        """Reinicia el contador del tiempo de viaje."""
        self.travel_time = 0

    def update_timer(self, time_increment):
        """
        Incrementa el contador del tiempo de viaje.

        Parámetros:
            time_increment: Valor a sumar al tiempo de viaje.
        """
        self.travel_time += time_increment
