import csv
import matplotlib.pyplot as plt

def plot_avg_travel_time_by_stations(csv_filename):
    """
    Lee el archivo CSV de pasajeros (con encabezados: Tiempo de viaje, Metros desplazados, Estaciones desplazadas)
    y crea un gráfico que muestra, para cada cantidad de estaciones desplazadas, el tiempo de viaje promedio de los pasajeros.
    """
    # Diccionario para acumular suma de tiempos y conteo por cada valor de "Estaciones desplazadas"
    group_data = {}

    with open(csv_filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            estaciones_str = row.get("Estaciones desplazadas", "")
            travel_time_str = row.get("Tiempo de viaje", "")
            if estaciones_str == "" or travel_time_str == "":
                continue
            try:
                estaciones = int(estaciones_str)
                travel_time = float(travel_time_str)
            except ValueError:
                continue

            if estaciones in group_data:
                group_data[estaciones]["sum"] += travel_time
                group_data[estaciones]["count"] += 1
            else:
                group_data[estaciones] = {"sum": travel_time, "count": 1}

    # Calcular el promedio de tiempo de viaje para cada grupo
    avg_data = {k: v["sum"] / v["count"] for k, v in group_data.items()}

    # Preparar datos para el gráfico: ordenar por la cantidad de estaciones desplazadas
    x_values = sorted(avg_data.keys())
    y_values = [avg_data[x] for x in x_values]

    # Graficar
    plt.figure(figsize=(8, 6))
    plt.bar(x_values, y_values, color='orchid', edgecolor='black')
    plt.xlabel("Estaciones desplazadas")
    plt.ylabel("Tiempo de viaje promedio (segundos)")
    plt.title("Tiempo promedio de viaje por estaciones desplazadas")
    plt.xticks(x_values)
    plt.show()

# Ejemplo de uso:
csv_filename = "passenger_report.csv"
plot_avg_travel_time_by_stations(csv_filename)
