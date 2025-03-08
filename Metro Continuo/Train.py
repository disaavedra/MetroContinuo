import uuid

class Train:
    """
    Clase que representa un tren, gestionando vagones, el movimiento de pasajeros
    y las interacciones entre ellos.
    """
    def __init__(self, wagons, headway, active, passenger_per_meter):
        """
        Inicializa una instancia de Train.

        Parámetros:
            wagons: Lista de vagones que componen el tren.
            headway: Intervalo entre trenes.
            active: Indicador de si el tren está activo.
            passenger_per_meter: Capacidad de pasajeros por metro en el vagón.
        """
        self.wagons = wagons
        self.headway = headway
        self.active = active
        self.train_id = self.generate_unique_id()
        self.passengers = []
        self.positions = []
        self.cycles = 1
        self.acquired_wagons = 0
        self.passenger_per_meter = passenger_per_meter

    def generate_unique_id(self):
        return str(uuid.uuid4())

    def move_passenger_right(self, wagon, passenger, row, col):
        """
        Mueve al pasajero una celda hacia la derecha si es posible.
        """
        next_col = col + 1
        if next_col < wagon.wagon_length_m and wagon.passenger_matrix[row][next_col] < self.passenger_per_meter:
            wagon.passenger_matrix[row][col] -= 1
            wagon.passenger_matrix[row][next_col] += 1
            passenger.wagon_position = (row, next_col)
            if row != wagon.wagon_width_m - 1:
                passenger.move_count += 1
        else:
            passenger.direction = 'left'

    def move_passenger_left(self, wagon, passenger, row, col):
        """
        Mueve al pasajero una celda hacia la izquierda si es posible.
        """
        prev_col = col - 1
        if prev_col >= 0 and wagon.passenger_matrix[row][prev_col] < self.passenger_per_meter:
            wagon.passenger_matrix[row][col] -= 1
            wagon.passenger_matrix[row][prev_col] += 1
            passenger.wagon_position = (row, prev_col)
            if row != wagon.wagon_width_m - 1:
                passenger.move_count += 1
        else:
            passenger.direction = 'right'

    def move_passenger_down(self, wagon, passenger, row, col):
        """
        Mueve al pasajero una celda hacia abajo si es posible.
        """
        next_row = row + 1
        if next_row < wagon.wagon_width_m and wagon.passenger_matrix[next_row][col] < self.passenger_per_meter:
            wagon.passenger_matrix[row][col] -= 1
            wagon.passenger_matrix[next_row][col] += 1
            passenger.wagon_position = (next_row, col)
            passenger.move_count += 1
            return True
        return False
    
    def move_passenger_down_or_right(self, wagon, passenger, row, col):
        """
        Mueve al pasajero hacia abajo si es posible. Si no hay espacio,
        lo mueve a la derecha.
        """
        if not self.move_passenger_down(wagon, passenger, row, col):
            self.move_passenger_right(wagon, passenger, row, col)

    def move_passenger_down_or_left(self, wagon, passenger, row, col):
        """
        Mueve al pasajero hacia abajo si es posible. Si no hay espacio,
        lo mueve a la izquierda.
        """
        if not self.move_passenger_down(wagon, passenger, row, col):
            self.move_passenger_left(wagon, passenger, row, col)

    def move_passenger_to_next_wagon(self, wagon, passenger, row, col, next_wagon):
        """
        Mueve al pasajero del último asiento del vagón actual al primer
        asiento del siguiente vagón. Si no puede moverse a la posición (row, 0)
        en el siguiente vagón, intenta moverse a la celda de arriba o abajo.
        """
        # Intentar moverse a la posición (row, 0) del siguiente vagón
        if next_wagon.passenger_matrix[row][0] < self.passenger_per_meter:
            # Movimiento exitoso a la primera columna del siguiente vagón
            wagon.passenger_matrix[row][col] -= 1
            next_wagon.passenger_matrix[row][0] += 1
            passenger.wagon_position = (row, 0)
            passenger.current_wagon = next_wagon
            wagon.passengers.remove(passenger)
            next_wagon.passengers.append(passenger)
            passenger.move_count += 1
        else:
            # Si no hay espacio en la posición (row, 0), intentar moverse hacia arriba (row-1)
            if row > 0 and next_wagon.passenger_matrix[row - 1][0] < self.passenger_per_meter:
                # Movimiento exitoso hacia arriba
                wagon.passenger_matrix[row][col] -= 1
                next_wagon.passenger_matrix[row - 1][0] += 1
                passenger.wagon_position = (row - 1, 0)
                passenger.current_wagon = next_wagon
                wagon.passengers.remove(passenger)
                next_wagon.passengers.append(passenger)
                passenger.move_count += 1
            # Si no hay espacio arriba, intentar moverse hacia abajo (row+1)
            elif row < next_wagon.wagon_width_m - 1 and next_wagon.passenger_matrix[row + 1][0] < self.passenger_per_meter:
                # Movimiento exitoso hacia abajo
                wagon.passenger_matrix[row][col] -= 1
                next_wagon.passenger_matrix[row + 1][0] += 1
                passenger.wagon_position = (row + 1, 0)
                passenger.current_wagon = next_wagon
                wagon.passengers.remove(passenger)
                next_wagon.passengers.append(passenger)
                passenger.move_count += 1

    def move_passenger_up_right_or_down_right(self, wagon, passenger, row, col):
        """
        Modifica el movimiento del pasajero dentro del vagón.
        - Si no está en su vagón de destino, intenta moverse en diagonal arriba a la derecha,
        luego a la derecha, y finalmente en diagonal abajo a la derecha.
        """
        if passenger.end_station != passenger.current_wagon.assigned_station:
            # Intentar mover en diagonal arriba a la derecha si hay espacio
            if row > 0 and col + 1 < wagon.wagon_length_m and wagon.passenger_matrix[row - 1][col + 1] < self.passenger_per_meter:
                wagon.passenger_matrix[row][col] -= 1
                wagon.passenger_matrix[row - 1][col + 1] += 1
                passenger.wagon_position = (row - 1, col + 1)
                passenger.move_count += 1
            # Si no puede, intentar mover a la derecha
            elif col + 1 < wagon.wagon_length_m and wagon.passenger_matrix[row][col + 1] < self.passenger_per_meter:
                wagon.passenger_matrix[row][col] -= 1
                wagon.passenger_matrix[row][col + 1] += 1
                passenger.wagon_position = (row, col + 1)
                passenger.move_count += 1
            # Si no puede, intentar mover en diagonal abajo a la derecha
            elif row + 1 < wagon.wagon_width_m and col + 1 < wagon.wagon_length_m and wagon.passenger_matrix[row + 1][col + 1] < self.passenger_per_meter:
                wagon.passenger_matrix[row][col] -= 1
                wagon.passenger_matrix[row + 1][col + 1] += 1
                passenger.wagon_position = (row + 1, col + 1)
                passenger.move_count += 1

    def move_passenger_left_if_no_wagon(self, wagon, passenger, row, col):
        """
        Mueve al pasajero hacia la izquierda si su vagón de destino no está presente en el tren,
        evitando, dentro de lo posible, que se desplace por la primera y última fila.
        La prioridad de movimiento es:
        - Si está en la primera fila, intenta moverse abajo a la izquierda, luego a la izquierda.
        - Si está en la última fila, intenta moverse arriba a la izquierda, luego a la izquierda.
        - Para las filas intermedias, intenta moverse a la izquierda, luego abajo a la izquierda, y por último arriba a la izquierda.
        """

        # Si el pasajero está en la primera fila (row 0)
        if row == 0:
            # Intentar mover en diagonal abajo a la izquierda
            if row < wagon.wagon_width_m - 1 and col > 0 and wagon.passenger_matrix[row + 1][col - 1] < self.passenger_per_meter:
                wagon.passenger_matrix[row][col] -= 1
                wagon.passenger_matrix[row + 1][col - 1] += 1
                passenger.wagon_position = (row + 1, col - 1)
                passenger.move_count += 1
            # Si no puede moverse abajo a la izquierda, intentar moverse a la izquierda
            elif col > 0 and wagon.passenger_matrix[row][col - 1] < self.passenger_per_meter:
                wagon.passenger_matrix[row][col] -= 1
                wagon.passenger_matrix[row][col - 1] += 1
                passenger.wagon_position = (row, col - 1)
                passenger.move_count += 1

        # Si el pasajero está en la última fila (row n-1)
        elif row == wagon.wagon_width_m - 1:
            # Intentar mover en diagonal arriba a la izquierda
            if row > 0 and col > 0 and wagon.passenger_matrix[row - 1][col - 1] < self.passenger_per_meter:
                wagon.passenger_matrix[row][col] -= 1
                wagon.passenger_matrix[row - 1][col - 1] += 1
                passenger.wagon_position = (row - 1, col - 1)
                passenger.move_count += 1
            # Si no puede moverse arriba a la izquierda, intentar moverse a la izquierda
            elif col > 0 and wagon.passenger_matrix[row][col - 1] < self.passenger_per_meter:
                wagon.passenger_matrix[row][col] -= 1
                wagon.passenger_matrix[row][col - 1] += 1
                passenger.wagon_position = (row, col - 1)
                passenger.move_count += 1

        # Si el pasajero está en una fila intermedia
        else:
            # Intentar moverse a la izquierda
            if col > 0 and wagon.passenger_matrix[row][col - 1] < self.passenger_per_meter:
                wagon.passenger_matrix[row][col] -= 1
                wagon.passenger_matrix[row][col - 1] += 1
                passenger.wagon_position = (row, col - 1)
                passenger.move_count += 1
            # Si no puede moverse a la izquierda, intentar moverse abajo a la izquierda
            elif row < wagon.wagon_width_m - 1 and col > 0 and wagon.passenger_matrix[row + 1][col - 1] < self.passenger_per_meter:
                wagon.passenger_matrix[row][col] -= 1
                wagon.passenger_matrix[row + 1][col - 1] += 1
                passenger.wagon_position = (row + 1, col - 1)
                passenger.move_count += 1
            # Si no puede moverse abajo a la izquierda, intentar moverse arriba a la izquierda
            elif row > 0 and col > 0 and wagon.passenger_matrix[row - 1][col - 1] < self.passenger_per_meter:
                wagon.passenger_matrix[row][col] -= 1
                wagon.passenger_matrix[row - 1][col - 1] += 1
                passenger.wagon_position = (row - 1, col - 1)
                passenger.move_count += 1

    def move_passenger_to_previous_wagon(self, wagon, passenger, row, col, prev_wagon):
        """
        Mueve al pasajero del primer asiento del vagón actual al último asiento
        del vagón anterior. Si no puede moverse a la posición (row, último asiento)
        en el vagón anterior, intenta moverse a la celda de arriba o abajo.
        """
        # Intentar moverse a la última columna (row, última columna) del vagón anterior
        if prev_wagon.passenger_matrix[row][prev_wagon.wagon_length_m - 1] < self.passenger_per_meter:
            # Movimiento exitoso al último asiento del vagón anterior
            wagon.passenger_matrix[row][col] -= 1
            prev_wagon.passenger_matrix[row][prev_wagon.wagon_length_m - 1] += 1
            passenger.wagon_position = (row, prev_wagon.wagon_length_m - 1)
            passenger.current_wagon = prev_wagon
            wagon.passengers.remove(passenger)
            prev_wagon.passengers.append(passenger)
            passenger.move_count += 1
        else:
            # Si no hay espacio en la posición (row, última columna), intentar moverse hacia arriba (row-1)
            if row > 0 and prev_wagon.passenger_matrix[row - 1][prev_wagon.wagon_length_m - 1] < self.passenger_per_meter:
                # Movimiento exitoso hacia arriba
                wagon.passenger_matrix[row][col] -= 1
                prev_wagon.passenger_matrix[row - 1][prev_wagon.wagon_length_m - 1] += 1
                passenger.wagon_position = (row - 1, prev_wagon.wagon_length_m - 1)
                passenger.current_wagon = prev_wagon
                wagon.passengers.remove(passenger)
                prev_wagon.passengers.append(passenger)
                passenger.move_count += 1
            # Si no hay espacio arriba, intentar moverse hacia abajo (row+1)
            elif row < prev_wagon.wagon_width_m - 1 and prev_wagon.passenger_matrix[row + 1][prev_wagon.wagon_length_m - 1] < self.passenger_per_meter:
                # Movimiento exitoso hacia abajo
                wagon.passenger_matrix[row][col] -= 1
                prev_wagon.passenger_matrix[row + 1][prev_wagon.wagon_length_m - 1] += 1
                passenger.wagon_position = (row + 1, prev_wagon.wagon_length_m - 1)
                passenger.current_wagon = prev_wagon
                wagon.passengers.remove(passenger)
                prev_wagon.passengers.append(passenger)
                passenger.move_count += 1

    def handle_moving_passengers(self):
        """
        Gestiona el movimiento de los pasajeros dentro del tren.
        Si el vagón de destino está en el tren, el pasajero sigue moviéndose a la derecha.
        Si el vagón de destino no está en el tren, el pasajero cambia la dirección a la izquierda.
        """
        moved_passengers = []

        for wagon_number, wagon in enumerate(self.wagons):
            for passenger in list(wagon.passengers):
                if passenger not in moved_passengers:
                    row, col = passenger.wagon_position

                    if passenger.end_station == passenger.current_wagon.assigned_station:
                        if passenger.direction == 'right':
                            self.move_passenger_down_or_right(wagon, passenger, row, col)
                        elif passenger.direction == 'left':
                            self.move_passenger_down_or_left(wagon, passenger, row, col)
                        continue

                    # Verificar si el vagón de destino está presente en el tren
                    destination_wagon_present = any(
                        w.assigned_station == passenger.end_station for w in self.wagons
                    )

                    # Cambiar la dirección a 'left' si el vagón de destino no está presente
                    if not destination_wagon_present and passenger.assigned_direction == False:
                        passenger.direction = 'left'
                    
                    # Manejar movimiento hacia la derecha
                    if passenger.direction == 'right':
                        if col < wagon.wagon_length_m - 1:
                            # Intentar mover hacia arriba a la derecha o hacia la derecha
                            self.move_passenger_up_right_or_down_right(wagon, passenger, row, col)
                        elif col >= wagon.wagon_length_m - 1:
                            # Intentar pasar al siguiente vagón si está en la última columna
                            if wagon_number + 1 < len(self.wagons):
                                next_wagon = self.wagons[wagon_number + 1]
                                self.move_passenger_to_next_wagon(wagon, passenger, row, col, next_wagon)
                                moved_passengers.append(passenger)
                        passenger.assigned_direction = True
                    
                    # Manejar movimiento hacia la izquierda
                    elif passenger.direction == 'left':
                        if col == 0:
                            # Intentar pasar al vagón anterior si está en la primera columna
                            if wagon_number > 0:
                                prev_wagon = self.wagons[wagon_number - 1]
                                self.move_passenger_to_previous_wagon(wagon, passenger, row, col, prev_wagon)
                                moved_passengers.append(passenger)
                        else:
                            # Intentar mover en diagonal arriba a la izquierda, a la izquierda o abajo a la izquierda
                            self.move_passenger_left_if_no_wagon(wagon, passenger, row, col)

            wagon.update_color_matrix()