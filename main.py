from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel
from typing import List
from datetime import date
import sqlite3

app = FastAPI()

def init_db():
    conn = sqlite3.connect("tarefas.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            descricao TEXT,
            prioridade INTEGER,
            data TEXT,
            hora TEXT,
            concluida INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

init_db()

class TarefaCreate(BaseModel):
    titulo: str
    descricao: str = ""
    prioridade: int
    data: str
    hora: str

@app.post("/tarefas")
def criar_tarefa(tarefa: TarefaCreate):
    conn = sqlite3.connect("tarefas.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tarefas (titulo, descricao, prioridade, data, hora)
        VALUES (?, ?, ?, ?, ?)
    """, (tarefa.titulo, tarefa.descricao, tarefa.prioridade, tarefa.data, tarefa.hora))
    conn.commit()
    id = cursor.lastrowid
    conn.close()
    return {"id": f"tarefa_{id}", "status": "criada"}

@app.get("/tarefas/hoje")
def listar_tarefas_hoje():
    hoje = date.today().isoformat()
    conn = sqlite3.connect("tarefas.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, titulo, descricao, prioridade, data, hora, concluida FROM tarefas WHERE data=?
    """, (hoje,))
    tarefas = cursor.fetchall()
    conn.close()
    return {
        "data": [
            {
                "id": f"tarefa_{t[0]}",
                "titulo": t[1],
                "descricao": t[2],
                "prioridade": t[3],
                "data": t[4],
                "hora": t[5],
                "concluida": bool(t[6])
            } for t in tarefas
        ]
    }

@app.post("/tarefas/{id}/concluir")
def concluir_tarefa(id: str = Path(..., example="tarefa_1")):
    try:
        tarefa_id = int(id.replace("tarefa_", ""))
    except:
        raise HTTPException(status_code=400, detail="ID inválido")
    conn = sqlite3.connect("tarefas.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE tarefas SET concluida=1 WHERE id=?", (tarefa_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    conn.commit()
    conn.close()
    return {"id": id, "status": "concluida"}
