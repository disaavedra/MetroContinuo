import csv
import collections
import matplotlib.pyplot as plt

def plot_fail_passenger_distribution(csv_filename):
    distribution = collections.Counter()

    # Leer el archivo CSV
    with open(csv_filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            estaciones = row["Estaciones desplazadas"]
            if estaciones != "" and estaciones is not None:
                try:
                    estaciones_int = int(estaciones)
                    distribution[estaciones_int] += 1
                except ValueError:
                    # Si la conversión falla, se omite la fila
                    continue

    # Mostrar la distribución por consola
    print("Distribución de pasajeros fallidos por estaciones desplazadas:")
    for diff, count in sorted(distribution.items()):
        print(f"Estaciones desplazadas: {diff}, Pasajeros fallidos: {count}")

    # Crear un gráfico de barras para visualizar la distribución
    plt.figure(figsize=(8, 6))
    plt.bar(distribution.keys(), distribution.values(), color='salmon', edgecolor='black')
    plt.xlabel("Estaciones desplazadas")
    plt.ylabel("Número de pasajeros fallidos")
    plt.title("Distribución de pasajeros fallidos por estaciones desplazadas")
    plt.xticks(list(distribution.keys()))
    plt.show()

# Ejemplo de uso:
csv_filename = "fail_passenger_report.csv"
plot_fail_passenger_distribution(csv_filename)
