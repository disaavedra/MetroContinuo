import numpy as np
from Passenger import Passenger
from Wagon import Wagon

class Station:
    """
    Representa una estación, gestionando los vagones, pasajeros y puntos de interés relacionados
    con la operación del tren.
    """
    
    def __init__(self, name, position, wagon_length_m, wagon_width_m, station_capacity, passenger_flows, passenger_per_meter):
        """
        Inicializa la estación con sus parámetros y crea el primer vagón inicial.

        Parámetros:
            name: Nombre de la estación.
            position: Posición de la estación.
            wagon_length_m: Longitud de los vagones en metros.
            wagon_width_m: Ancho de los vagones en metros.
            station_capacity: Capacidad máxima de pasajeros de la estación.
            passenger_flows: Flujos de pasajeros (usados para calcular probabilidades de destino).
            passenger_per_meter: Factor para calcular el espacio disponible por pasajero.
        """
        self.name = name
        self.position = position
        self.wagons = []
        self.decoupling_point = None
        self.start_wagon_for_coupling_point = None
        self.coupling_point = None
        self.passengers = []
        self.arrived_passengers = []
        self.fail_passengers_arrived = []
        self.wagon_length_m = wagon_length_m
        self.wagon_width_m = wagon_width_m
        self.station_capacity = station_capacity
        self.passenger_flows = passenger_flows
        self.passenger_creation = sum(passenger_flows) / 3600
        self.destination_probabilities = self.calculate_probabilities()
        self.create_initial_wagon(passenger_per_meter)

    def calculate_probabilities(self):
        """
        Calcula las probabilidades de destino para los pasajeros en función de los flujos.

        Retorna:
            Lista de probabilidades para cada destino basado en passenger_flows.
        """
        flow_sum = sum(self.passenger_flows)
        if flow_sum == 0:
            return [0] * len(self.passenger_flows)
        return [flow / flow_sum for flow in self.passenger_flows]

    def create_initial_wagon(self, passenger_per_meter):
        """
        Crea el vagón inicial de la estación que se mantiene en espera hasta que llegue un tren.

        Parámetros:
            passenger_per_meter: Factor para calcular el espacio disponible por pasajero en el vagón.
        """
        initial_wagon = Wagon(self.wagon_length_m, self.wagon_width_m, speed=0, passenger_per_meter=passenger_per_meter)
        initial_wagon.state = 2
        initial_wagon.assigned_station = self
        initial_wagon.positions.append(self.position)
        initial_wagon.is_initial_wagon = True
        self.wagons.append(initial_wagon)

    def set_decoupling_point(self, decoupling_point):
        """
        Establece el punto de desacoplamiento, donde el último vagón se desacopla para detenerse.

        Parámetros:
            decoupling_point: Punto de desacoplamiento.
        """
        self.decoupling_point = decoupling_point

    def set_start_wagon_for_coupling_point(self, start_wagon_for_coupling_point):
        """
        Establece el punto donde se inicia el movimiento del vagón detenido para acoplarse al tren.

        Parámetros:
            start_wagon_for_coupling_point: Punto de inicio para el acople.
        """
        self.start_wagon_for_coupling_point = start_wagon_for_coupling_point

    def set_coupling_point(self, coupling_point):
        """
        Establece el punto de acople, donde el vagón de la estación se conecta al tren.

        Parámetros:
            coupling_point: Punto de acople.
        """
        self.coupling_point = coupling_point

    def create_passenger(self, stations):
        """
        Crea pasajeros en la estación usando una distribución de Poisson.
        Esta distribución se usa ya que pueden generarse más de un pasajero por segundo.
        A cada pasajero se le asigna un destino de forma probabilística basado en destination_probabilities.
        Si se supera la capacidad de la estación, se limita el número de pasajeros.

        Parámetros:
            stations: Lista de estaciones para asignar destinos.
        """
        if len(self.passengers) >= self.station_capacity:
            return []
        num_passengers = np.random.poisson(self.passenger_creation)
        for _ in range(num_passengers):
            if self.destination_probabilities:
                end_station = np.random.choice(stations, p=self.destination_probabilities)
                if end_station != self:
                    new_passenger = Passenger(self, end_station)
                    new_passenger.start_timer()
                    self.passengers.append(new_passenger)
        if len(self.passengers) > self.station_capacity:
            self.passengers = self.passengers[:self.station_capacity]
