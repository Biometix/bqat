from pydantic import BaseModel, validator


class RuntimeConfiguration(BaseModel):
    shm: str = "8G"
    cpus: int | None = None
    memory: str | None = None
    pull: bool | None = None
    volume: str = "data"
    image: str
    entrypoint: str

    @validator("shm")
    def shm_must_follow_by_unit(cls, v):
        assert v.endswith("G")
        return v

    @validator("memory")
    def memory_must_follow_by_unit(cls, v):
        assert v.endswith("G")
        return v


class JobConfiguration(BaseModel):
    mode: str
    input: str = "data"
    filename: str | None = None
    attributes: str | None = None
    query: str | None = None

    @validator("query")
    def query_must_not_contain_space(cls, v):
        if " " in v:
            raise ValueError("must not contain a space")
        return v.title()

    @validator("attributes")
    def attributes_must_separated_by_comma(cls, v):
        if "," not in v:
            raise ValueError("must separated by comma")
        return v.title()
