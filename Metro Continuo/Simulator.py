import csv
import statistics
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from Train import Train
from Wagon import Wagon
from random import choice
import random

class Simulator:
    """
    Simula el funcionamiento de un sistema ferroviario, gestionando trenes, estaciones, pasajeros
    y la animación de la simulación.
    """

    def __init__(self, speed, number_of_trains, number_of_wagons, wagon_length_m, wagon_width_m, simulator_time, stations, acceleration, deceleration, position_limit, interval, passenger_per_meter, passenger_creation_time):
        
        """
        Inicializa la simulación configurando trenes, estaciones y parámetros de animación.

        Parámetros:
            speed: Velocidad de los trenes.
            number_of_trains: Número total de trenes.
            number_of_wagons: Número de vagones por tren.
            wagon_length_m: Longitud de cada vagón en metros.
            wagon_width_m: Ancho de cada vagón en metros.
            simulator_time: Tiempo total de la simulación.
            stations: Lista de estaciones en la simulación.
            acceleration: Aceleración de los trenes.
            deceleration: Deceleración de los trenes.
            position_limit: Límite de la posición para la animación.
            interval: Intervalo de tiempo entre actualizaciones de la animación.
            passenger_per_meter: Capacidad de pasajeros por metro en el vagón.
            passenger_creation_time: Tiempo de "precalentamiento" en la creacion de pasajeros.
        """
        
        self.speed = speed
        self.headway = (position_limit / number_of_trains) / speed
        self.simulator_time = simulator_time
        self.trains = self.create_trains(number_of_trains, number_of_wagons, wagon_length_m, wagon_width_m, self.headway, passenger_per_meter)
        self.stations = stations
        self.acceleration = acceleration
        self.deceleration = deceleration
        self.add_wagon_to_accelerate = []
        self.wagon_length_m = wagon_length_m
        self.wagon_width_m = wagon_width_m
        self.position_limit = position_limit
        self.interval = interval
        self.passenger_creation_time = passenger_creation_time

        self.initialize_station_points()
        self.assign_stations_to_wagons()

        # Configuración de la animación

        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim(0, self.simulator_time)
        self.ax.set_ylim(0, self.position_limit)

        x_range = self.ax.get_xlim()[1] - self.ax.get_xlim()[0]
        y_range = self.ax.get_ylim()[1] - self.ax.get_ylim()[0]

        constant = 10000
        self.marker_size = constant / min(x_range, y_range)

        # Inicialización de los scatters para trenes y vagones

        self.train_scatters = [self.ax.plot([], [], 'bo', markersize=self.marker_size/2)[0] for _ in self.trains]
        self.wagon_scatters = {train: [self.ax.plot([], [], 'ro', markersize=self.marker_size/2)[0] for _ in train.wagons] for train in self.trains}

        self.decoupled_wagon_scatters = {station: [] for station in self.stations}
        self.passenger_texts = []

        for station in self.stations:
            self.ax.axhline(y=station.position, color='gray', linestyle='--', lw=1)
            passenger_text = self.ax.text(self.simulator_time * 0.95, station.position, f"{station.name}: 0", va='center', ha='right')
            self.passenger_texts.append(passenger_text)

            if station.decoupling_point is not None:
                self.ax.axhline(y=station.decoupling_point, color='red', linestyle='-', lw=1, label='Decoupling Point' if station == self.stations[0] else "")
            if station.coupling_point is not None:
                self.ax.axhline(y=station.coupling_point, color='green', linestyle='-', lw=1, label='Coupling Point' if station == self.stations[0] else "")

    # Train and Wagon Creation
    def create_trains(self, number_of_trains, number_of_wagons, wagon_length_m, wagon_width_m, headway, passenger_per_meter):
        """
        Crea una lista de trenes con sus respectivos vagones, asignando un headway incremental a cada tren.
        """
        trains = []
        for i in range(number_of_trains):
            wagons = [Wagon(wagon_length_m, wagon_width_m, self.speed, passenger_per_meter)
                      for _ in range(number_of_wagons)]
            trains.append(Train(wagons, headway * i, False, passenger_per_meter))
        return trains

    def assign_stations_to_wagons(self):
        """
        Asigna a cada vagón de cada tren una estación de destino de forma cíclica,
        recorriendo los vagones en orden inverso para distribuir equitativamente las estaciones.
        """
        for train in self.trains:
            num_stations = len(self.stations)
            for i, wagon in enumerate(reversed(train.wagons)):
                station_index = i % num_stations
                wagon.assigned_station = self.stations[station_index]


    # Station Initialization
    def initialize_station_points(self):
        """
        Inicializa los puntos de interés de cada estación.
        """
        for station in self.stations:
            self.station_add_points(station)

    def station_add_points(self, station):
        """
        Calcula y asigna a la estación sus puntos de desacople, acople y el inicio del acople.
        """
        decoupling_point = self.decoupling_wagon(station.position, self.speed, self.acceleration)
        station.set_decoupling_point(decoupling_point)

        coupling_point = self.coupling_wagon(station.position, self.speed, self.acceleration)
        station.set_coupling_point(coupling_point)

        start_wagon_for_coupling_point = self.start_wagon_for_coupling(station.position, self.speed, self.acceleration)
        station.set_start_wagon_for_coupling_point(start_wagon_for_coupling_point)

    
    # Mathematical Calculations
    def calculate_distance(self, speed, time):
        """
        Calcula la distancia recorrida en función de la velocidad y el tiempo.
        """
        return speed * time

    def accelerate_distance(self, speed, acceleration):
        """
        Calcula la distancia necesaria para alcanzar la velocidad dada con la aceleración especificada.
        """
        return (speed ** 2) / (2 * acceleration)

    def time_to_decelerate(self, speed, deceleration):
        """
        Calcula el tiempo requerido para detenerse desde la velocidad dada, usando la desaceleración.
        """
        return speed / deceleration

    def time_to_accelerate(self, speed, acceleration):
        """
        Calcula el tiempo necesario para alcanzar la velocidad dada con la aceleración especificada.
        """
        return speed / acceleration

    def decoupling_wagon(self, station_distance, speed, acceleration):
        """
        Determina la posición de desacople, restando la distancia de aceleración a la distancia de la estación.
        """
        return station_distance - self.accelerate_distance(speed, acceleration)

    def coupling_wagon(self, station_distance, speed, acceleration):
        """
        Determina la posición de acople, sumando la distancia de aceleración a la distancia de la estación.
        """
        return station_distance + self.accelerate_distance(speed, acceleration)

    def start_wagon_for_coupling(self, station_distance, speed, acceleration):
        """
        Calcula la posición de inicio para acoplar el vagón, ajustando la distancia según la aceleración y la longitud del vagón.
        """
        return station_distance - (self.calculate_distance(speed, self.time_to_accelerate(speed, acceleration)) - self.accelerate_distance(speed, acceleration)) - self.wagon_length_m

    # Simulation Logic
    def set_train_coordinates(self, train, time):
        """
        Calcula y asigna la posición del tren y de cada uno de sus vagones según el tiempo transcurrido,
        ajustando la posición para que se mantenga dentro de un límite predefinido.
        """
        calculate_time = time - train.headway
        if calculate_time < 0:
            calculate_position = 0
        else:
            calculate_position = calculate_time * self.speed + self.wagon_length_m * train.acquired_wagons

        # Ajusta la posición utilizando el operador módulo para mantenerla dentro del límite
        calculate_position %= self.position_limit
        train.positions.append(calculate_position)
        
        for i, wagon in enumerate(train.wagons):
            wagon_position = calculate_position - (self.wagon_length_m * i)
            wagon.positions.append(wagon_position)

    # Event Handling
    def handle_decoupling_event(self, train, train_index):
        """
        Maneja el evento de desacople: si el último vagón del tren cruza el punto de desacople de alguna estación,
        se desacopla y se asigna a la estación correspondiente.
        """
        if len(train.positions) < 2 or train.positions[-1] == 0 or not train.wagons:
            return

        last_wagon = train.wagons[-1]
        current_position = last_wagon.positions[-1]
        previous_position = last_wagon.positions[-2]

        if current_position < previous_position:
            return

        for station in self.stations:
            if station.decoupling_point is None:
                continue
            if previous_position < station.decoupling_point <= current_position:
                train.wagons.pop()
                last_wagon.state = 1
                last_wagon.train_index = train_index
                station.wagons.append(last_wagon)

    def handle_moving_events(self, wagon):
        """
        Gestiona los eventos de movimiento del vagón en función de su estado.
        Si el vagón está acelerando, en espera o desacelerando, se llama al evento correspondiente.
        """
        if wagon.state == 3:
            self.handle_acceleration_event(wagon)
        elif wagon.state == 2:
            self.handle_waiting_event(wagon)
        elif wagon.state == 1:
            self.handle_deceleration_event(wagon)

    def handle_deceleration_event(self, wagon):
        """
        Gestiona el evento de desaceleración del vagón.
        Aplica la desaceleración y, si la velocidad llega a 0 o menos, se detiene y cambia el estado a espera.
        """
        self.deceleration_wagon(wagon)
        if wagon.speed <= 0:
            wagon.speed = 0
            wagon.state = 2

    def handle_waiting_event(self, wagon):
        """
        Gestiona el evento de espera del vagón en la estación asignada:
        - Permite que los pasajeros se bajen.
        - Incorpora nuevos pasajeros si hay espacio.
        - Verifica si se ha alcanzado el punto de acople para iniciar la aceleración.
        """
        for station in self.stations:
            if wagon in station.wagons:
                self.wait(wagon)
                self.handle_alighting_passengers(wagon, station)
                self.handle_boarding_passengers(wagon, station)
                self.check_coupling_point(wagon, station)
                break

    def handle_alighting_passengers(self, wagon, station):
        """
        Procesa el descenso de pasajeros:
          - Los pasajeros cuyo destino es la estación bajan y se agregan a arrived_passengers.
          - Los demás, que fallan al bajar, se agregan a fail_passengers_arrived.
        """
        passengers_to_arrive = [p for p in wagon.passengers if p.end_station == station and not p.boarded_recently]
        for passenger in passengers_to_arrive:
            wagon.passengers.remove(passenger)
            station.arrived_passengers.append(passenger)

        passengers_failed_to_arrive = [p for p in wagon.passengers if p.end_station != station and not p.boarded_recently]
        for passenger in passengers_failed_to_arrive:
            wagon.passengers.remove(passenger)
            station.fail_passengers_arrived.append(passenger)

    def handle_boarding_passengers(self, wagon, station):
        """
        Incorpora pasajeros al vagón si está en estado de espera y hay espacio disponible.
        Selecciona hasta 6 pasajeros de forma aleatoria para transferirlos al vagón.
        """
        if wagon.state == 2 and station.passengers:
            available_space = wagon.wagon_space_for_passenger - len(wagon.passengers)
            if available_space > 0:
                num_passengers_to_transfer = min(6, len(station.passengers), available_space)
                for _ in range(num_passengers_to_transfer):
                    passenger = random.choice(station.passengers)
                    station.passengers.remove(passenger)
                    passenger.current_wagon = wagon
                    passenger.current_train = None
                    self.add_passenger_to_ordered_position(wagon, passenger)
                    passenger.boarded_recently = True

    def check_coupling_point(self, wagon, station):
        """
        Verifica si se ha alcanzado el punto de acople para iniciar la aceleración del vagón.
        Si es así, registra el tiempo de espera, cambia el estado del vagón y actualiza la bandera de los pasajeros.
        """
        if station.start_wagon_for_coupling_point is not None:
            for train in self.trains:
                if len(train.positions) >= 2:
                    previous_position = train.positions[-2]
                    current_position = train.positions[-1]
                    if previous_position <= station.start_wagon_for_coupling_point <= current_position:
                        wagon.waiting_time_list.append(wagon.waiting_time)
                        wagon.waiting_time = 0
                        wagon.state = 3
                        self.add_wagon_to_accelerate.append(wagon)
                        for passenger in wagon.passengers:
                            passenger.boarded_recently = False
                        break

    def add_passenger_to_ordered_position(self, wagon, passenger):
        """
        Asigna un pasajero a una posición en la matriz del vagón de forma ordenada.
        Si el pasajero está en su estación de destino, se le ubica en las últimas posiciones;
        de lo contrario, se le ubica en las primeras. Además, se actualiza el contador de movimiento
        del pasajero en función de la distancia calculada.
        """
        import math  # Se importa una sola vez al inicio de la función
        width = wagon.wagon_width_m
        length = wagon.wagon_length_m
        max_passengers = 4

        if passenger.end_station == passenger.current_wagon.assigned_station:
            # Buscar desde la última posición hacia la primera
            for row in range(width - 1, -1, -1):
                for col in range(length - 1, -1, -1):
                    if wagon.passenger_matrix[row][col] < max_passengers:
                        wagon.add_passenger(passenger, row, col)
                        distance = math.sqrt(row**2 + (col - (length / 2))**2)
                        passenger.move_count += distance
                        return
        else:
            # Buscar desde la primera posición hacia la última
            for row in range(width):
                for col in range(length):
                    if wagon.passenger_matrix[row][col] < max_passengers:
                        wagon.add_passenger(passenger, row, col)
                        distance = math.sqrt(row**2 + (col - (length / 2))**2)
                        passenger.move_count += distance
                        return

    def handle_acceleration_event(self, wagon):
        """
        Gestiona el evento de aceleración del vagón.
        Si el vagón no está marcado para acelerar, se aplica la aceleración.
        Una vez alcanzada la velocidad deseada, se detiene la aceleración y se transfiere el vagón.
        """
        if wagon not in self.add_wagon_to_accelerate:
            self.acceleration_wagon(wagon)
            if wagon.speed >= self.speed:
                self.stop_acceleration(wagon)
                self.process_wagon_transfer(wagon)

    def stop_acceleration(self, wagon):
        """
        Detiene la aceleración del vagón, estableciendo su velocidad al valor deseado
        y cambiando su estado a inactivo.
        """
        wagon.speed = self.speed
        wagon.state = 0

    def process_wagon_transfer(self, wagon):
        """
        Transfiere el vagón de la estación actual al siguiente tren.
        Busca la estación en la que se encuentra el vagón, obtiene el siguiente tren,
        transfiere los pasajeros, remueve el vagón de la estación y asigna un nuevo tren y estación.
        """
        for station in self.stations:
            if wagon in station.wagons:
                next_train = self.get_next_train_for_wagon(wagon)
                if next_train:
                    self.transfer_passengers_to_train(wagon, next_train)
                    self.remove_wagon_from_station(wagon, station)
                    self.assign_new_station_and_train(wagon, next_train)
                break

    def get_next_train_for_wagon(self, wagon):
        """
        Retorna el siguiente tren al que debe transferirse el vagón, utilizando una lógica cíclica.
        """
        if wagon.train_index is None:
            wagon.train_index = 0
        next_train_index = (wagon.train_index + 1) % len(self.trains)
        return self.trains[next_train_index]
    
    def get_next_train_for_wagon(self, wagon):
        """
        Retorna el siguiente tren al que debe transferirse el vagón, utilizando una lógica cíclica.
        """
        train_index = wagon.train_index if wagon.train_index is not None else 0
        
        if wagon.train_index is None:
            wagon.train_index = 0
            next_train_index = 0
        elif train_index >= len(self.trains) - 1:
            next_train_index = 0
        else:
            next_train_index = train_index + 1

        if 0 <= next_train_index < len(self.trains):
            return self.trains[next_train_index]
        
        return None  # Si no hay un tren válido

    def transfer_passengers_to_train(self, wagon, train):
        """
        Transfiere todos los pasajeros del vagón al tren, asignando el tren actual a cada pasajero.
        """
        for passenger in wagon.passengers:
            passenger.current_train = train
        train.passengers.extend(wagon.passengers)

    def remove_wagon_from_station(self, wagon, station):
        """
        Elimina el vagón de la lista de vagones de la estación.
        """
        station.wagons.remove(wagon)

    def assign_new_station_and_train(self, wagon, train):
        """
        Asigna una nueva estación al vagón, lo inserta al inicio del tren y ajusta la posición del tren.
        """
        self.set_new_station_to_wagon(wagon)
        train.wagons.insert(0, wagon)
        train.acquired_wagons += 1
        train.positions[-1] += wagon.wagon_length_m

    def deceleration_wagon(self, wagon):
        """
        Aplica desaceleración al vagón, actualizando su velocidad y posición.
        """
        dt = 1  # Intervalo de tiempo (segundos)
        last_position = wagon.positions[-1]
        last_speed = wagon.speed
        new_speed = max(0, last_speed - self.deceleration)
        new_position = last_position + last_speed * dt - 0.5 * self.deceleration * dt**2
        wagon.positions.append(new_position)
        wagon.speed = new_speed

    def acceleration_wagon(self, wagon):
        """
        Acelera el vagón, actualizando su velocidad y posición hasta alcanzar la velocidad objetivo.
        """
        dt = 1  # Intervalo de tiempo (segundos)
        last_position = wagon.positions[-1]
        last_speed = wagon.speed
        new_speed = min(self.speed, last_speed + self.acceleration)
        new_position = last_position + last_speed * dt + 0.5 * self.acceleration * dt**2
        wagon.positions.append(new_position)
        wagon.speed = new_speed

    def wait(self, wagon):
        """
        Incrementa el tiempo de espera del vagón y mantiene su posición constante.
        """
        last_position = wagon.positions[-1]
        wagon.waiting_time += 1
        wagon.positions.append(last_position)

    # Station Management
    def set_new_station_to_wagon(self, wagon):
        """
        Asigna una nueva estación al vagón basado en la asignación del tren siguiente.
        Si el vagón es inicial, se asigna al primer tren y se marca como no inicial.
        En otro caso, se toma el tren siguiente y se asigna la estación siguiente a la
        del primer vagón de ese tren, según el orden de las estaciones.
        """
        if wagon.is_initial_wagon:
            next_train_index = 0
            wagon.is_initial_wagon = False
        else:
            next_train_index = (wagon.train_index + 1) % len(self.trains)
        next_train = self.trains[next_train_index]
        
        if next_train.wagons:
            first_wagon_assigned_station = next_train.wagons[0].assigned_station
            try:
                station_index = self.stations.index(first_wagon_assigned_station)
                new_station_index = (station_index + 1) % len(self.stations)
                wagon.assigned_station = self.stations[new_station_index]
            except ValueError:
                pass

    # Passengers Management
    def update_all_passengers(self, time_increment):
        """
        Actualiza el tiempo de viaje de todos los pasajeros, tanto en las estaciones como en los trenes,
        incrementando su contador de tiempo en el intervalo proporcionado.
        """
        for station in self.stations:
            for wagon in station.wagons:
                for passenger in wagon.passengers:
                    passenger.update_timer(time_increment)

        for train in self.trains:
            for wagon in train.wagons:
                for passenger in wagon.passengers:
                    passenger.update_timer(time_increment)

    # Print INFO
    def generate_report(self):
        """
        Genera y muestra un reporte con la siguiente información:
          - Para cada estación:
              * Número de pasajeros llegados (aquellos cuyo end_station es la estación actual).
              * Promedio del tiempo de viaje (travel_time) de los pasajeros que llegaron.
              * Número de pasajeros fallidos.
          - Al final, se muestra el total de pasajeros que se movieron (llegaron a su estación)
            durante el tiempo de simulación, expresado en horas.
        """
        total_arrived = 0
        total_move_distance = 0
        total_passengers_global = 0

        print("Reporte de pasajeros en estaciones:\n")
        for station in self.stations:
            # Se filtran los pasajeros que han llegado a la estación (end_station coincide con la estación)
            arrived_passengers = [p for p in station.arrived_passengers if p.end_station == station]
            num_arrived = len(arrived_passengers)
            total_arrived += num_arrived
            total_passengers_global += num_arrived

            # Acumular la distancia recorrida (move_count) de todos los pasajeros de la estación
            total_move_distance += sum(p.move_count for p in arrived_passengers)

            # Número de pasajeros fallidos de la estación
            num_failed = len(station.fail_passengers_arrived)

            print(f"Estación: {station.name}")
            print(f"  - Número de pasajeros llegados: {num_arrived}")
            print(f"  - Número de pasajeros fallidos: {num_failed}")
            print("--------------------------------------------------")

        # Calcular el promedio global de metros movidos entre todos los pasajeros llegados
        if total_passengers_global > 0:
            global_avg_move = total_move_distance / total_passengers_global
        else:
            global_avg_move = 0

        print(f"\nPromedio global de metros movidos por pasajero: {global_avg_move:.2f}")

        # Imprimir el headway obtenido de self.hedway
        print(f"Headway: {self.headway}")

        # Calcular la mediana del tiempo de espera de todos los wagones (acumulando los valores de waiting_time_list)
        all_waiting_times = []
        for train in self.trains:
            for wagon in train.wagons:
                all_waiting_times.extend(wagon.waiting_time_list)
        if all_waiting_times:
            median_waiting_time = statistics.median(all_waiting_times)
        else:
            median_waiting_time = 0
        print(f"Mediana de tiempo de espera de los wagones: {median_waiting_time:.2f} segundos")

        # Convertir el tiempo de simulación de segundos a horas
        simulator_time_hours = (self.simulator_time - self.passenger_creation_time) / 3600
        print(f"\nEn un tiempo de {(simulator_time_hours):.2f} horas, se movieron un total de {total_arrived} pasajeros.")

        # Exportar el reporte detallado de pasajeros a archivo
        self.export_passenger_report("passenger_report.csv")
        self.export_fail_passenger_report("fail_passenger_report.csv")

    def export_passenger_report(self, filename):
        """
        Crea un archivo CSV con el siguiente encabezado:
        - Tiempo de viaje de cada pasajero
        - Metros desplazados
        - Estaciones desplazadas

        La cantidad de estaciones desplazadas se calcula a partir de la lista fija de estaciones L6,
        considerando que si el pasajero sube en una estación y baja en otra, si el índice destino es menor que el de origen se da la vuelta a la lista.
        """
        station_order = [
            "Cerrillos",
            "Lo Valledor",
            "Pedro Aguirre Cerda",
            "Franklin L6",
            "Bio Bio",
            "Nuble L6",
            "Estadio Nacional",
            "Nunoa L6",
            "Ines de Suarez",
            "Los Leones L6"
        ]

        def compute_station_difference(start, destination, stations_list):
            index_start = stations_list.index(start)
            index_destination = stations_list.index(destination)
            if index_destination >= index_start:
                return index_destination - index_start
            else:
                return (len(stations_list) - index_start) + index_destination

        rows = []
        headers = ["Tiempo de viaje", "Metros desplazados", "Estaciones desplazadas"]

        # Recorrer todas las estaciones y sus pasajeros para obtener la información de cada pasajero
        for station in self.stations:
            for passenger in station.arrived_passengers:
                start_name = getattr(passenger.start_station, "name", passenger.start_station)
                destination_name = getattr(passenger.end_station, "name", passenger.end_station)
                try:
                    stations_diff = compute_station_difference(start_name, destination_name, station_order)
                except Exception as e:
                    stations_diff = None
                rows.append({
                    "Tiempo de viaje": passenger.travel_time,
                    "Metros desplazados": passenger.move_count,
                    "Estaciones desplazadas": stations_diff
                })

        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        print(f"Reporte detallado exportado a {filename}")


    def export_fail_passenger_report(self, filename):
        """
        Crea un archivo CSV con el siguiente encabezado:
          - Tiempo de viaje de cada pasajero
          - Metros desplazados
          - Estaciones desplazadas

        La cantidad de estaciones desplazadas se calcula a partir de la lista fija de estaciones L6,
        considerando que si el pasajero sube en una estación y baja en otra, si el índice destino es menor que el de origen se da la vuelta a la lista.
        """
        station_order = [
            "Cerrillos",
            "Lo Valledor",
            "Pedro Aguirre Cerda",
            "Franklin L6",
            "Bio Bio",
            "Nuble L6",
            "Estadio Nacional",
            "Nunoa L6",
            "Ines de Suarez",
            "Los Leones L6"
        ]

        def compute_station_difference(start, destination, stations_list):
            index_start = stations_list.index(start)
            index_destination = stations_list.index(destination)
            if index_destination >= index_start:
                return index_destination - index_start
            else:
                return (len(stations_list) - index_start) + index_destination

        rows = []
        headers = ["Tiempo de viaje", "Metros desplazados", "Estaciones desplazadas"]

        # Recorrer todas las estaciones y sus pasajeros fallidos para obtener la información de cada pasajero
        for station in self.stations:
            for passenger in station.fail_passengers_arrived:
                start_name = getattr(passenger.start_station, "name", passenger.start_station)
                destination_name = getattr(passenger.end_station, "name", passenger.end_station)
                try:
                    stations_diff = compute_station_difference(start_name, destination_name, station_order)
                except Exception as e:
                    stations_diff = None
                rows.append({
                    "Tiempo de viaje": passenger.travel_time,
                    "Metros desplazados": passenger.move_count,
                    "Estaciones desplazadas": stations_diff
                })

        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        print(f"Reporte detallado de fallidos exportado a {filename}")

    # Simulation Execution
    def run_simulation(self):
        """
        Ejecuta la animación de la simulación y, una vez finalizada, genera el reporte.
        """
        ani = FuncAnimation(
            self.fig,
            self.update,
            frames=range(self.simulator_time),
            init_func=self.init,
            interval=self.interval,
            blit=True
        )
        plt.show()
        self.generate_report()

    def init(self):
        """
        Inicializa los scatter plots de trenes, vagones y vagones desacoplados, 
        limpiando sus datos para el inicio de la animación.
        Retorna una lista concatenada de todos los scatters para la animación.
        """
        for scatter in self.train_scatters:
            scatter.set_data([], [])

        for scatters in self.wagon_scatters.values():
            for scatter in scatters:
                scatter.set_data([], [])

        for station_scatters in self.decoupled_wagon_scatters.values():
            for scatter in station_scatters:
                scatter.set_data([], [])

        all_decoupled_scatters = [
            scatter for scatters in self.decoupled_wagon_scatters.values() for scatter in scatters
        ]

        return (
            self.train_scatters +
            [scatter for scatters in self.wagon_scatters.values() for scatter in scatters] +
            all_decoupled_scatters
        )

    def update(self, frame):
        """
        Actualiza la posición de trenes, vagones y pasajeros en cada frame de la animación.
        También se encarga de:
          - Ajustar las posiciones de trenes y vagones.
          - Actualizar las etiquetas que muestran el número de pasajeros.
          - Manejar el movimiento de vagones desacoplados.
          - Crear nuevos pasajeros en las estaciones a partir de un tiempo de creación definido.
          - Procesar eventos de desacople de vagones.
          - Actualizar el tiempo de viaje de todos los pasajeros.
        Retorna una lista con todos los objetos actualizados para la animación.
        """

        if frame >= self.simulator_time:
            return

        all_scatters = []
        station_wagon_labels = {station: [] for station in self.stations}
        wagon_passenger_labels = {train: [] for train in self.trains}

        for train_index, (train_scatter, train) in enumerate(zip(self.train_scatters, self.trains)):
            self.set_train_coordinates(train, frame)
            train.handle_moving_passengers()

            if train.wagons:
                train_scatter.set_data([frame], [train.positions[-1]])
                all_scatters.append(train_scatter)

            current_wagon_scatters = self.wagon_scatters[train]
            while len(current_wagon_scatters) < len(train.wagons):
                scatter, = self.ax.plot([], [], 'ro', markersize=self.marker_size/2)
                current_wagon_scatters.insert(0, scatter)

            for i, (wagon, wagon_scatter) in enumerate(zip(train.wagons, current_wagon_scatters)):
                wagon_scatter.set_data([frame], [wagon.positions[-1]])
                all_scatters.append(wagon_scatter)

                label_offset = i * 100

                # Crear o actualizar la etiqueta del número de pasajeros para cada vagón acoplado al tren
                if i >= len(wagon_passenger_labels[train]):
                    passenger_label = self.ax.text(frame + label_offset, wagon.positions[-1], f"{len(wagon.passengers)}", fontsize=8, ha='left', color='black')
                    wagon_passenger_labels[train].append(passenger_label)
                else:
                    wagon_passenger_labels[train][i].set_position((frame + label_offset, wagon.positions[-1]))
                    wagon_passenger_labels[train][i].set_text(f"{len(wagon.passengers)}")

            if len(current_wagon_scatters) > len(train.wagons):
                for _ in range(len(current_wagon_scatters) - len(train.wagons)):
                    scatter_to_remove = current_wagon_scatters.pop(0)
                    scatter_to_remove.set_data([], [])

        # Manejar los vagones desacoplados
        self.add_wagon_to_accelerate = []
        for station in self.stations:
            while len(self.decoupled_wagon_scatters[station]) < len(station.wagons):
                scatter, = self.ax.plot([], [], 'ro', markersize=self.marker_size/2)
                self.decoupled_wagon_scatters[station].append(scatter)

            for wagon, scatter in zip(station.wagons, self.decoupled_wagon_scatters[station]):
                self.handle_moving_events(wagon)
                scatter.set_data([frame], [wagon.positions[-1]])
                all_scatters.append(scatter)

                if wagon in station.wagons:
                    if len(station_wagon_labels[station]) <= station.wagons.index(wagon):
                        passenger_label = self.ax.text(frame, wagon.positions[-1], str(len(wagon.passengers)), fontsize=8, ha='left', color='black')
                        station_wagon_labels[station].append(passenger_label)
                    else:
                        label_index = station.wagons.index(wagon)
                        station_wagon_labels[station][label_index].set_position((frame, wagon.positions[-1]))
                        station_wagon_labels[station][label_index].set_text(str(len(wagon.passengers)))

            station_wagon_labels[station] = station_wagon_labels[station][:len(station.wagons)]

        # Actualizar los pasajeros de las estaciones y manejar el desacoplamiento
        for station_index, station in enumerate(self.stations):
            if frame >= self.passenger_creation_time:
                station.create_passenger(self.stations)
            self.passenger_texts[station_index].set_text(f"{station.name}: {len(station.passengers)}")

        for train_index, train in enumerate(self.trains):
            self.handle_decoupling_event(train, train_index)

        self.update_all_passengers(1)

        all_scatters += [label for labels in station_wagon_labels.values() for label in labels] + self.passenger_texts + [label for labels in wagon_passenger_labels.values() for label in labels]

        return all_scatters

    def animate_train_simulation(self):
        """
        Muestra una animación en la que se visualizan los trenes y sus vagones.
        Cada vagón se representa mediante una imagen que muestra su matriz de colores,
        sobre la cual se superpone el número de pasajeros en cada celda.
        """
        plt.close(self.fig)
        max_wagons = max(len(train.wagons) for train in self.trains)
        fig, axes = plt.subplots(
            nrows=len(self.trains),
            ncols=max_wagons,
            figsize=(max_wagons * 2, len(self.trains) * 2),
            gridspec_kw={'hspace': 0.5, 'wspace': 0.2}
        )

        # Asegurar que axes sea una lista de listas para facilitar la iteración
        if len(self.trains) == 1:
            axes = [axes]
        elif len(self.trains) > 1 and isinstance(axes[0], np.ndarray):
            axes = axes
        else:
            axes = [ax if isinstance(ax, np.ndarray) else [ax] for ax in axes]

        # Precomputar el mapa de colores para mayor eficiencia
        color_map_arr = np.array([
            [0.5, 0.5, 0.5],  # gris
            [1, 0, 0],        # rojo
            [0, 0, 1],        # azul
            [0, 1, 0],        # verde
            [1, 1, 0]         # amarillo
        ])

        def update(frame):
            """
            Función interna que se llama en cada frame de la animación.
            Actualiza la lógica de la simulación, la posición de cada tren, vagón y
            actualiza las imágenes de las matrices de colores y etiquetas de pasajeros.
            """
            self.update(frame)

            for train, axs in zip(self.trains, axes):
                num_active_wagons = len(train.wagons)
                for i, ax in enumerate(axs):
                    ax.clear()
                    if i < num_active_wagons:
                        wagon = train.wagons[i]
                        # Convertir las matrices a NumPy para procesamiento vectorizado
                        passenger_matrix = np.asarray(wagon.passenger_matrix)
                        color_matrix = np.asarray(wagon.color_matrix)
                        # Crear la cuadrícula de colores usando el mapa precomputado
                        color_grid = color_map_arr[color_matrix]
                        ax.imshow(color_grid, aspect='equal')
                        # Mostrar el número de pasajeros en cada celda
                        for (r, c), val in np.ndenumerate(passenger_matrix):
                            ax.text(c, r, str(val), ha='center', va='center', color='white', fontsize=6)
                        ax.set_title(f'{wagon.assigned_station.name} ({passenger_matrix.sum()} passengers)')
                    else:
                        # Si no hay vagón, se muestra un placeholder
                        ax.matshow(np.zeros((5, 5)), cmap='gray', aspect='equal')
                        ax.set_title("Decouple Wagon")
                        ax.axis('off')

        ani = FuncAnimation(
            fig, update, frames=range(self.simulator_time),
            interval=self.interval, repeat=False
        )
        plt.show()

    def execute_simulation_logic(self):
        """
        Ejecuta la simulación lógica sin mostrar la animación gráfica.
        Una vez finalizada, genera el reporte final.
        """
        for frame in range(self.simulator_time):
            self.update(frame)
        self.generate_report()
