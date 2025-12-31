from database import SessionLocal , engine
import models

models.Base.metadata.create_all(bind=engine)


db = SessionLocal()

def seed():
    #seed some initial data
    apps = [
        models.Application(user_id=1, job_id=10, status="Applied"),
        models.Application(user_id=1, job_id=11, status="Viewed"),
        models.Application(user_id=2, job_id=10, status="Accepted")
    ]
    db.add_all(apps)
    db.commit()
    print("Seed data added!")

if __name__ == "__main__":
    seed()