
from fastapi import FastAPI, HTTPException, Depends
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from schemas import CompareRequest, UserCreate, UserLogin, Token
from database import get_db, engine, Base
from models import History, User
from auth import hash_password, verify_password, create_access_token, get_current_user

load_dotenv()

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))



@app.post("/user/create")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(
        User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Usuário já existe"
        )

    hashed_password = hash_password(user.password)

    db_user = User(
        username=user.username,
        hashed_password=hashed_password
    )

    # Salvar no banco
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {
        "id": db_user.id,
        "username": db_user.username,
        "created_at": db_user.created_at,
        "message": "Usuário criado com sucesso"
    }


@app.get("/users")
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return {
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "created_at": user.created_at
            }
            for user in users
        ]
    }


@app.post("/user/login", response_model=Token)
async def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": db_user.username})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.post("/compare")
def compare_products(req: CompareRequest, current_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    # Obter o usuário atual do banco de dados
    current_user = db.query(User).filter(
        User.username == current_username).first()
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Usuário não encontrado"
        )

    product1 = req.product1.strip()
    product2 = req.product2.strip()

    if not product1 or not product2:
        raise HTTPException(
            status_code=400, detail="Both product names must be provided.")

    prompt = f"""
    Você é um assistente especialista em comparação de produtos.
    Compare os dois produtos abaixo e **retorne APENAS um JSON válido** no formato:

    {{
      "resumo": "string",
      "pros_produto1": ["item1", "item2", "item3"],
      "pros_produto2": ["item1", "item2", "item3"],
      "contras_produto1": ["item1", "item2", "item3"],
      "contras_produto2": ["item1", "item2", "item3"],
      "conclusao": "string",
      "links_recomendados": {{
        "produto1": ["https://loja1.com/produto1", "https://loja2.com/produto1"],
        "produto2": ["https://loja1.com/produto2", "https://loja2.com/produto2"]
      }}
    }}

    Regras:
    - Se os produtos forem de categorias diferentes, retorne um JSON com o campo resumo informando que não é possível comparar diretamente.
    - Caso contrário:
        - "resumo": faça um resumo do custo-benefício de ambos.
        - "pros_produto1": array com os pontos positivos do produto 1 (cada item como string separada).
        - "pros_produto2": array com os pontos positivos do produto 2 (cada item como string separada).
        - "contras_produto1": array com os pontos negativos do produto 1 (cada item como string separada).
        - "contras_produto2": array com os pontos negativos do produto 2 (cada item como string separada).
        - "conclusao": diga qual é o mais vantajoso e por quê.
        - "links_recomendados": objeto com arrays de links de lojas onde é possível comprar cada produto ("produto1" e "produto2").

    Produto 1: {product1}
    Produto 2: {product2}

    IMPORTANTE: Responda **somente** com JSON válido. Não inclua explicações nem texto adicional fora do JSON.
    """

    try:
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        response = model.generate_content(prompt)


        text = response.text.strip()
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
        
            text = text.replace("```json", "").replace("```", "").strip()
            data = json.loads(text)

        db_history = History(
            user_id=current_user.id,
            product1=product1,
            product2=product2,
            comparison_result=data
        )
        db.add(db_history)
        db.commit()
        db.refresh(db_history)

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history")
def get_comparison_history(current_username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    # Obter o usuário atual do banco de dados
    current_user = db.query(User).filter(
        User.username == current_username).first()
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Usuário não encontrado"
        )

    history = db.query(History).filter(
        History.user_id == current_user.id).all()
    return history


@app.get("/all_history")
def get_all_comparison_history(db: Session = Depends(get_db)):
    history = db.query(History).all()
    return history
