from pydantic import BaseModel, Field

class ClientProfile(BaseModel):
    client_id: int = Field(description="Уникальный ID клиента")
    name: str = Field(description="ФИО клиента")
    status: str = Field(description="Статус: new, active, blocked")
    balance: float = Field(description="Текущий баланс")

class BotResponse(BaseModel):
    message_to_client: str = Field(description="Текст, который будет отправлен клиенту в Telegram")
    action_log: str = Field(description="Краткое описание действия для логирования в CRM")
