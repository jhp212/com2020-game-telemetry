from datetime import datetime, timedelta
import random

from database.main import SessionLocal, Telemetry, Parameters, DecisionLog

def seed():
    db = SessionLocal()

    try:
        params = [
            ("enemy_damage", 12.5),
            ("enemy_health", 100.0),
            ("player_speed", 6.2),
            ("spawn_rate", 1.4),
        ]
        
        # deleting child tables first to avoid errors during seeding
        db.query(DecisionLog).delete()
        db.query(Telemetry).delete()
        db.query(Parameters).delete()
        db.commit()


        for name, value in params:
            existing = db.query(Parameters).filter(Parameters.name == name).first()
            if existing:
                existing.value = value
            else:
                db.add(Parameters(name=name, value=value))

        # Seed telemetry rows
        base_time = datetime.now() - timedelta(minutes=60)

        allowed_types = ["stage_start", "stage_end", "enemy_defeated", "damage_taken", "tower_spawn","tower_upgrade","money_spent"] 

        
        
        for i in range(300):
            t = Telemetry(
                user_id=random.randint(1, 10000),
                stage_id=random.randint(1, 3),
                telemetry_type=random.choice(allowed_types),
                dateTime=base_time + timedelta(seconds=i * 10),
                data={
                    "stage_start": random.randint(1,200),
                    "stage_end": random.randint(1,200),
                    "enemy_defeated": random.randint(1,200),
                    "damage_taken": random.randint(1,200),
                    "tower_spawn": random.randint(1,200),
                    "tower_upgrade": random.randint(1,20),
                    "money_spent": random.randint(1,10000)
                },
            )
            db.add(t)
            
        for i in range(100):
            d = DecisionLog(
                id=random.randint(1, 10000),
                parameter_name = random.choice(["enemy_damage","enemy_health","player_speed","spawn_rate"]),
                stage_id=random.randint(1, 3),
                change= "TESTING CHANGE MADE",
                rationale = "TESTING RATIONALE",
                evidence = "TESTING EVIDENCE",
                dateTime=base_time + timedelta(seconds=i * 10),
            )
            db.add(d)

        db.commit()

    finally:
        db.close()

if __name__ == "__main__":
    seed()
