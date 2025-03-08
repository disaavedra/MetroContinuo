import csv
import matplotlib.pyplot as plt

def plot_passenger_move_distribution(csv_filename):
    move_counts = []

    # Leer el archivo CSV
    with open(csv_filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            move_val = row["Metros desplazados"]
            if move_val != "" and move_val is not None:
                try:
                    move_counts.append(float(move_val))
                except ValueError:
                    continue

    # Crear el histograma
    plt.figure(figsize=(8, 6))
    plt.hist(move_counts, bins=20, edgecolor='black', color='skyblue')
    plt.xlabel("Metros desplazados")
    plt.ylabel("Número de pasajeros")
    plt.title("Distribución de metros recorridos por pasajeros")
    plt.show()

# Ejemplo de uso:
csv_filename = "passenger_report.csv"
plot_passenger_move_distribution(csv_filename)
