from app.models import SystemMessagePDF
from sqlalchemy.orm import Session


def get_latest_system_message(username,db: Session):
    latest_message = db.query(SystemMessagePDF).filter(
        SystemMessagePDF.username == username
    ).order_by(
        SystemMessagePDF.timestamp.desc()
    ).first()

    return latest_message


