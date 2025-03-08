import random
from Simulator import Simulator
from Station import Station

# =============================================================================
# CONFIGURACIÓN DE LA SIMULACIÓN
# =============================================================================

# Parámetros generales
number_of_trains = 5
number_of_wagons = 5
speed_km_h = 60
speed_m_s = speed_km_h * 1000 / 3600
simulator_time = 10800  # Tiempo total de simulación en segundos
acceleration = 1
deceleration = 1
interval = 1  # Factor para acelerar el tiempo de la animación

# Parámetros de unidades y estaciones
wagon_length_m = 14
wagon_width_m = 5
station_capacity = 500
passenger_per_meter = 5

# =============================================================================
# MATRICES DE FLUJOS DE PASAJEROS
# =============================================================================

# Matriz real de flujos de pasajeros (filas: estación de origen, columnas: estación de destino)
passenger_flows = [
    [0,   106, 28, 84, 76, 81, 185, 81, 68, 51],
    [40,  0,   22, 20, 26, 38, 68,  24, 25, 32],
    [19,  51,  0,  11, 21, 18, 33,  22, 23, 37],
    [139, 152, 44, 0,  16, 34, 55,  44, 27, 40],
    [64,  67,  18, 4,  0,  16, 26,  14, 11, 20],
    [162, 180, 29, 29, 22, 0, 38,  63, 54, 102],
    [132, 169, 48, 24, 27, 42, 0,   12, 21, 30],
    [179, 191, 72, 47, 58, 91, 24,  0,  34, 73],
    [199, 238, 61, 45, 75, 63, 53,  35, 0,  45],
    [193, 172, 106,99, 68, 168,115, 139, 58, 0],
]

# =============================================================================
# DEFINICIÓN DE ESTACIONES
# =============================================================================

# Estaciones reales para la línea L6:
real_stations = [
    Station(name='Cerrillos', position=1670, wagon_length_m=wagon_length_m, wagon_width_m=wagon_width_m,
            station_capacity=station_capacity, passenger_flows=passenger_flows[0],
            passenger_per_meter=passenger_per_meter),
    Station(name='Lo Valledor', position=3340, wagon_length_m=wagon_length_m, wagon_width_m=wagon_width_m,
            station_capacity=station_capacity, passenger_flows=passenger_flows[1],
            passenger_per_meter=passenger_per_meter),
    Station(name='Pedro Aguirre Cerda', position=5010, wagon_length_m=wagon_length_m, wagon_width_m=wagon_width_m,
            station_capacity=station_capacity, passenger_flows=passenger_flows[2],
            passenger_per_meter=passenger_per_meter),
    Station(name='Franklin L6', position=6680, wagon_length_m=wagon_length_m, wagon_width_m=wagon_width_m,
            station_capacity=station_capacity, passenger_flows=passenger_flows[3],
            passenger_per_meter=passenger_per_meter),
    Station(name='Bio Bio', position=8350, wagon_length_m=wagon_length_m, wagon_width_m=wagon_width_m,
            station_capacity=station_capacity, passenger_flows=passenger_flows[4],
            passenger_per_meter=passenger_per_meter),
    Station(name='Nuble L6', position=10020, wagon_length_m=wagon_length_m, wagon_width_m=wagon_width_m,
            station_capacity=station_capacity, passenger_flows=passenger_flows[5],
            passenger_per_meter=passenger_per_meter),
    Station(name='Estadio Nacional', position=11690, wagon_length_m=wagon_length_m, wagon_width_m=wagon_width_m,
            station_capacity=station_capacity, passenger_flows=passenger_flows[6],
            passenger_per_meter=passenger_per_meter),
    Station(name='Nunoa L6', position=13360, wagon_length_m=wagon_length_m, wagon_width_m=wagon_width_m,
            station_capacity=station_capacity, passenger_flows=passenger_flows[7],
            passenger_per_meter=passenger_per_meter),
    Station(name='Ines de Suarez', position=15030, wagon_length_m=wagon_length_m, wagon_width_m=wagon_width_m,
            station_capacity=station_capacity, passenger_flows=passenger_flows[8],
            passenger_per_meter=passenger_per_meter),
    Station(name='Los Leones L6', position=16700, wagon_length_m=wagon_length_m, wagon_width_m=wagon_width_m,
            station_capacity=station_capacity, passenger_flows=passenger_flows[9],
            passenger_per_meter=passenger_per_meter),
]

# Función auxiliar para crear estaciones con flujos aleatorios (opcional)
def create_stations(stations_number, wagon_length_m, wagon_width_m, station_capacity):
    stations = []
    for s in range(1, stations_number + 1):
        flows = [random.randint(1000, 2000) if i != s - 1 else 0 for i in range(stations_number)]
        station = Station(name=f"Station {s}", position=s * 2000, wagon_length_m=wagon_length_m,
                          wagon_width_m=wagon_width_m, station_capacity=station_capacity,
                          passenger_flows=flows, passenger_per_meter=passenger_per_meter)
        stations.append(station)
    return stations

# Seleccionar el conjunto de estaciones a utilizar:
stations = create_stations(7, wagon_length_m, wagon_width_m, station_capacity)
# stations = real_stations  # Usamos las estaciones reales con nombres de la línea L6

# Calcular el límite de posición (para definir el final del trayecto)
position_limit = max(station.position for station in stations) + 200

# Calcular el momento de la creacion de pasajeros para no sobrecargar al primer tren.
position = max(station.position for station in stations)
passenger_creation_time = position / speed_m_s
simulator_time_with_passenger_creation_time = int(simulator_time + passenger_creation_time)

# =============================================================================
# CREACIÓN Y EJECUCIÓN DEL SIMULADOR
# =============================================================================

simulator = Simulator(
    speed_m_s,
    number_of_trains,
    number_of_wagons,
    wagon_length_m,
    wagon_width_m,
    simulator_time_with_passenger_creation_time,
    stations,
    acceleration,
    deceleration,
    position_limit,
    interval,
    passenger_per_meter,
    passenger_creation_time
)

# Descomenta la función que desees ejecutar:

# Para ejecutar la simulación con animación:
simulator.run_simulation()

# Para visualizar únicamente la animación de trenes:
#simulator.animate_train_simulation()

# Para ejecutar la simulación lógica sin animación:
#simulator.execute_simulation_logic()

