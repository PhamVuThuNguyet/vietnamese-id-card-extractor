from datetime import datetime

from sources.Models.database import SessionLocal
from sources.Models.models import Client


def add_record_to_db(detected_fields, face_id):
    client = Client()
    client.id = detected_fields[0]
    client.image = face_id
    client.name = detected_fields[1]
    client.dob = datetime.strptime(detected_fields[2], "%d/%m/%Y")
    client.sex = 1 if detected_fields[3] == "Nữ" else 0
    client.nationality = detected_fields[4]
    client.poo = detected_fields[5]
    client.por = detected_fields[6]
    client.doe = datetime.strptime(detected_fields[7], "%d/%m/%Y")

    db = SessionLocal()
    db.add(client)
    db.commit()

    db.close()
