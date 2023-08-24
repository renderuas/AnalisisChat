# python script.py Chat.txt report.pdf
import re
from collections import defaultdict
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import sys
from matplotlib.backends.backend_pdf import PdfPages


def analyze_chat(file_path):
    # variables
    participants = set()
    messages_per_participant = defaultdict(int)
    active_hours_per_participant = defaultdict(lambda: defaultdict(int))
    monthly_activity_per_participant_and_year = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    total_messages = 0
    days_activity = defaultdict(int)

    # Lectira
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            match = re.match(r'(\d+/\d+/\d+), (\d+:\d+) - (.*?):', line)
            if match:
                date_str, time_str, participant = match.groups()
                date_obj = datetime.strptime(date_str + " " + time_str, '%d/%m/%y %H:%M')

                #Calculos
                participants.add(participant)

                messages_per_participant[participant] += 1
                total_messages += 1

                active_hours_per_participant[participant][date_obj.hour] += 1

                monthly_activity_per_participant_and_year[participant][date_obj.year][date_obj.month - 1] += 1
                
                days_activity[date_str] += 1

    return messages_per_participant, active_hours_per_participant, monthly_activity_per_participant_and_year

def create_report(file_path, output_pdf):
    messages_per_participant, active_hours_per_participant, monthly_activity_per_participant_and_year = analyze_chat(file_path)

    # Cremos el writer de pdf
    pdf_writer = PdfPages(output_pdf)

    # funcion para salvar a pdf
    def save_plot_to_pdf():
        pdf_writer.savefig(bbox_inches='tight')

    # Mensajes por paritip
    names, message_counts = zip(*sorted(messages_per_participant.items(), key=lambda x: x[1], reverse=True))
    plt.bar(names, message_counts)
    plt.xticks(rotation=90)
    plt.xlabel('Participante')
    plt.ylabel('Numero total de mensajes')
    plt.title('Mensajes por participante')
    save_plot_to_pdf()
    plt.close()

    # Comparacion por horas
    sorted_participants = sorted(messages_per_participant.items(), key=lambda x: x[1], reverse=True)
    colors = plt.cm.tab20.colors
    for idx, (participant, _) in enumerate(sorted_participants):
        activity_per_hour = [active_hours_per_participant[participant].get(h, 0) for h in range(24)]
        plt.plot(list(range(24)), activity_per_hour, label=participant, color=colors[idx % 20])
    plt.xlabel('Hora del dia')
    plt.ylabel('Numero de mensajes')
    plt.title('Comparacion de horas activas en todos los participantes')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    save_plot_to_pdf()
    plt.close()

    #Comparacion de rtiempo
    all_years = sorted(set(year for participant in monthly_activity_per_participant_and_year.values() for year in participant.keys()))
    months_with_years = [f"{month} {year}" for year in all_years for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]]
    for idx, (participant, _) in enumerate(sorted_participants):
        activity_per_year = [monthly_activity_per_participant_and_year[participant][year].get(m, 0) for year in all_years for m in range(12)]
        plt.plot(months_with_years, activity_per_year, label=participant, color=colors[idx % 20])
    plt.xlabel('Año y mes')
    plt.ylabel('Numero de mensajes')
    plt.title('Comparacion a lo largo de los meses')
    plt.xticks(rotation=45)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    save_plot_to_pdf()
    plt.close()

    # Cerramos pdf
    pdf_writer.close()

if __name__ == "__main__":
    file_path = sys.argv[1]
    output_pdf = sys.argv[2]
    create_report(file_path, output_pdf)

