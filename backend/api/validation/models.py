from pydantic import BaseModel, Field, field_validator, model_validator


class RulesAutoResponse(BaseModel):
    budget_from: int = Field(name="budget_from")
    budget_to: int = Field(name="budget_to")
    deadline_days: int = Field(name="deadline_days")
    qty_freelancers: int = Field(name="qty_freelancers")

    @model_validator(mode="before")
    @classmethod
    def budget_validate(cls, values: dict) -> dict:
        if values["budget_from"] < 0 or values["budget_to"] < 0:
            raise ValueError("The budget cannot be a negative number")
        if values["budget_to"] < values["budget_from"]:
            raise ValueError("The value of budget_to must be greater than budget_from")
        return values
    
    @field_validator("deadline_days", mode="before")
    @classmethod
    def deadline_validate(cls, value: int) -> int:
        if value < 0:
            raise ValueError("The number days of deadline cannot be a negative")
        return value
    
    @field_validator("qty_freelancers")
    @classmethod
    def freelancers_validate(cls, value: int) -> int:
        if value < 0:
            raise ValueError("The number of freelancers cannot be a negative")
        return value


class HardTaskCreate(BaseModel):
    title: str = Field(name="title")
    description: str = Field(name="description")
    tags: list = Field(name="tags")
    budget_from: int = Field(name="budget_from")
    budget_to: int = Field(name="budget_to")
    deadline_days: int = Field(name="deadline_days")
    number_of_reminders: int = Field(name="number_of_reminders")
    private_content: str | None = Field(name="private_content", max_length=5000)
    is_hard: bool = Field(name="is_hard", default=True)
    all_auto_responses: bool = Field(name="all_auto_responses")
    rules: dict | None = Field(name="rules")


    @model_validator(mode="before")
    @classmethod
    def budget_validate(cls, values: dict) -> dict:
        if values["budget_from"] < 0 or values["budget_to"] < 0:
            raise ValueError("The budget cannot be a negative number")
        if values["budget_to"] < values["budget_from"]:
            raise ValueError("The value of budget_to must be greater than budget_from")
        return values
    
    @model_validator(mode="before")
    @classmethod
    def autoresponse_validate(cls, values: dict) -> dict:
        if values["all_auto_responses"] and values["rules"]:
            raise ValueError("If autoresponse is enabled for everyone, you cannot transmit the rules.")
        return values

    @model_validator(mode="before")
    @classmethod
    def rules_validate(cls, value: dict) -> dict:
        if value.get("rules"):
            rules = RulesAutoResponse(**value["rules"])
        return value
    
    @field_validator("tags", mode="before")
    @classmethod
    def tags_conversion(cls, value: str) -> list:
        tags = value.split(",")
        return tags
    
    @field_validator("number_of_reminders", mode="before")
    @classmethod
    def reminds_validate(cls, value: int) -> int:
        if value < 0:
            raise ValueError("The number of reminds cannot be a negative")
        return value
    
    @field_validator("deadline_days", mode="before")
    @classmethod
    def deadline_validate(cls, value: int) -> int:
        if value < 0:
            raise ValueError("The number days of deadline cannot be a negative")
        return value
    