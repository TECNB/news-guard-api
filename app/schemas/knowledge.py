from pydantic import BaseModel

class parseDocumentsRequest(BaseModel):
    datasetsId: str
    documentId: str

class CreateKnowledgeRequest(BaseModel):
    datasetsName: str

class DeleteKnowledgeRequest(BaseModel):
    datasetsId: str